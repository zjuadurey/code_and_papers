"""Prepare an indivisible archive staging request and its transfer manifest."""

from typing import Any


def prepare_request(request: Any) -> tuple[list[dict], list[str], int]:
    if not isinstance(request, dict) or set(request) != {"items", "current", "capacity"}:
        raise ValueError("invalid request fields")
    items, current, capacity = request["items"], request["current"], request["capacity"]
    if not isinstance(items, list) or not isinstance(current, list) or type(capacity) is not int or capacity < 0:
        raise ValueError("invalid lists or capacity")
    ids = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"item_id", "size", "priority"}:
            raise ValueError("invalid item")
        name = item["item_id"]
        if not isinstance(name, str) or not name or name in ids:
            raise ValueError("unique nonempty item IDs required")
        ids.add(name)
        if (type(item["size"]) is not int or item["size"] <= 0
                or type(item["priority"]) is not int or item["priority"] < 0):
            raise ValueError("positive sizes and nonnegative priorities required")
    if (any(not isinstance(name, str) or name not in ids for name in current)
            or len(set(current)) != len(current)):
        raise ValueError("invalid current IDs")
    return items, current, capacity


def describe(items: list[dict], selected: list[str], capacity: int) -> dict:
    chosen = [item for item in items if item["item_id"] in selected]
    used = sum(item["size"] for item in chosen)
    return {"selected": [item["item_id"] for item in chosen], "used": used,
            "priority": sum(item["priority"] for item in chosen), "feasible": used <= capacity,
            "remaining_capacity": capacity - used}


def transfer_manifest(items: list[dict], selected: list[str]) -> list[dict]:
    offset = 0
    entries = []
    for item in items:
        if item["item_id"] in selected:
            entries.append({"item_id": item["item_id"], "offset": offset, "length": item["size"]})
            offset += item["size"]
    return entries


def select_items(sizes: list[int], values: list[int], capacity: int) -> tuple[int, ...]:
    best: tuple[int, ...] = ()
    best_value = 0
    for mask in range(1 << len(sizes)):
        chosen = tuple(i for i in range(len(sizes)) if mask & (1 << i))
        if sum(sizes[i] for i in chosen) > capacity:
            continue
        value = sum(values[i] for i in chosen)
        if value > best_value or (value == best_value and chosen < best):
            best, best_value = chosen, value
    return best
