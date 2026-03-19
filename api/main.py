from fastapi import FastAPI, HTTPException, Depends, Request
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import redis
import json
import logging
import time
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("graph_api")

app = FastAPI(
    title="GraphRank API",
    description="API for accessing social network influence and recommendation metrics.",
    version="1.0.0"
)

import os

# Configuration (Supports Environment Variables for Docker)
DB_HOST = os.getenv("DB_HOST", "localhost")
POSTGRES_DSN = f"dbname=graphrank user=admin password=admin host={DB_HOST} port=5432"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# PostgreSQL Connection Pool
db_pool = None

@app.on_event("startup")
def startup():
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, POSTGRES_DSN)
        if db_pool:
            logger.info("PostgreSQL connection pool initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")

@app.on_event("shutdown")
def shutdown():
    if db_pool:
        db_pool.closeall()
        logger.info("PostgreSQL connection pool closed.")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    logger.info(f"{request.method} {request.url.path} completed in {process_time:.2f}ms with status code {response.status_code}")
    return response

# Dependency to get DB connection per request from pool
def get_db():
    if db_pool is None:
        raise HTTPException(status_code=500, detail="Database pool not initialized")
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

# Dependency to get Redis client
def get_redis():
    try:
        return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        raise HTTPException(status_code=500, detail="Redis connection failed")

class Interaction(BaseModel):
    user_a: int
    user_b: int

@app.post("/interactions")
def add_interaction(interaction: Interaction, db = Depends(get_db), cache = Depends(get_redis)):
    """
    Real-time interaction ingestion endpoint simulating near real-time updates.
    """
    # 1. Append to CSV for batch processing
    try:
        # We append directly to the connections.csv
        with open("data/connections.csv", "a") as f:
            f.write(f"\n{interaction.user_a},{interaction.user_b}")
    except Exception as e:
        logger.error(f"Failed to append to connections.csv: {e}")
        # We continue despite CSV failure, to ensure the real-time DB is updated
        
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            # 2. Increment PageRank for user_b
            # Since they received a new inbound link, we instantly bump their influence slightly.
            cur.execute("""
                UPDATE users 
                SET pagerank_score = pagerank_score + 0.02 
                WHERE user_id = %s
            """, (interaction.user_b,))
            
            # 3. Triadic Closure: Fetch user_b's current recommendations
            cur.execute("""
                SELECT recommended_user_id, score
                FROM recommendations
                WHERE user_id = %s
                ORDER BY score DESC
                LIMIT 5
            """, (interaction.user_b,))
            b_recs = cur.fetchall()
            
            if b_recs:
                # Recommend them to user_a as well
                insert_query = """
                    INSERT INTO recommendations (user_id, recommended_user_id, score) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, recommended_user_id) 
                    DO UPDATE SET score = recommendations.score + EXCLUDED.score
                """
                for rec in b_recs:
                    # Discount the score to reflect length-2 path
                    new_score = rec['score'] * 0.5
                    # Don't recommend self
                    if rec['recommended_user_id'] != interaction.user_a:
                        cur.execute(insert_query, (interaction.user_a, rec['recommended_user_id'], new_score))
                
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
        
    # 4. Invalidate Redis Caches
    try:
        cache.delete(f"recs:{interaction.user_a}")
        cache.delete(f"recs:{interaction.user_b}")
    except Exception as e:
        logger.warning(f"Failed to clear Redis cache: {e}")
        
    return {"status": "success", "message": "Interaction recorded and real-time updates applied.", "interaction": interaction.dict()}

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "GraphRank API"}

@app.get("/top-influencers")
def get_top_influencers(limit: int = 10, db = Depends(get_db)):
    """
    Retrieves the top users ranked by their PageRank influence score.
    Queries the PostgreSQL database directly.
    """
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT user_id, name, username, pagerank_score 
                FROM users 
                ORDER BY pagerank_score DESC 
                LIMIT %s
            """, (limit,))
            influencers = cur.fetchall()
            return {"top_influencers": influencers}
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to query influencers: {str(e)}")

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, db = Depends(get_db), cache = Depends(get_redis)):
    """
    Retrieves 'People You May Know' recommendations for a specific user.
    Implements a Cache-Aside pattern using Redis.
    """
    cache_key = f"recs:{user_id}"
    
    # 1. Try to fetch from Redis Cache first (Lightning fast!)
    try:
        cached_recs = cache.get(cache_key)
        if cached_recs:
            return {
                "user_id": user_id, 
                "source": "redis_cache", 
                "recommendations": json.loads(cached_recs)
            }
    except Exception as e:
        logger.warning(f"Redis cache lookup failed: {e}")
        # Continue to DB query if cache fails
    
    # 2. Cache Miss: Fetch from PostgreSQL
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            # Join with users table to get recommended user details
            cur.execute("""
                SELECT r.recommended_user_id, u.name, u.username, r.score 
                FROM recommendations r
                JOIN users u ON r.recommended_user_id = u.user_id
                WHERE r.user_id = %s 
                ORDER BY r.score DESC 
                LIMIT 10
            """, (user_id,))
            recs = cur.fetchall()
            
            if not recs:
                # If the user has no recommendations, return empty list
                return {"user_id": user_id, "source": "postgres", "recommendations": []}
                
            # 3. Cache the result for next time (e.g., expire in 1 hour)
            try:
                # We format slightly differently for cache to store just core IDs/scores
                cache_list = [{"recommended_user_id": r["recommended_user_id"], "score": r["score"]} for r in recs]
                cache.setex(cache_key, 3600, json.dumps(cache_list))
            except Exception as e:
                 logger.warning(f"Failed to write to Redis cache: {e}")
                 
            return {
                "user_id": user_id, 
                "source": "postgres", 
                "recommendations": recs
            }
            
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to query recommendations: {str(e)}")

# To run locally: uvicorn api.main:app --reload