"""Assess optional component costs and pair-specific adjustments in integer units."""

from typing import Any


def prepare_request(request: Any) -> tuple[list[dict], list[dict], list[str], int]:
    if not isinstance(request, dict) or set(request) != {"base_cost", "components", "adjustments", "current"}:
        raise ValueError("invalid request fields")
    if type(request["base_cost"]) is not int:
        raise ValueError("integer base cost required")
    components, adjustments, current = request["components"], request["adjustments"], request["current"]
    if not all(isinstance(value, list) for value in (components, adjustments, current)):
        raise ValueError("lists required")
    names = set()
    for item in components:
        if not isinstance(item, dict) or set(item) != {"name", "cost"}:
            raise ValueError("invalid component")
        name = item["name"]
        if not isinstance(name, str) or not name or name in names or type(item["cost"]) is not int:
            raise ValueError("invalid component name or cost")
        names.add(name)
    for pair in adjustments:
        if not isinstance(pair, dict) or set(pair) != {"members", "cost"}:
            raise ValueError("invalid adjustment")
        members = pair["members"]
        if (not isinstance(members, list) or len(members) != 2
                or any(not isinstance(n, str) or n not in names for n in members)
                or members[0] == members[1] or type(pair["cost"]) is not int):
            raise ValueError("adjustment needs two distinct known components and integer cost")
    if (any(not isinstance(n, str) or n not in names for n in current)
            or len(set(current)) != len(current)):
        raise ValueError("invalid current selection")
    return components, adjustments, current, request["base_cost"]


def describe(components: list[dict], adjustments: list[dict], selected: list[str], base: int) -> dict:
    chosen = set(selected)
    applied = [i for i, pair in enumerate(adjustments) if set(pair["members"]) <= chosen]
    component_cost = sum(c["cost"] for c in components if c["name"] in chosen)
    adjustment_cost = sum(adjustments[i]["cost"] for i in applied)
    return {"selected": [c["name"] for c in components if c["name"] in chosen],
            "component_cost": component_cost, "applied_adjustment_indices": applied,
            "adjustment_cost": adjustment_cost, "total_cost": base + component_cost + adjustment_cost}


def coefficients(components: list[dict], adjustments: list[dict]) -> tuple[list[int], list[tuple[int, int, int]]]:
    indices = {c["name"]: i for i, c in enumerate(components)}
    return [c["cost"] for c in components], [(indices[p["members"][0]], indices[p["members"][1]], p["cost"])
                                            for p in adjustments]


def minimum_energy(biases: list[int], couplings: list[tuple[int, int, int]]) -> int:
    best = None
    for mask in range(1 << len(biases)):
        bits = [(mask >> i) & 1 for i in range(len(biases))]
        value = sum(b * x for b, x in zip(biases, bits))
        value += sum(w * bits[i] * bits[j] for i, j, w in couplings)
        best = value if best is None else min(best, value)
    return best
