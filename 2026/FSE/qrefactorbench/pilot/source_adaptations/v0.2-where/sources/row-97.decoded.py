def greedy_kcolor_adj_matrix(adj_matrix, k):
    n = len(adj_matrix)
    colors = [-1] * n
    v = 0
    while v < n:
        used = set()
        u = 0
        while u < n:
            if adj_matrix[v][u] == 1 and colors[u] != -1:
                used.add(colors[u])
            u += 1
        c = 0
        while c < k and c in used:
            c += 1
        if c == k:
            raise ValueError('k-coloring failed at vertex {}'.format(v))
        colors[v] = c
        v += 1
    return colors

adj = [
    [0,1,1,0],
    [1,0,1,1],
    [1,1,0,1],
    [0,1,1,0]
]
print(greedy_kcolor_adj_matrix(adj, 3))