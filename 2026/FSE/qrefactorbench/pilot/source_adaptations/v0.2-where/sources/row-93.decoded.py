def clique_bitmask(n, edges):
    max_clique = []
    for mask in range(1 << n):
        subset = [i for i in range(n) if mask & (1 << i)]
        if all((u, v) in edges or (v, u) in edges for u in subset for v in subset if u != v):
            if len(subset) > len(max_clique):
                max_clique = subset
    return max_clique