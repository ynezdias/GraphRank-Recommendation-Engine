import random
import pandas as pd

NUM_USERS = 100000
NUM_CONNECTIONS = 1000000
NUM_POSTS = 500000

users = [{"id": i, "name": f"user_{i}"} for i in range(NUM_USERS)]

connections = []
for _ in range(NUM_CONNECTIONS):
    a = random.randint(0, NUM_USERS-1)
    b = random.randint(0, NUM_USERS-1)

    if a != b:
        connections.append((a,b))

posts = []
for i in range(NUM_POSTS):
    posts.append({
        "post_id": i,
        "user_id": random.randint(0,NUM_USERS-1),
        "content": "Sample post",
    })

pd.DataFrame(users).to_csv("users.csv", index=False)
pd.DataFrame(connections, columns=["user_a","user_b"]).to_csv("connections.csv", index=False)
pd.DataFrame(posts).to_csv("posts.csv", index=False)

print("Synthetic Data Generated")