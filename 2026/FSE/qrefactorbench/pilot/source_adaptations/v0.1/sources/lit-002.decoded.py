import itertools

# Brute-force minimum vertex cover for a small graph

def min_vertex_cover_bruteforce(edges, n):
    nodes = list(range(n))
    best_cover = None
    for r in range(n + 1):
        for subset in itertools.combinations(nodes, r):
            cover = set(subset)
            ok = True
            for u, v in edges:
                if u not in cover and v not in cover:
                    ok = False
                    break
            if ok:
                best_cover = cover
                return best_cover
    return best_cover

edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
cover = min_vertex_cover_bruteforce(edges, 4)
print(sorted(cover))