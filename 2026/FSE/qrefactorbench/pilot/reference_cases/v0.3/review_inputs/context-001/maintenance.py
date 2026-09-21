"""Validation, assignment calculations and reporting for two maintenance windows."""

from typing import Any


def prepare_request(request: Any) -> tuple[list[str], list[list[int]], list[list[int]]]:
    """Validate all data before evaluating either assignment; never mutate input."""
    required = {"equipment", "requirements", "current_windows"}
    if not isinstance(request, dict) or set(request) != required:
        raise ValueError("Expected equipment, requirements and current_windows")
    names = request["equipment"]
    if not isinstance(names, list) or len(names) > 16:
        raise ValueError("equipment must be a list of at most 16 names")
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError("equipment names must be unique nonempty strings")
    index = {name: i for i, name in enumerate(names)}
    requirements = request["requirements"]
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")
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
    windows = request["current_windows"]
    if not isinstance(windows, list) or len(windows) != 2:
        raise ValueError("current_windows must contain exactly two lists")
    seen: set[str] = set()
    current = []
    for window in windows:
        if not isinstance(window, list):
            raise ValueError("Each window must be a list")
        positions = []
        for name in window:
            if not isinstance(name, str) or name not in index or name in seen:
                raise ValueError("Each equipment name must occur exactly once")
            seen.add(name)
            positions.append(index[name])
        current.append(sorted(positions))
    if seen != set(names):
        raise ValueError("Every equipment item must be assigned")
    return list(names), matrix, current


def evaluate_windows(
    names: list[str], matrix: list[list[int]], windows: list[list[int]]
) -> dict[str, Any]:
    """Describe a validated assignment, including positive-weight conflicts."""
    side = {position: group for group, members in enumerate(windows) for position in members}
    conflicts = []
    total_weight = 0
    for u in range(len(names)):
        for v in range(u + 1, len(names)):
            weight = matrix[u][v]
            total_weight += weight
            if weight > 0 and side[u] == side[v]:
                conflicts.append({"first": names[u], "second": names[v], "weight": weight})
    conflict_weight = sum(item["weight"] for item in conflicts)
    return {"windows": [[names[i] for i in members] for members in windows],
            "conflict_weight": conflict_weight,
            "separated_weight": total_weight - conflict_weight,
            "conflicts": conflicts}


def maxcut_bruteforce(adj):
    n=len(adj)
    best=-1
    best_part=None
    for mask in range(1<<n):
        left=[i for i in range(n) if (mask>>i)&1]
        right=[i for i in range(n) if not (mask>>i)&1]
        val=0
        for i in range(n):
            for j in range(i+1,n):
                if adj[i][j]!=0 and ((i in left and j in right) or (i in right and j in left)):
                    val+=adj[i][j]
        if val>best:
            best=val
            best_part=(left,right)
    return best,best_part


def compare_assignments(
    names: list[str], current: dict[str, Any], proposed: dict[str, Any]
) -> dict[str, Any]:
    """Report changes without adding movement cost to the selection objective."""
    old_side = {name: group for group, members in enumerate(current["windows"]) for name in members}
    new_side = {name: group for group, members in enumerate(proposed["windows"]) for name in members}
    moved = [{"equipment": name, "from_window": old_side[name], "to_window": new_side[name]}
             for name in names if old_side[name] != new_side[name]]
    old_pairs = {(item["first"], item["second"]) for item in current["conflicts"]}
    new_pairs = {(item["first"], item["second"]) for item in proposed["conflicts"]}
    return {"moved_equipment": moved,
            "conflict_reduction": current["conflict_weight"] - proposed["conflict_weight"],
            "resolved_conflicts": [item.copy() for item in current["conflicts"]
                                   if (item["first"], item["second"]) not in new_pairs],
            "introduced_conflicts": [item.copy() for item in proposed["conflicts"]
                                     if (item["first"], item["second"]) not in old_pairs]}
