import os
import json
import uuid
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("stream_processor")

# Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
POSTGRES_DSN = f"dbname=graphrank user=admin password=admin host={DB_HOST} port=5432"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def process_microbatch(df, epoch_id):
    """
    Process a microbatch of new interactions incrementally.
    """
    interactions = df.collect()
    if not interactions:
        return
        
    logger.info(f"Processing microbatch {epoch_id} with {len(interactions)} new interactions.")
    
    cache = get_redis_client()
    
    try:
        conn = psycopg2.connect(POSTGRES_DSN)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for row in interactions:
                user_a = row.user_a
                user_b = row.user_b
                
                # 1. Increment PageRank for user_b
                cur.execute("""
                    UPDATE users 
                    SET pagerank_score = pagerank_score + 0.02 
                    WHERE user_id = %s
                """, (user_b,))
                
                # 2. Triadic Closure
                cur.execute("""
                    SELECT recommended_user_id, score
                    FROM recommendations
                    WHERE user_id = %s
                    ORDER BY score DESC
                    LIMIT 5
                """, (user_b,))
                b_recs = cur.fetchall()
                
                if b_recs:
                    insert_query = """
                        INSERT INTO recommendations (user_id, recommended_user_id, score) 
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, recommended_user_id) 
                        DO UPDATE SET score = recommendations.score + EXCLUDED.score
                    """
                    for rec in b_recs:
                        new_score = rec['score'] * 0.5
                        if rec['recommended_user_id'] != user_a:
                            cur.execute(insert_query, (user_a, rec['recommended_user_id'], new_score))
                
                # 3. Invalidate caches
                cache.delete(f"recs:{user_a}")
                cache.delete(f"recs:{user_b}")
                
        conn.commit()
        conn.close()
        logger.info(f"Microbatch {epoch_id} processed successfully.")
    except Exception as e:
        logger.error(f"Error processing microbatch: {e}")

def main():
    spark = SparkSession.builder \
        .appName("GraphRank Stream Processor") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("ERROR")
    
    stream_dir = "data/stream"
    os.makedirs(stream_dir, exist_ok=True)
    
    logger.info(f"Starting GraphRank Structured Streaming on {stream_dir}...")
    
    schema = StructType([
        StructField("user_a", IntegerType(), True),
        StructField("user_b", IntegerType(), True)
    ])
    
    # Read streaming JSON files from directory
    streaming_df = spark.readStream \
        .schema(schema) \
        .json(stream_dir)
        
    # Process micro-batches
    query = streaming_df.writeStream \
        .foreachBatch(process_microbatch) \
        .outputMode("append") \
        .option("checkpointLocation", "processed/checkpoints/stream_interactions") \
        .start()
        
    query.awaitTermination()

if __name__ == "__main__":
    main()
