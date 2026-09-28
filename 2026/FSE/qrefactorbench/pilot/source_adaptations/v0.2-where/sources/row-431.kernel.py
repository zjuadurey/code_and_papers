import itertools

def is_cover(cover, edges):
    for u, v in edges:
        if u not in cover and v not in cover:
            return False
    return True

def min_vertex_cover_bnb(edges, n):
    best = None
    nodes = list(range(n))
    for r in range(1, n + 1):
        for subset in itertools.combinations(nodes, r):
            cover = set(subset)
            if is_cover(cover, edges):
                best = cover
                return best
    return best
