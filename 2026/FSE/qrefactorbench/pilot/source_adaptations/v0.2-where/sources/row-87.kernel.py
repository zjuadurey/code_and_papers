def clique_brute_force(n, edges):
    from itertools import combinations
    max_clique = []
    for k in range(2, n+1):
        for subset in combinations(range(n), k):
            if all((u, v) in edges or (v, u) in edges for u in subset for v in subset if u != v):
                if len(subset) > len(max_clique):
                    max_clique = subset
    return max_clique
