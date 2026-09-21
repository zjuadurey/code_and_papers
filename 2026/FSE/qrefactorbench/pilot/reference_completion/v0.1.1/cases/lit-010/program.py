"""Advance a sparse balance calculation under a caller's iteration budget."""
import json
import math
import sys
from common import fields, finite, integer, names, vector
from kernel import advance, apply, dot


def review(request):
    fields(request, ("variables", "entries", "rhs", "current", "steps", "relative_tolerance", "mode"))
    variables = names(request["variables"])
    n = len(variables)
    rhs, current = vector(request["rhs"], n), vector(request["current"], n)
    steps, tolerance = integer(request["steps"]), finite(request["relative_tolerance"])
    if tolerance < 0 or request["mode"] not in ("inspect", "advance") or not isinstance(request["entries"], list):
        raise ValueError("invalid mode, entries or tolerance")
    matrix = {}
    for item in request["entries"]:
        fields(item, ("row", "column", "value"))
        if item["row"] not in variables or item["column"] not in variables:
            raise ValueError("unknown variable")
        i, j = variables.index(item["row"]), variables.index(item["column"])
        if (i, j) in matrix:
            raise ValueError("duplicate entry")
        matrix[i, j] = finite(item["value"])
    for (i, j), value in matrix.items():
        if matrix.get((j, i), 0.0) != value:
            raise ValueError("symmetric matrix required")
    rows = [[(j, matrix[i, j]) for j in range(n) if (i, j) in matrix] for i in range(n)]
    for i, row in enumerate(rows):
        if matrix.get((i, i), 0.0) <= sum(abs(v) for j, v in row if j != i):
            raise ValueError("positive strict diagonal dominance required")
    before = [b - v for b, v in zip(rhs, apply(rows, current))]
    before_norm = math.sqrt(dot(before, before))
    if not math.isfinite(before_norm):
        raise ValueError("numerical overflow")
    report = {"initial_residual_norm": before_norm, "proposal": None, "trace": [],
              "iterations": 0, "final_residual_norm": None}
    if request["mode"] == "advance":
        x, _, trace = advance(rows, rhs, current, steps, tolerance)
        final = [b - v for b, v in zip(rhs, apply(rows, x))]
        norm = math.sqrt(dot(final, final))
        if not math.isfinite(norm):
            raise ValueError("numerical overflow")
        report.update(proposal=dict(zip(variables, x)), trace=trace,
                      iterations=len(trace), final_residual_norm=norm)
    return report


if __name__ == "__main__":
    print(json.dumps(review(json.load(sys.stdin)), indent=2))
