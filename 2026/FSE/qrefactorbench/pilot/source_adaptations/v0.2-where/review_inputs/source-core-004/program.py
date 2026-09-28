# Source portions: C2|Q> Dataset, CC BY 4.0; see supplied NOTICE.txt.

def clique_greedy(n, edges):
    clique = set()
    for node in range(n):
        if all((node, neighbor) in edges or (neighbor, node) in edges for neighbor in clique):
            clique.add(node)
    return clique

def clique_bitmask(n, edges):
    max_clique = []
    for mask in range(1 << n):
        subset = [i for i in range(n) if mask & (1 << i)]
        if all((u, v) in edges or (v, u) in edges for u in subset for v in subset if u != v):
            if len(subset) > len(max_clique):
                max_clique = subset
    return max_clique
