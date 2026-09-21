def satisfies(mask: int, clauses: list[list[int]]) -> bool:
    return all(
        any(bool(mask & (1 << (abs(literal) - 1))) == (literal > 0)
            for literal in clause)
        for clause in clauses
    )


def has_assignment(n: int, clauses: list[list[int]]) -> bool:
    for mask in range(1 << n):
        if satisfies(mask, clauses):
            return True
    return False
