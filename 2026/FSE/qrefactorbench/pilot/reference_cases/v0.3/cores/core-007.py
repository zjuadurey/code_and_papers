"""Return a capacity-feasible index tuple with greatest total value."""


def select_items(sizes: list[int], values: list[int], capacity: int) -> tuple[int, ...]:
    best: tuple[int, ...] = ()
    best_value = 0
    for mask in range(1 << len(sizes)):
        chosen = tuple(i for i in range(len(sizes)) if mask & (1 << i))
        if sum(sizes[i] for i in chosen) > capacity:
            continue
        value = sum(values[i] for i in chosen)
        if value > best_value or (value == best_value and chosen < best):
            best, best_value = chosen, value
    return best
