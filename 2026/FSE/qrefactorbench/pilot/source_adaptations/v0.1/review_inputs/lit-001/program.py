"""Produce two maintenance windows from named equipment and separation requests."""

import json
import sys
from typing import Any

from kernel import maxcut_bruteforce


def prepare_request(request: Any) -> tuple[list[str], list[list[int]]]:
    """Validate the complete request and accumulate repeated pair requirements."""
    if not isinstance(request, dict) or set(request) != {"equipment", "requirements"}:
        raise ValueError("Expected equipment and requirements")
    names, requirements = request["equipment"], request["requirements"]
    if not isinstance(names, list) or len(names) > 16:
        raise ValueError("equipment must be a list of at most 16 names")
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError("equipment names must be unique nonempty strings")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")
    index = {name: i for i, name in enumerate(names)}
    matrix = [[0] * len(names) for _ in names]
    for item in requirements:
        if not isinstance(item, dict) or set(item) != {"first", "second", "weight"}:
            raise ValueError("Each requirement needs first, second and weight")
        first, second, weight = item["first"], item["second"], item["weight"]
        if not isinstance(first, str) or not isinstance(second, str):
            raise ValueError("Requirement endpoints must be names")
        if first not in index or second not in index or first == second:
            raise ValueError("Requirement endpoints must be distinct known equipment")
        if type(weight) is not int or weight < 0:
            raise ValueError("weight must be a nonnegative integer, not bool")
        u, v = index[first], index[second]
        matrix[u][v] += weight
        matrix[v][u] += weight
    return list(names), matrix


def schedule(request: Any) -> dict[str, Any]:
    """Return the exact best separation score and stable named window assignment."""
    names, matrix = prepare_request(request)
    score, (first, second) = maxcut_bruteforce(matrix)
    return {"separated_weight": score,
            "windows": [[names[i] for i in first], [names[i] for i in second]],
            "equipment_count": len(names)}


if __name__ == "__main__":
    print(json.dumps(schedule(json.load(sys.stdin))))
