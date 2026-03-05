import networkx as nx
import pandas as pd

connections = pd.read_csv("connections.csv")

G = nx.Graph()

for _,row in connections.iterrows():
    G.add_edge(row["user_a"], row["user_b"])

pagerank = nx.pagerank(G)

df = pd.DataFrame(pagerank.items(), columns=["user_id","score"])

df.to_csv("pagerank_scores.csv", index=False)

print("PageRank Computed")