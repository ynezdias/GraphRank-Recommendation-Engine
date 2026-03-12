import pandas as pd
import psycopg2

df = pd.read_csv("processed/pagerank_scores.csv")

conn = psycopg2.connect(
    host="localhost",
    database="graphrank",
    user="admin",
    password="admin"
)

cur = conn.cursor()

for _,row in df.iterrows():

    cur.execute(
        "INSERT INTO influence_scores (user_id,score) VALUES (%s,%s)",
        (int(row.user_id), float(row.pagerank))
    )

conn.commit()