def has_total(values: list[int], target: int) -> bool:
    for mask in range(1 << len(values)):
        total = sum(value for index, value in enumerate(values)
                    if mask & (1 << index))
        if total == target:
            return True
    return False
