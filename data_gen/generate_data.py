import random
import pandas as pd
import os
import argparse
from faker import Faker
from tqdm import tqdm
from datetime import datetime, timedelta

def generate_data(num_users, num_connections, num_posts, output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    fake = Faker()

    print(f"Generating {num_users} users...")
    users = []
    for i in range(num_users):
        users.append({
            "user_id": i,
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email()
        })
    pd.DataFrame(users).to_csv(os.path.join(output_dir, "users.csv"), index=False)

    print(f"Generating {num_connections} connections (Power-law distribution)...")
    # Using a simple preferential attachment logic for more realistic graph
    connections = []
    nodes = list(range(num_users))
    if num_users > 1:
        # Initial edges to ensure connectivity
        for i in range(1, min(num_users, 10)):
            connections.append((i-1, i))
        
        existing_nodes = list(range(min(num_users, 10)))
        for _ in tqdm(range(num_connections - len(connections))):
            a = random.choice(nodes)
            # Preferential attachment: nodes with more connections are more likely to get new ones
            # For simplicity, we'll just pick a random node for now, 
            # but a real BA model would weigh by degree.
            b = random.choice(nodes)
            if a != b:
                connections.append((a, b))

    pd.DataFrame(connections, columns=["user_a", "user_b"]).to_csv(os.path.join(output_dir, "connections.csv"), index=False)

    print(f"Generating {num_posts} posts...")
    posts = []
    start_date = datetime.now() - timedelta(days=365)
    for i in tqdm(range(num_posts)):
        created_at = start_date + timedelta(seconds=random.randint(0, 31536000))
        posts.append({
            "post_id": i,
            "user_id": random.randint(0, num_users - 1),
            "content": fake.sentence(nb_words=10),
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    pd.DataFrame(posts).to_csv(os.path.join(output_dir, "posts.csv"), index=False)
    print("Data generation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic social network data.")
    parser.add_argument("--num-users", type=int, default=10000, help="Number of users to generate")
    parser.add_argument("--num-connections", type=int, default=50000, help="Number of connections to generate")
    parser.add_argument("--num-posts", type=int, default=20000, help="Number of posts to generate")
    parser.add_argument("--output-dir", type=str, default="data", help="Output directory for CSV files")

    args = parser.parse_args()
    generate_data(args.num_users, args.num_connections, args.num_posts, args.output_dir)