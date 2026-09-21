"""Dense elimination with partial pivoting and an HPL-style residual diagnostic.

New small Python implementation of the documented problem, not an HPL port/rating.
"""
import math
import sys


def solve(matrix, rhs):
    n = len(rhs)
    rows = [list(row) + [b] for row, b in zip(matrix, rhs)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda i: abs(rows[i][col]))
        if rows[pivot][col] == 0:
            raise ValueError("singular system")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for i in range(col + 1, n):
            factor = rows[i][col] / rows[col][col]
            for j in range(col, n + 1):
                rows[i][j] -= factor * rows[col][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (rows[i][n] - sum(rows[i][j] * x[j] for j in range(i + 1, n))) / rows[i][i]
    if any(not math.isfinite(v) for v in x):
        raise ValueError("numerical overflow")
    return x


def residual(matrix, rhs, x):
    errors = [sum(a * v for a, v in zip(row, x)) - b for row, b in zip(matrix, rhs)]
    norm = max(map(abs, errors), default=0.0)
    a_norm = max((sum(map(abs, row)) for row in matrix), default=0.0)
    denominator = sys.float_info.epsilon * (a_norm * max(map(abs, x), default=0.0)
                   + max(map(abs, rhs), default=0.0)) * len(rhs)
    if any(not math.isfinite(v) for v in errors + [norm, denominator]):
        raise ValueError("numerical overflow")
    scaled = norm / denominator if denominator else (0.0 if norm == 0 else None)
    return {"vector": errors, "infinity_norm": norm, "scaled_backward_error": scaled}
