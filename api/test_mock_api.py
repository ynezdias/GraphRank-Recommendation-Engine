from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import sqlite3
import json

app = FastAPI()

# In-memory "Redis" cache
mock_redis_cache = {}

def get_db():
    conn = sqlite3.connect("local_graphrank.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = get_db()
    cur = conn.cursor()
    
    # Init Tables
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, pagerank_score REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS recommendations (user_id INTEGER, recommended_user_id INTEGER, score REAL)")
    
    # Load Dummy Data
    cur.execute("DELETE FROM users")
    cur.execute("DELETE FROM recommendations")
    
    users = [
        (1, 'Alice', 'alice', 0.9),
        (2, 'Bob', 'bob', 0.8),
        (3, 'Charlie', 'charlie', 0.5)
    ]
    cur.executemany("INSERT INTO users VALUES (?,?,?,?)", users)
    
    recs = [
        (1, 2, 85.0),
        (1, 3, 40.0)
    ]
    cur.executemany("INSERT INTO recommendations VALUES (?,?,?)", recs)
    conn.commit()
    conn.close()

@app.get("/top-influencers")
def get_top_influencers(limit: int = 10):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY pagerank_score DESC LIMIT ?", (limit,))
    influencers = [dict(row) for row in cur.fetchall()]
    conn.close()
    return {"top_influencers": influencers}

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int):
    cache_key = f"recs:{user_id}"
    
    if cache_key in mock_redis_cache:
        return {"user_id": user_id, "source": "redis_cache", "recommendations": mock_redis_cache[cache_key]}
        
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT r.recommended_user_id, u.name, u.username, r.score 
        FROM recommendations r
        JOIN users u ON r.recommended_user_id = u.user_id
        WHERE r.user_id = ? 
        ORDER BY r.score DESC 
        LIMIT 10
    ''', (user_id,))
    
    recs = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    if recs:
        # Cache for next time
        mock_redis_cache[cache_key] = recs
        
    return {"user_id": user_id, "source": "postgres", "recommendations": recs}

# --- Test Script ---
def test_api():
    client = TestClient(app)
    # Trigger startup to load data
    with client:
        print("Testing /top-influencers...")
        response = client.get("/top-influencers")
        print("Status code:", response.status_code)
        print("Response:", json.dumps(response.json(), indent=2))
        
        print("\nTesting /recommendations/1 (First call, should hit DB)...")
        response1 = client.get("/recommendations/1")
        print("Source:", response1.json().get("source"))
        print("Response:", json.dumps(response1.json(), indent=2))
        
        print("\nTesting /recommendations/1 (Second call, should hit Cache)...")
        response2 = client.get("/recommendations/1")
        print("Source:", response2.json().get("source"))
        print("Response:", json.dumps(response2.json(), indent=2))

if __name__ == "__main__":
    test_api()
