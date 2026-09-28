def format_label(name: str) -> str:
    return name.strip().upper()


def max_cut_score(n: int, edges: list[tuple[int, int]]) -> int:
    """Exact small-graph enumeration; callers supply valid vertex indices."""
    best = 0
    for mask in range(1 << n):
        best = max(best, sum(((mask >> a) & 1) != ((mask >> b) & 1) for a, b in edges))
    return best
