def materialize(rows: list[list[int]], copies: int) -> list[list[float]]:
    output = []
    for row in rows:
        scale = sum(abs(value) for value in row)
        normalized = [value / scale if scale else 0.0 for value in row]
        for _ in range(copies):
            output.append(list(normalized))
    return output
