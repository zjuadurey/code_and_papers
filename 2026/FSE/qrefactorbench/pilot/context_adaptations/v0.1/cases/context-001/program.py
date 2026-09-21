"""Assess a current maintenance assignment and explain a proposed alternative."""

import json
import sys
from typing import Any

from maintenance import compare_assignments, evaluate_windows, maxcut_bruteforce, prepare_request


def review_schedule(request: Any) -> dict[str, Any]:
    """Return an exact assignment comparison with ordered, named explanations."""
    names, matrix, current_windows = prepare_request(request)
    current = evaluate_windows(names, matrix, current_windows)
    _, (first, second) = maxcut_bruteforce(matrix)
    proposed = evaluate_windows(names, matrix, [first, second])
    return {"equipment_count": len(names), "requirement_count": len(request["requirements"]),
            "current": current, "proposed": proposed,
            "changes": compare_assignments(names, current, proposed)}


if __name__ == "__main__":
    print(json.dumps(review_schedule(json.load(sys.stdin)), indent=2))
