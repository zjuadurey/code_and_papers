"""Choose endpoint inspection stations for all declared connections."""

import json
import sys
from typing import Any

from kernel import min_vertex_cover_bruteforce


def prepare_request(request: Any) -> tuple[list[str], list[tuple[int, int]]]:
    """Validate named connections and merge duplicate undirected declarations."""
    if not isinstance(request, dict) or set(request) != {"stations", "connections"}:
        raise ValueError("Expected stations and connections")
    names, connections = request["stations"], request["connections"]
    if not isinstance(names, list) or len(names) > 16:
        raise ValueError("stations must be a list of at most 16 names")
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError("station names must be unique nonempty strings")
    if not isinstance(connections, list):
        raise ValueError("connections must be a list")
    index = {name: i for i, name in enumerate(names)}
    edges = set()
    for pair in connections:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("A connection must be a two-name list")
        first, second = pair
        if not isinstance(first, str) or not isinstance(second, str):
            raise ValueError("Connection endpoints must be names")
        if first not in index or second not in index or first == second:
            raise ValueError("Connection endpoints must be distinct known stations")
        edges.add(tuple(sorted((index[first], index[second]))))
    return list(names), sorted(edges)


def inspection_plan(request: Any) -> dict[str, Any]:
    """Return the fewest stations touching every connection, with stable ties."""
    names, edges = prepare_request(request)
    selected = min_vertex_cover_bruteforce(edges, len(names))
    return {"selected_stations": [name for i, name in enumerate(names) if i in selected],
            "station_count": len(selected), "connection_count": len(edges)}


if __name__ == "__main__":
    print(json.dumps(inspection_plan(json.load(sys.stdin))))
