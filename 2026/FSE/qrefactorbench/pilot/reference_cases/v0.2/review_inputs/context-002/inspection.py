"""Validation, coverage assessment, worklists and changes for endpoint inspections."""

import itertools
from typing import Any


def prepare_request(request: Any) -> tuple[list[str], list[tuple[int, int]], set[int]]:
    """Read all fields; an incomplete current coverage is legal and must be reported."""
    if not isinstance(request, dict) or set(request) != {"stations", "connections", "current_stations"}:
        raise ValueError("Expected stations, connections and current_stations")
    names = request["stations"]
    if not isinstance(names, list) or len(names) > 16:
        raise ValueError("stations must be a list of at most 16 names")
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError("Station names must be unique nonempty strings")
    index = {name: i for i, name in enumerate(names)}
    connections = request["connections"]
    if not isinstance(connections, list):
        raise ValueError("connections must be a list")
    edges = set()
    for pair in connections:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("Connections require two endpoints")
        first, second = pair
        if not isinstance(first, str) or not isinstance(second, str):
            raise ValueError("Endpoints must be names")
        if first not in index or second not in index or first == second:
            raise ValueError("Endpoints must be distinct known stations")
        edges.add(tuple(sorted((index[first], index[second]))))
    current = request["current_stations"]
    if not isinstance(current, list):
        raise ValueError("current_stations must be a list")
    selected = set()
    for name in current:
        if not isinstance(name, str) or name not in index or index[name] in selected:
            raise ValueError("Current stations must be distinct known names")
        selected.add(index[name])
    return list(names), sorted(edges), selected


def describe_plan(names: list[str], edges: list[tuple[int, int]], selected: set[int]) -> dict[str, Any]:
    """Assign each covered connection once to its earliest selected endpoint."""
    assigned = {i: [] for i in sorted(selected)}
    uncovered = []
    for u, v in edges:
        pair = [names[u], names[v]]
        if u in selected:
            assigned[u].append(pair)
        elif v in selected:
            assigned[v].append(pair)
        else:
            uncovered.append(pair)
    return {"selected_stations": [names[i] for i in sorted(selected)],
            "selected_count": len(selected), "covered_connection_count": len(edges) - len(uncovered),
            "uncovered_connections": uncovered,
            "checklists": [{"station": names[i], "connections": pairs} for i, pairs in assigned.items()]}


def compare_plans(names: list[str], edges: list[tuple[int, int]], current: dict, proposed: dict) -> dict:
    """Describe station activation and connection responsibility changes independently."""
    old_set, new_set = set(current["selected_stations"]), set(proposed["selected_stations"])

    def owners(plan: dict) -> dict:
        return {tuple(pair): row["station"] for row in plan["checklists"] for pair in row["connections"]}

    old, new = owners(current), owners(proposed)
    pairs = [(names[u], names[v]) for u, v in edges]
    return {"add_stations": [name for name in names if name in new_set - old_set],
            "remove_stations": [name for name in names if name in old_set - new_set],
            "selected_count_delta": len(new_set) - len(old_set),
            "newly_covered_connections": [list(pair) for pair in pairs if pair not in old and pair in new],
            "reassigned_connections": [{"connection": list(pair), "from_station": old.get(pair),
                                        "to_station": new.get(pair)}
                                       for pair in pairs if old.get(pair) != new.get(pair)]}


def min_vertex_cover_bruteforce(edges, n):
    nodes = list(range(n))
    best_cover = None
    for r in range(n + 1):
        for subset in itertools.combinations(nodes, r):
            cover = set(subset)
            ok = True
            for u, v in edges:
                if u not in cover and v not in cover:
                    ok = False
                    break
            if ok:
                best_cover = cover
                return best_cover
    return best_cover
