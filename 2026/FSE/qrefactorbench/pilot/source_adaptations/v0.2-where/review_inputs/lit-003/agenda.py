"""Construct ordered agenda proposals from participant conflicts."""

# Adapted source portions: C2|Q> Dataset, CC BY 4.0; see supplied NOTICE.txt.


def preview(matrix: list[list[int]], slot_count: int) -> list[int]:
    # First available slot in session order. A blocked preview is inconclusive.
    n = len(matrix)
    assigned = [-1] * n
    v = 0
    while v < n:
        used = set()
        u = 0
        while u < n:
            if matrix[v][u] == 1 and assigned[u] != -1:
                used.add(assigned[u])
            u += 1
        slot = 0
        while slot < slot_count and slot in used:
            slot += 1
        if slot == slot_count:
            raise ValueError("preview blocked")
        assigned[v] = slot
        v += 1
    return assigned


def complete(neighbors: dict[int, list[int]], slot_count: int) -> list[int]:
    n = len(neighbors)
    assigned = [-1] * n

    def available(v: int, slot: int) -> bool:
        idx = 0
        linked = neighbors[v]
        while idx < len(linked):
            u = linked[idx]
            if assigned[u] == slot:
                return False
            idx += 1
        return True

    def place(v: int) -> bool:
        if v == n:
            return True
        slot = 0
        while slot < slot_count:
            if available(v, slot):
                assigned[v] = slot
                if place(v + 1):
                    return True
                assigned[v] = -1
            slot += 1
        return False

    if not place(0):
        raise ValueError("no arrangement")
    return assigned
