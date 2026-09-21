"""Review a named balance system, optionally compute a replacement vector."""
import json
import sys
from common import fields, finite, names, vector
from kernel import residual, solve


def review(request):
    fields(request, ("variables", "matrix", "rhs", "current", "mode", "residual_limit"))
    variables = names(request["variables"])
    n = len(variables)
    if not isinstance(request["matrix"], list) or len(request["matrix"]) != n:
        raise ValueError("square matrix required")
    matrix = [vector(row, n) for row in request["matrix"]]
    rhs, current = vector(request["rhs"], n), vector(request["current"], n)
    limit = finite(request["residual_limit"])
    if limit < 0 or request["mode"] not in ("inspect", "solve"):
        raise ValueError("invalid limit or mode")
    before = residual(matrix, rhs, current)
    report = {"current_residual": before, "proposal": None, "proposed_residual": None,
              "within_requested_limit": None, "deltas": None}
    if request["mode"] == "solve":
        x = solve(matrix, rhs)
        after = residual(matrix, rhs, x)
        report.update(proposal=dict(zip(variables, x)), proposed_residual=after,
                      within_requested_limit=after["scaled_backward_error"] is not None and after["scaled_backward_error"] <= limit,
                      deltas=dict(zip(variables, [a - b for a, b in zip(x, current)])))
    return report


if __name__ == "__main__":
    print(json.dumps(review(json.load(sys.stdin)), indent=2))
