from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("graph_engine")

def calculate_pagerank(spark, connections, max_iter=10, damping_factor=0.85):
    """
    Computes PageRank natively using PySpark DataFrames.
    """
    logger.info("Initializing PageRank calculation...")
    
    # 1. Identify all unique nodes
    nodes = connections.select(F.col("user_a").alias("id")) \
        .union(connections.select(F.col("user_b").alias("id"))) \
        .distinct()
    
    nodes.cache() # Cache for reuse in iterative loop
    
    num_nodes = nodes.count()
    if num_nodes == 0:
        return spark.createDataFrame([], schema="id: string, pagerank: double")
    
    logger.info(f"Total graph nodes: {num_nodes}")

    # 2. Compute out-degree for each node
    out_degrees = connections.groupBy("user_a") \
        .count() \
        .withColumnRenamed("user_a", "id") \
        .withColumnRenamed("count", "degree")

    # 3. Initialize ranks (1.0 / num_nodes)
    initial_rank = 1.0 / num_nodes
    ranks = nodes.withColumn("rank", F.lit(initial_rank))
    
    # 4. Prepare the adjacency list with contribution weights
    links = connections.join(out_degrees, connections.user_a == out_degrees.id) \
        .select(
            F.col("user_a").alias("src"), 
            F.col("user_b").alias("dst"), 
            (F.lit(1.0) / F.col("degree")).alias("weight")
        )
    links.cache() # Cache links as they are heavily reused

    # 5. Iteratively calculate PageRank
    for i in range(max_iter):
        logger.info(f"  PageRank Iteration {i+1}/{max_iter}...")
        
        # Calculate contributions from sources to destinations
        contributions = links.join(ranks, links.src == ranks.id) \
            .withColumn("contribution", F.col("rank") * F.col("weight")) \
            .groupBy("dst") \
            .agg(F.sum("contribution").alias("sum_contrib"))
        
        # Update ranks: (1 - d)/N + d * sum(contributions)
        base_rank = (1.0 - damping_factor) / num_nodes
        ranks = nodes.join(contributions, nodes.id == contributions.dst, "left_outer") \
            .fillna({"sum_contrib": 0.0}) \
            .withColumn("rank", F.lit(base_rank) + (F.lit(damping_factor) * F.col("sum_contrib"))) \
            .select("id", "rank")
            
        # Truncate lineage to prevent OutOfMemory/StackOverflow on many iterations
        ranks.cache()
        # Force materialization
        ranks.count()

    # Rename output columns for consistency
    return ranks.withColumnRenamed("id", "user_id").withColumnRenamed("rank", "pagerank")


def load_ranking_weights():
    control_weights = {
        "w_mutual": 0.5,
        "w_influence": 0.3,
        "w_activity": 0.1,
        "w_recency": 0.1
    }
    treatment_weights = {
        "w_mutual": 0.5,
        "w_influence": 0.3,
        "w_activity": 0.1,
        "w_recency": 0.1
    }
    try:
        with open("config/ranking_weights.json", "r") as f:
            weights = json.load(f)
            control_weights.update(weights)
    except Exception:
        pass
        
    try:
        with open("config/experiment_weights.json", "r") as f:
            e_weights = json.load(f)
            treatment_weights.update(e_weights)
    except Exception:
        pass
        
    return control_weights, treatment_weights

def generate_recommendations(spark, connections, pagerank_scores, user_metrics, weights=None, limit=10):
    """
    Recommends users based on mutual connections (triadic closure)
    and weights them by PageRank influence, activity, and recency.
    Assigns users to A/B testing variants (Control/Treatment).
    """
    if weights is None:
        control_weights, treatment_weights = load_ranking_weights()
    elif isinstance(weights, dict):
        control_weights = weights
        treatment_weights = weights # If explicitly provided, use the same for both variants
    else:
        control_weights, treatment_weights = weights
        
    logger.info(f"Generating recommendations with Control: {control_weights} | Treatment: {treatment_weights}")
    
    # connections is currently user_a -> user_b
    # Let's ensure we consider links mostly bidirectional or at least find mutuals
    
    # Step 1: Find paths of length 2 (A -> B -> C)
    # A is connected to B, B is connected to C. Therefore A might know C.
    
    # Rename columns for joining
    edges1 = connections.select(F.col("user_a").alias("src"), F.col("user_b").alias("mid"))
    edges2 = connections.select(F.col("user_a").alias("mid"), F.col("user_b").alias("dst"))
    
    # Join to find A -> B -> C paths
    paths = edges1.join(edges2, "mid")
    
    # Step 2: Filter out existing direct connections and self-loops
    # We don't want to recommend someone you are already connected to, or yourself.
    direct_edges = connections.select(
        F.col("user_a").alias("src"), 
        F.col("user_b").alias("dst")
    ).withColumn("is_direct", F.lit(True))
    
    potential_recs = paths.filter(F.col("src") != F.col("dst")) \
        .join(direct_edges, ["src", "dst"], "left_outer") \
        .filter(F.col("is_direct").isNull()) \
        .drop("is_direct")
        
    # Step 3: Count mutual connections (the "mid" nodes)
    mutual_counts = potential_recs.groupBy("src", "dst") \
        .count() \
        .withColumnRenamed("count", "mutual_friends")
        
    # Step 4: Add PageRank influence to rank the recommendations
    # We want to recommend influential people (dst's PageRank) if mutuals are tied
    
    # Calculate deterministic experiment variant for each user
    experiment_variant_expr = F.when(F.col("src") % 2 == 0, "control").otherwise("treatment")
    
    ranked_recs = mutual_counts.join(pagerank_scores, mutual_counts.dst == pagerank_scores.user_id) \
        .join(user_metrics, mutual_counts.dst == user_metrics.user_id, "left") \
        .fillna({"post_count": 0, "total_connections": 0, "recency_score": 0.0}) \
        .withColumn("experiment_variant", experiment_variant_expr)
        
    # Calculate separate scores for control and treatment and pick the right one
    control_score_expr = (
        (F.col("mutual_friends") * control_weights.get("w_mutual", 0.5)) + 
        (F.col("pagerank") * 100 * control_weights.get("w_influence", 0.3)) + 
        ((F.col("total_connections") + F.col("post_count")) * control_weights.get("w_activity", 0.1)) + 
        (F.col("recency_score") * control_weights.get("w_recency", 0.1))
    )
    
    treatment_score_expr = (
        (F.col("mutual_friends") * treatment_weights.get("w_mutual", 0.5)) + 
        (F.col("pagerank") * 100 * treatment_weights.get("w_influence", 0.3)) + 
        ((F.col("total_connections") + F.col("post_count")) * treatment_weights.get("w_activity", 0.1)) + 
        (F.col("recency_score") * treatment_weights.get("w_recency", 0.1))
    )

    ranked_recs = ranked_recs.withColumn(
        "recommendation_score", 
        F.when(F.col("experiment_variant") == "control", control_score_expr)
         .otherwise(treatment_score_expr)
    )
        
    # Step 5: Format output
    final_recs = ranked_recs.select(
        F.col("src").alias("user_id"),
        F.col("dst").alias("recommended_user_id"),
        "mutual_friends",
        "pagerank",
        "experiment_variant",
        "recommendation_score"
    )
    
    return final_recs


def main():
    spark = SparkSession.builder \
        .appName("GraphRank Engine - Influence & Recommendations") \
        .config("spark.sql.shuffle.partitions", "10") \
        .getOrCreate()
        
    # Set log level to minimize verbosity in logs
    spark.sparkContext.setLogLevel("ERROR")

    logger.info("Loading graph data...")
    df_connections = spark.read.csv("data/connections.csv", header=True, inferSchema=True)
    df_user_metrics = spark.read.parquet("processed/user_metrics")
    
    # 1. Compute PageRank
    pagerank_scores = calculate_pagerank(spark, df_connections, max_iter=5) # Reduced iter for test data speed
    
    logger.info("Writing PageRank results...")
    pr_output_path = "processed/pagerank_scores"
    pagerank_scores.write.parquet(pr_output_path, mode="overwrite")
    pagerank_scores.orderBy(F.col("pagerank").desc()).limit(100).write.csv(f"{pr_output_path}_sample", header=True, mode="overwrite")
    
    # 2. Compute Recommendations
    recommendations = generate_recommendations(spark, df_connections, pagerank_scores, df_user_metrics)
    
    logger.info("Writing Recommendation results...")
    rec_output_path = "processed/recommendations"
    recommendations.write.parquet(rec_output_path, mode="overwrite")
    
    # Save top recommendations overall to CSV sample
    recommendations.orderBy(F.col("recommendation_score").desc()).limit(100).write.csv(f"{rec_output_path}_sample", header=True, mode="overwrite")

    logger.info("Graph Engine job completed successfully.")
    spark.stop()

if __name__ == "__main__":
    main()
