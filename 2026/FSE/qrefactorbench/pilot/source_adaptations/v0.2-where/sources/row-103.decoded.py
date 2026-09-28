def kcolor_with_color_sets(adj_list, k):
    vertices = list(adj_list.keys())
    n = len(vertices)
    color_sets = [set() for _ in range(k)]
    assignment = {v: None for v in vertices}

    i = 0
    while i < n:
        v = vertices[i]
        chosen = None
        c = 0
        while c < k:
            valid = True
            ns = adj_list[v]
            j = 0
            while j < len(ns):
                u = ns[j]
                if assignment[u] == c:
                    valid = False
                    break
                j += 1
            if valid:
                chosen = c
                break
            c += 1
        if chosen is None:
            raise ValueError('k-coloring failed')
        assignment[v] = chosen
        color_sets[chosen].add(v)
        i += 1
    return assignment, color_sets

adj = {
    0: [1,4],
    1: [0,2],
    2: [1,3,4],
    3: [2],
    4: [0,2]
}
print(kcolor_with_color_sets(adj, 3))