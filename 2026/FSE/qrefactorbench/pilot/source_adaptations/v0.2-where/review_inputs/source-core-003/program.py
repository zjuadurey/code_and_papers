# Source portions: C2|Q> Dataset, CC BY 4.0; see supplied NOTICE.txt.

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

def kcolor_backtracking(adj_list, k):
    n = len(adj_list)
    colors = [-1] * n

    def is_safe(v, col):
        idx = 0
        neighbors = adj_list[v]
        while idx < len(neighbors):
            u = neighbors[idx]
            if colors[u] == col:
                return False
            idx += 1
        return True

    def assign_color(v):
        if v == n:
            return True
        c = 0
        while c < k:
            if is_safe(v, c):
                colors[v] = c
                if assign_color(v + 1):
                    return True
                colors[v] = -1
            c += 1
        return False

    if not assign_color(0):
        raise ValueError('No {}-coloring exists'.format(k))
    return colors
