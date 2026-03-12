import pandas as pd
import networkx as nx

connections = pd.read_csv("data/connections.csv")

G = nx.Graph()

for _,row in connections.iterrows():
    G.add_edge(row["user_a"], row["user_b"])

pagerank_scores = nx.pagerank(G)

df = pd.DataFrame(
    pagerank_scores.items(),
    columns=["user_id","pagerank"]
)

df.to_csv("processed/pagerank_scores.csv", index=False)