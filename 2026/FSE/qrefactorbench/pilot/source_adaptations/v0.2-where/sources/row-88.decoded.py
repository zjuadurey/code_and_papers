def clique_greedy(n, edges):
    clique = set()
    for node in range(n):
        if all((node, neighbor) in edges or (neighbor, node) in edges for neighbor in clique):
            clique.add(node)
    return clique