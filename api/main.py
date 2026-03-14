from fastapi import FastAPI, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import json

app = FastAPI(
    title="GraphRank API",
    description="API for accessing social network influence and recommendation metrics.",
    version="1.0.0"
)

# Configuration
POSTGRES_DSN = "dbname=graphrank user=admin password=admin host=localhost port=5432"
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Dependency to get DB connection per request
def get_db():
    conn = None
    try:
        conn = psycopg2.connect(POSTGRES_DSN)
        yield conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")
    finally:
        if conn:
            conn.close()

# Dependency to get Redis client
def get_redis():
    try:
        return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    except Exception as e:
        print(f"Redis connection error: {e}")
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
        print(f"Warning: Redis cache lookup failed: {e}")
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
                 print(f"Warning: Failed to write to Redis cache: {e}")
                 
            return {
                "user_id": user_id, 
                "source": "postgres", 
                "recommendations": recs
            }
            
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to query recommendations: {str(e)}")

# To run locally: uvicorn api.main:app --reload