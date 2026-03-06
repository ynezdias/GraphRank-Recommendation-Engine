import networkx as nx

def recommend(G, user):

    neighbors = set(G.neighbors(user))

    scores = {}

    for node in G.nodes():

        if node == user or node in neighbors:
            continue

        node_neighbors = set(G.neighbors(node))

        intersection = len(neighbors & node_neighbors)
        union = len(neighbors | node_neighbors)

        if union == 0:
            continue

        score = intersection / union

        scores[node] = score

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]