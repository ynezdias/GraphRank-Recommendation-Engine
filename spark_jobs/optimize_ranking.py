import os
import json
import logging
import random
from pyspark.sql import SparkSession
from graph_engine import calculate_pagerank, generate_recommendations
from evaluate_model import evaluate_predictions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("optimize_ranking")

def generate_search_grid(num_samples=5):
    """
    Generates random weight combinations for Random Search.
    Variables: w_mutual, w_influence, w_activity, w_recency
    """
    grid = []
    # Always include the baseline default
    grid.append({
        "w_mutual": 0.5,
        "w_influence": 0.3,
        "w_activity": 0.1,
        "w_recency": 0.1
    })
    
    for _ in range(num_samples - 1):
        # Generate random weights roughly summing to ~1.0
        w1 = random.uniform(0.1, 0.8)
        w2 = random.uniform(0.1, 0.8)
        w3 = random.uniform(0.0, 0.5)
        w4 = random.uniform(0.0, 0.5)
        
        total = w1 + w2 + w3 + w4
        grid.append({
            "w_mutual": round(w1/total, 2),
            "w_influence": round(w2/total, 2),
            "w_activity": round(w3/total, 2),
            "w_recency": round(w4/total, 2)
        })
        
    return grid

def main():
    spark = SparkSession.builder \
        .appName("GraphRank Engine - Optimizer") \
        .config("spark.sql.shuffle.partitions", "10") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("ERROR")
    
    logger.info("Loading graph connections for Optimization Search...")
    df_connections = spark.read.csv("data/connections.csv", header=True, inferSchema=True)
    df_user_metrics = spark.read.parquet("processed/user_metrics")
    
    logger.info("Splitting data into 80% train and 20% test...")
    splits = df_connections.randomSplit([0.8, 0.2], seed=42)
    train_edges = splits[0].cache()
    test_edges = splits[1].cache()
    
    # Compute PageRank once for the search
    logger.info("Computing PageRank scores purely on Training Data...")
    pagerank_scores = calculate_pagerank(spark, train_edges, max_iter=5)
    
    grid = generate_search_grid(num_samples=5)
    best_weights = None
    best_precision = -1.0
    
    logger.info(f"Starting Random Search across {len(grid)} configurations...")
    
    for i, weights in enumerate(grid):
        logger.info(f"--- Variant {i+1}/{len(grid)} ---")
        logger.info(f"Weights: {weights}")
        
        recs = generate_recommendations(spark, train_edges, pagerank_scores, df_user_metrics, weights=weights)
        metrics = evaluate_predictions(recs, test_edges, k=10)
        
        logger.info(f"Precision@10: {metrics['precision_at_k']:.4f} | Recall: {metrics['recall']:.4f}")
        
        if metrics['precision_at_k'] > best_precision:
            best_precision = metrics['precision_at_k']
            best_weights = weights
            
    logger.info("=========================================")
    logger.info(f"🏆 BEST WEIGHTS FOUND (Precision: {best_precision:.4f}) 🏆")
    logger.info(json.dumps(best_weights, indent=4))
    
    # Save the optimal weights for the production engine
    os.makedirs("config", exist_ok=True)
    out_file = "config/ranking_weights.json"
    with open(out_file, "w") as f:
        json.dump(best_weights, f, indent=4)
        
    logger.info(f"Best weights exported to {out_file}. The Graph Engine will now use these automatically.")
    spark.stop()

if __name__ == "__main__":
    main()
