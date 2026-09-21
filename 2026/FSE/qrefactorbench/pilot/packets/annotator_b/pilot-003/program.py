def best_partition_score(n: int, edges: list[tuple[int, int, int]]) -> int:
    best = 0
    for mask in range(1 << n):
        score = sum(weight for u, v, weight in edges
                    if ((mask >> u) & 1) != ((mask >> v) & 1))
        best = max(best, score)
    return best
