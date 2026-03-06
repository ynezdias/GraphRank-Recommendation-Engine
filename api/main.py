from fastapi import FastAPI
import redis
import psycopg2

app = FastAPI()

redis_client = redis.Redis(host="redis", port=6379)

conn = psycopg2.connect(
    host="postgres",
    database="graphrank",
    user="admin",
    password="admin"
)

@app.get("/influencers")

def influencers():

    cur = conn.cursor()

    cur.execute(
        "SELECT user_id, score FROM influence_scores ORDER BY score DESC LIMIT 10"
    )

    rows = cur.fetchall()

    return {"top_influencers": rows}


@app.get("/feed/{user_id}")

def get_feed(user_id:int):

    cache = redis_client.get(f"feed:{user_id}")

    if cache:
        return {"feed": cache}

    cur = conn.cursor()

    cur.execute(
        "SELECT content FROM posts ORDER BY created_at DESC LIMIT 20"
    )

    posts = cur.fetchall()

    redis_client.set(f"feed:{user_id}", str(posts))

    return {"feed": posts}