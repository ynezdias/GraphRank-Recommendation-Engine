from fastapi import FastAPI, HTTPException, Depends, Request
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import redis
import json
import logging
import time

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