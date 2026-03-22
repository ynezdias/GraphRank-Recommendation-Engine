from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import sqlite3
import json
from pydantic import BaseModel

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

class Interaction(BaseModel):
    user_a: int
    user_b: int

@app.post("/interactions")
def add_interaction(interaction: Interaction):
    # Invalidate Mock Redis Cache
    cache_key_a = f"recs:{interaction.user_a}"
    cache_key_b = f"recs:{interaction.user_b}"
    if cache_key_a in mock_redis_cache:
        del mock_redis_cache[cache_key_a]
    if cache_key_b in mock_redis_cache:
        del mock_redis_cache[cache_key_b]
        
    conn = get_db()
    cur = conn.cursor()
    # 1. Update PageRank globally
    cur.execute("UPDATE users SET pagerank_score = pagerank_score + 0.1 WHERE user_id = ?", (interaction.user_b,))
    
    # 2. Triadic Closure
    cur.execute("SELECT recommended_user_id, score FROM recommendations WHERE user_id = ? ORDER BY score DESC LIMIT 5", (interaction.user_b,))
    b_recs = [dict(row) for row in cur.fetchall()]
    
    for rec in b_recs:
        new_score = rec['score'] * 0.5
        if rec['recommended_user_id'] != interaction.user_a:
            cur.execute("INSERT INTO recommendations (user_id, recommended_user_id, score) VALUES (?, ?, ?)", 
                        (interaction.user_a, rec['recommended_user_id'], new_score))
            
    conn.commit()
    conn.close()
    return {"status": "success"}

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
        
        print("\n--- SIMULATING REAL-TIME INTERACTION ---")
        print("User 3 connects to User 1.")
        client.post("/interactions", json={"user_a": 3, "user_b": 1})
        
        print("\nTesting /top-influencers (Verifying PageRank went up)...")
        response_pr = client.get("/top-influencers")
        print("Response:", json.dumps(response_pr.json(), indent=2))
        
        print("\nTesting /recommendations/3 (Checking for new dynamic Triadic Closure recs)...")
        response_recs = client.get("/recommendations/3")
        print("Source:", response_recs.json().get("source"))
        print("Response:", json.dumps(response_recs.json(), indent=2))

if __name__ == "__main__":
    test_api()
