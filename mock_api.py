from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/top-influencers")
def get_top_influencers(limit: int = 5):
    # Mocking dynamic PageRank changes
    base_scores = [0.952, 0.812, 0.760, 0.650, 0.540]
    jitter = [s + random.uniform(-0.02, 0.02) for s in base_scores]
    return {"top_influencers": [
        {"user_id": 1, "name": "Alice Expert", "username": "alice", "pagerank_score": jitter[0]},
        {"user_id": 2, "name": "Bob Networker", "username": "bob_net", "pagerank_score": jitter[1]},
        {"user_id": 3, "name": "Charlie Connector", "username": "charliec", "pagerank_score": jitter[2]},
        {"user_id": 4, "name": "Dana Insight", "username": "dana_i", "pagerank_score": jitter[3]},
        {"user_id": 5, "name": "Eve Developer", "username": "eve_dev", "pagerank_score": jitter[4]},
    ]}

@app.get("/api/recommendations/{user_id}")
def get_recommendations(user_id: int):
    variant = "treatment" if int(user_id) % 2 == 0 else "control"
    return {
        "user_id": user_id,
        "experiment_variant": variant,
        "source": "redis_cache_mock",
        "recommendations": [
            {"recommended_user_id": 101, "name": "John Doe", "score": 0.89 + random.uniform(-0.05, 0.05)},
            {"recommended_user_id": 102, "name": "Jane Smith", "score": 0.75 + random.uniform(-0.05, 0.05)},
            {"recommended_user_id": 103, "name": "Michael Tech", "score": 0.65 + random.uniform(-0.05, 0.05)},
            {"recommended_user_id": 104, "name": "Sarah Code", "score": 0.55 + random.uniform(-0.05, 0.05)},
        ]
    }

# Mount the static frontend directory directly to the root path 
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
