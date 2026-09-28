def clique_backtracking(n, edges):
    def is_clique(nodes):
        return all((u, v) in edges or (v, u) in edges for u in nodes for v in nodes if u != v)
    def backtrack(node, current_clique):
        if node == n:
            return current_clique
        if is_clique(current_clique + [node]):
            with_node = backtrack(node + 1, current_clique + [node])
            without_node = backtrack(node + 1, current_clique)
            return max(with_node, without_node, key=len)
        return backtrack(node + 1, current_clique)
    return backtrack(0, [])