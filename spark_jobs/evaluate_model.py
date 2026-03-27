import os
import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from graph_engine import calculate_pagerank, generate_recommendations

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("evaluate_model")

def evaluate_predictions(predictions, ground_truth, k=10):
    """
    Evaluates Precision@K and Recall.
    predictions: DataFrame[user_id, recommended_user_id, recommendation_score]
    ground_truth: DataFrame[user_a (src), user_b (dst)]
    """
    # 1. Get Top K predictions per user
    window = Window.partitionBy("user_id").orderBy(F.col("recommendation_score").desc())
    top_k = predictions.withColumn("rank", F.rank().over(window)).filter(F.col("rank") <= k)
    
    # 2. Extract actual test edges for each user
    actuals = ground_truth.groupBy(F.col("user_a").alias("user_id")) \
        .agg(F.collect_set(F.col("user_b")).alias("actual_connections"))
        
    # 3. Extract predicted edges for each user
    preds = top_k.groupBy("user_id") \
        .agg(F.collect_list("recommended_user_id").alias("predicted_connections"))
        
    # 4. Join and compute metrics per user
    joined = actuals.join(preds, "user_id", "left_outer")
    
    # UDF to compute intersection size, precision, and recall
    def compute_metrics(actual_list, pred_list):
        if not actual_list:
            return (0.0, 0.0)
        actual_set = set(actual_list)
        pred_set = set(pred_list) if pred_list else set()
        
        hits = len(actual_set.intersection(pred_set))
        precision_at_k = hits / float(k) if k > 0 else 0.0
        recall = hits / float(len(actual_set))
        return (float(precision_at_k), float(recall))
        
    metrics_schema = "struct<precision:double, recall:double>"
    metrics_udf = F.udf(compute_metrics, metrics_schema)
    
    eval_df = joined.withColumn("metrics", metrics_udf(F.col("actual_connections"), F.col("predicted_connections"))) \
        .select("user_id", "metrics.precision", "metrics.recall")
        
    # 5. Average metrics over all users
    final_metrics = eval_df.agg(
        F.mean("precision").alias("mean_precision_at_k"),
        F.mean("recall").alias("mean_recall")
    ).collect()[0]
    
    return {
        "precision_at_k": final_metrics["mean_precision_at_k"] or 0.0,
        "recall": final_metrics["mean_recall"] or 0.0,
        "k": k
    }

def main():
    spark = SparkSession.builder \
        .appName("GraphRank Engine - Evaluation") \
        .config("spark.sql.shuffle.partitions", "10") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("ERROR")
    
    logger.info("Loading graph connections for Evaluation...")
    df_connections = spark.read.csv("data/connections.csv", header=True, inferSchema=True)
    df_user_metrics = spark.read.parquet("processed/user_metrics")
    
    logger.info("Splitting data into 80% train and 20% test...")
    splits = df_connections.randomSplit([0.8, 0.2], seed=42)
    train_edges = splits[0].cache()
    test_edges = splits[1].cache()
    
    logger.info(f"Train edges: {train_edges.count()}, Test edges: {test_edges.count()}")
    
    # Compute PageRank on Train Set
    logger.info("Computing PageRank scores purely on Training Data...")
    pagerank_scores = calculate_pagerank(spark, train_edges, max_iter=5)
    
    # Generate Recommendations on Train Set
    logger.info("Generating Recommendations purely on Training Data...")
    recommendations = generate_recommendations(spark, train_edges, pagerank_scores, df_user_metrics)
    
    # Evaluate Predictions against Test Set
    logger.info("Evaluating predictions against unseen test edges...")
    metrics = evaluate_predictions(recommendations, test_edges, k=10)
    
    logger.info(f"Evaluation Results:")
    logger.info(f"  Precision@{metrics['k']}: {metrics['precision_at_k']:.4f}")
    logger.info(f"  Recall: {metrics['recall']:.4f}")
    
    # 1. Read weights to log them
    import datetime
    try:
        with open("config/ranking_weights.json", "r") as f:
            weights = json.load(f)
    except Exception:
        weights = {"w_mutual": 0.5, "w_influence": 0.3, "w_activity": 0.1, "w_recency": 0.1}
        
    metrics["timestamp"] = datetime.datetime.now().isoformat()
    metrics["weights"] = weights

    # Save to JSON
    output_dir = "processed"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "evaluation_metrics.json")
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=4)
        
    history_file = os.path.join(output_dir, "evaluation_history.jsonl")
    with open(history_file, "a") as f:
        f.write(json.dumps(metrics) + "\n")
        
    logger.info(f"Evaluation complete. Metrics saved to {output_file} and appended to {history_file}")
    spark.stop()

if __name__ == "__main__":
    main()
