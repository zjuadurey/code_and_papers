def kcolor_backtrack_partial(adj_list, k):
    # variant with vertex ordering and while-based neighbor checks
    order = list(adj_list.keys())
    n = len(order)
    colors = {v: -1 for v in order}

    def safe(v, col):
        ns = adj_list[v]
        i = 0
        while i < len(ns):
            u = ns[i]
            if colors[u] == col:
                return False
            i += 1
        return True

    def dfs(pos):
        if pos == n:
            return True
        v = order[pos]
        c = 0
        while c < k:
            if safe(v, c):
                colors[v] = c
                if dfs(pos + 1):
                    return True
                colors[v] = -1
            c += 1
        return False

    if not dfs(0):
        raise RuntimeError('No {}-coloring found'.format(k))
    return colors

adj = {
    0: [1,2,3],
    1: [0,2],
    2: [0,1,3],
    3: [0,2]
}
print(kcolor_backtrack_partial(adj, 3))