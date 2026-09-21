def min_vertex_cover_bruteforce(n, edges):
    min_cover = set()
    for i in range(1 << n):
        cover = {j for j in range(n) if i & (1 << j)}
        if all(u in cover or v in cover for u, v in edges):
            if not min_cover or len(cover) < len(min_cover):
                min_cover = cover
    return min_cover

# Input data
edges = [(0, 1), (1, 2), (2, 3)]
min_cover = min_vertex_cover_bruteforce(4, edges)
print(min_cover)