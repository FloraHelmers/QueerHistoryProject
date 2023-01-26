def top_n_degree_nodes(G, n):
    degree_dict = dict(G.degree())
    sorted_degree = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
    top_n_nodes = [node for node, degree in sorted_degree[:n]]
    return top_n_nodes

def common_neighbors(G, u, v):
    u_neighbors = set(G.neighbors(u))
    v_neighbors = set(G.neighbors(v))
    common_neighbors = u_neighbors.intersection(v_neighbors)
    return common_neighbors