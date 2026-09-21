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

adj_list = {
    0: [1,2],
    1: [0,2,3],
    2: [0,1,3],
    3: [1,2]
}
print(kcolor_backtracking(adj_list, 3))