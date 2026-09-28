"""Capacity table for indivisible items; newly authored from a source task."""


def choose(items, capacity):
    table = [(0, 0) for _ in range(capacity + 1)]
    for i, item in enumerate(items):
        previous = table
        table = list(previous)
        for available in range(item["weight"], capacity + 1):
            value, mask = previous[available - item["weight"]]
            candidate = (value + item["value"], mask | (1 << i))
            incumbent = previous[available]
            if candidate[0] > incumbent[0] or (candidate[0] == incumbent[0] and candidate[1] < incumbent[1]):
                table[available] = candidate
    return table[capacity][1]
