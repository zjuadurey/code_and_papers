"""Validate indivisible lots and report exact capacity requests independently."""

from typing import Any


def prepare_request(request: Any) -> tuple[list[dict], list[dict]]:
    if not isinstance(request, dict) or set(request) != {"lots", "requests"}:
        raise ValueError("expected lots and requests")
    lots, requests = request["lots"], request["requests"]
    if not isinstance(lots, list) or not isinstance(requests, list):
        raise ValueError("lists required")
    ids = set()
    for lot in lots:
        if not isinstance(lot, dict) or set(lot) != {"lot_id", "units", "site", "held"}:
            raise ValueError("invalid lot")
        if not isinstance(lot["lot_id"], str) or not lot["lot_id"] or lot["lot_id"] in ids:
            raise ValueError("unique nonempty lot ID required")
        ids.add(lot["lot_id"])
        if type(lot["units"]) is not int or lot["units"] <= 0:
            raise ValueError("positive whole units required")
        if not isinstance(lot["site"], str) or not lot["site"] or type(lot["held"]) is not bool:
            raise ValueError("invalid site or held flag")
    ids = set()
    for row in requests:
        if not isinstance(row, dict) or set(row) != {"request_id", "target", "sites"}:
            raise ValueError("invalid request")
        if not isinstance(row["request_id"], str) or not row["request_id"] or row["request_id"] in ids:
            raise ValueError("unique nonempty request ID required")
        ids.add(row["request_id"])
        if type(row["target"]) is not int or row["target"] < 0:
            raise ValueError("nonnegative whole target required")
        sites = row["sites"]
        if (not isinstance(sites, list) or any(not isinstance(s, str) or not s for s in sites)
                or len(set(sites)) != len(sites)):
            raise ValueError("distinct nonempty site names required")
    return lots, requests


def eligible_lots(lots: list[dict], sites: list[str]) -> list[dict]:
    return [lot for lot in lots if not lot["held"] and lot["site"] in sites]


def has_total(values: list[int], target: int) -> bool:
    for mask in range(1 << len(values)):
        total = sum(value for index, value in enumerate(values)
                    if mask & (1 << index))
        if total == target:
            return True
    return False


def describe(row: dict, eligible: list[dict], possible: bool) -> dict:
    return {"request_id": row["request_id"], "target": row["target"],
            "eligible_lot_ids": [lot["lot_id"] for lot in eligible],
            "available_units": sum(lot["units"] for lot in eligible),
            "exact_capacity_exists": possible}
