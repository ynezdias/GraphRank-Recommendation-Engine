import os
import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from graph_engine import calculate_pagerank, generate_recommendations, load_ranking_weights

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
    preds = top_k.groupBy("user_id", "experiment_variant") \
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
        .select("user_id", "experiment_variant", "metrics.precision", "metrics.recall")
        
    # 5. Average metrics over all users per variant
    final_metrics = eval_df.groupBy("experiment_variant").agg(
        F.mean("precision").alias("mean_precision_at_k"),
        F.mean("recall").alias("mean_recall")
    ).collect()
    
    results = {"k": k, "variants": {}}
    for row in final_metrics:
        variant = row["experiment_variant"]
        if variant:
            results["variants"][variant] = {
                "precision_at_k": row["mean_precision_at_k"] or 0.0,
                "recall": row["mean_recall"] or 0.0
            }
            
    return results

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
    
    logger.info(f"Evaluation Results for Top-{metrics['k']}:")
    for variant, var_metrics in metrics.get("variants", {}).items():
        logger.info(f"  Variant [{variant}] -> Precision: {var_metrics['precision_at_k']:.4f} | Recall: {var_metrics['recall']:.4f}")
    
    # 1. Read weights to log them
    import datetime
    control_weights, treatment_weights = load_ranking_weights()
        
    metrics["timestamp"] = datetime.datetime.now().isoformat()
    metrics["weights"] = {
        "control": control_weights,
        "treatment": treatment_weights
    }

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
