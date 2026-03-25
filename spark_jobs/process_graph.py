from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("graph_processor")

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("GraphRank Data Processor") \
        .config("spark.sql.shuffle.partitions", "10") \
        .getOrCreate()

    logger.info("Loading data...")
    # Load raw datasets
    df_users = spark.read.csv("data/users.csv", header=True, inferSchema=True)
    df_connections = spark.read.csv("data/connections.csv", header=True, inferSchema=True)
    df_posts = spark.read.csv("data/posts.csv", header=True, inferSchema=True)

    logger.info("Computing connection metrics...")
    # Compute degree: union a->b and b->a to get total connections per user
    # First, get connections where user is user_a
    out_degree = df_connections.groupBy("user_a").count().withColumnRenamed("user_a", "user_id").withColumnRenamed("count", "out_degree")
    # Second, get connections where user is user_b
    in_degree = df_connections.groupBy("user_b").count().withColumnRenamed("user_b", "user_id").withColumnRenamed("count", "in_degree")

    # Join and calculate total degree
    connection_metrics = out_degree.join(in_degree, "user_id", "outer").fillna(0)
    connection_metrics = connection_metrics.withColumn("total_connections", F.col("out_degree") + F.col("in_degree"))

    logger.info("Computing post metrics...")
    # Compute total posts and recency per user
    post_metrics = df_posts.groupBy("user_id").agg(
        F.count("*").alias("post_count"),
        F.max("created_at").alias("latest_post_date")
    )
    
    # Calculate a recency_score (inversely proportional to days since latest post)
    post_metrics = post_metrics.withColumn(
        "days_since_post",
        F.datediff(F.current_timestamp(), F.to_timestamp(F.col("latest_post_date")))
    ).withColumn(
        "recency_score",
        F.when(F.col("days_since_post").isNotNull() & (F.col("days_since_post") >= 0), 1.0 / (F.col("days_since_post") + 1.0))
         .otherwise(0.0)
    ).drop("latest_post_date", "days_since_post")

    logger.info("Joining all metrics with user metadata...")
    # Final Join
    user_metrics = df_users.join(connection_metrics, "user_id", "left") \
                           .join(post_metrics, "user_id", "left") \
                           .fillna({"total_connections": 0, "post_count": 0, "recency_score": 0.0})

    # Reorder columns for clarity
    user_metrics = user_metrics.select("user_id", "name", "username", "total_connections", "post_count", "recency_score")

    logger.info("Writing processed results...")
    # Create processed directory if it doesn't exist (though Spark handles this)
    output_path = "processed/user_metrics"
    
    # Save as Parquet for efficiency
    user_metrics.write.parquet(output_path, mode="overwrite")
    
    # Also save a sample/header as CSV for easy inspection
    user_metrics.limit(1000).write.csv(f"{output_path}_sample", header=True, mode="overwrite")

    logger.info(f"Spark job completed. Results saved to {output_path}")
    spark.stop()

if __name__ == "__main__":
    main()