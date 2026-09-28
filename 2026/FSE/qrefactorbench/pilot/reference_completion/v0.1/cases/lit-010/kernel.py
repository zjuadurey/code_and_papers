"""Small unpreconditioned CG path derived from HPCG's documented recurrence.

HPCG source: University of Tennessee/UT-Battelle/Sandia, BSD-3-Clause; NOTICE.txt.
No MPI, multigrid, performance rating or C++ translation system is implemented.
"""
import math


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def apply(rows, x):
    return [sum(value * x[j] for j, value in row) for row in rows]


def advance(rows, rhs, current, steps, tolerance):
    x = list(current)
    r = [b - v for b, v in zip(rhs, apply(rows, x))]
    initial = math.sqrt(dot(r, r))
    if not math.isfinite(initial):
        raise ValueError("numerical overflow")
    norm, trace, p, previous = initial, [], list(r), None
    while len(trace) < steps and initial and norm / initial > tolerance:
        rr = dot(r, r)
        if previous is not None:
            p = [v + rr / previous * old for v, old in zip(r, p)]
        ap = apply(rows, p)
        denominator = dot(p, ap)
        if denominator <= 0 or not math.isfinite(denominator):
            raise ValueError("numerical breakdown")
        alpha = rr / denominator
        x = [v + alpha * direction for v, direction in zip(x, p)]
        r = [v - alpha * av for v, av in zip(r, ap)]
        previous = rr
        norm = math.sqrt(dot(r, r))
        if not math.isfinite(norm) or any(not math.isfinite(v) for v in x):
            raise ValueError("numerical overflow")
        trace.append({"iteration": len(trace) + 1, "residual_norm": norm})
    return x, initial, trace
