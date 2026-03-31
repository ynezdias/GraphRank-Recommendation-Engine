import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import redis
import json
import os
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("data_loader")

# Configuration (Supports Environment Variables for Docker)
DB_HOST = os.getenv("DB_HOST", "localhost")
POSTGRES_DSN = f"dbname=graphrank user=admin password=admin host={DB_HOST} port=5432"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

def create_tables(conn):
    logger.info("Initializing PostgreSQL schema (if not exists)...")
    with conn.cursor() as cur:
        # Create users table holding PageRank influence scores
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name VARCHAR(255),
                username VARCHAR(255),
                pagerank_score FLOAT DEFAULT 0.0
            );
        """)
        
        # Create recommendations table mapping user to recommended users
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                user_id INTEGER,
                recommended_user_id INTEGER,
                score FLOAT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                PRIMARY KEY (user_id, recommended_user_id)
            );
        """)
        
        # Performance Indexes for API Lookups
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_pagerank ON users(pagerank_score DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_recs_score ON recommendations(user_id, score DESC);")
        
        # Create recommendation engagements table for A/B testing
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recommendation_engagements (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                recommended_user_id INTEGER,
                experiment_variant VARCHAR(50),
                interaction_type VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.commit()

def load_data_to_postgres(conn):
    logger.info("Loading data into PostgreSQL...")
    
    with conn.cursor() as cur:
        # 1. Load Users & PageRank Scores
        # For simplicity, we assume we want to load users that have a PageRank score.
        # In a real system, we'd upsert or load all users then update scores.
        logger.info("  Reading pagerank sample data...")
        try:
            # We use the CSV sample for simplicity in this loader, 
            # in production we would read the Parquet files using pyarrow or similar.
            pr_df = pd.read_csv("processed/pagerank_scores_sample")
            # We also need the original user names to populate the users table properly.
            users_df = pd.read_csv("data/users.csv")
            
            # Merge to get names and pagerank together
            merged_users = pd.merge(pr_df, users_df, successfully_on="user_id", how="left").fillna("")
            
            # Prepare data for insertion
            user_records = merged_users[['user_id', 'name', 'username', 'pagerank']].to_records(index=False)
            
            logger.info("  Upserting user data...")
            execute_values(
                cur,
                """
                INSERT INTO users (user_id, name, username, pagerank_score) 
                VALUES %s 
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    username = EXCLUDED.username,
                    pagerank_score = EXCLUDED.pagerank_score
                """,
                user_records
            )
        except Exception as e:
             logger.warning(f"Could not load user PageRank data: {e}")


        # 2. Load Recommendations
        logger.info("  Reading recommendations sample data...")
        try:
            rec_df = pd.read_csv("processed/recommendations_sample")
            # Ensure we only insert recommendations where the base user exists in our sample 'users' table
            # to avoid foreign key constraints in this minimal setup
            valid_user_ids = merged_users['user_id'].tolist()
            filtered_recs = rec_df[rec_df['user_id'].isin(valid_user_ids)]
            
            rec_records = filtered_recs[['user_id', 'recommended_user_id', 'recommendation_score']].to_records(index=False)
            
            logger.info("  Upserting recommendation data...")
            execute_values(
                cur,
                """
                INSERT INTO recommendations (user_id, recommended_user_id, score) 
                VALUES %s 
                ON CONFLICT (user_id, recommended_user_id) 
                DO UPDATE SET score = EXCLUDED.score
                """,
                rec_records
            )
        except Exception as e:
            logger.warning(f"Could not load recommendations data: {e}")

    conn.commit()
    logger.info("PostgreSQL loading complete.")

def prime_redis_cache(conn, redis_cli):
    logger.info("Priming Redis cache with top recommendations...")
    
    with conn.cursor() as cur:
        # Get users who have recommendations
        cur.execute("SELECT DISTINCT user_id FROM recommendations")
        users = cur.fetchall()
        
        for (user_id,) in tqdm(users):
            # Fetch top 5 recommendations for this user
            cur.execute("""
                SELECT recommended_user_id, score 
                FROM recommendations 
                WHERE user_id = %s 
                ORDER BY score DESC LIMIT 5
            """, (user_id,))
            
            recs = cur.fetchall()
            
            # Format as JSON string for Redis value
            rec_list = [{"recommended_user_id": r_id, "score": score} for r_id, score in recs]
            
            # Cache the result with a TTL (e.g., 1 hour)
            cache_key = f"recs:{user_id}"
            redis_cli.setex(cache_key, 3600, json.dumps(rec_list))
            
    logger.info("Redis priming complete.")

def main():
    logger.info("Starting data loading process...")
    
    # 1. Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(POSTGRES_DSN)
        logger.info("Connected to PostgreSQL.")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL. Ensure it is running: {e}")
        return

    # 2. Connect to Redis
    try:
        redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        redis_cli.ping()
        logger.info("Connected to Redis.")
    except Exception as e:
        logger.error(f"Failed to connect to Redis. Ensure it is running: {e}")
        return

    # Execute loading steps
    create_tables(pg_conn)
    load_data_to_postgres(pg_conn)
    prime_redis_cache(pg_conn, redis_cli)
    
    # Cleanup
    pg_conn.close()
    logger.info("Process finished successfully.")

if __name__ == "__main__":
    main()
