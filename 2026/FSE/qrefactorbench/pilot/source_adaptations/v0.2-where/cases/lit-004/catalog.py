"""Validate independent release requests and construct the latest pair-status view."""

from typing import Any


def prepare(request: Any) -> tuple[list[dict], list[dict], list[dict]]:
    if not isinstance(request, dict) or set(request) != {"versions", "checks", "requests"}:
        raise ValueError("invalid request fields")
    versions, checks, requests = (request[k] for k in ("versions", "checks", "requests"))
    if not all(isinstance(x, list) for x in (versions, checks, requests)):
        raise ValueError("lists required")
    names = set()
    for version in versions:
        if (not isinstance(version, dict) or set(version) != {"version_id", "active"}
                or not isinstance(version["version_id"], str) or not version["version_id"]
                or version["version_id"] in names or type(version["active"]) is not bool):
            raise ValueError("invalid version")
        names.add(version["version_id"])
    for check in checks:
        if (not isinstance(check, dict) or set(check) != {"left", "right", "passed"}
                or any(not isinstance(check[n], str) or check[n] not in names for n in ("left", "right"))
                or check["left"] == check["right"] or type(check["passed"]) is not bool):
            raise ValueError("invalid check")
    ids = set()
    for row in requests:
        if (not isinstance(row, dict) or set(row) != {"request_id", "members", "current", "mode"}
                or not isinstance(row["request_id"], str) or not row["request_id"] or row["request_id"] in ids
                or row["mode"] not in ("inspect", "select")):
            raise ValueError("invalid selection request")
        ids.add(row["request_id"])
        for key in ("members", "current"):
            values = row[key]
            if (not isinstance(values, list) or any(not isinstance(v, str) or v not in names for v in values)
                    or len(set(values)) != len(values)):
                raise ValueError("invalid request members")
        if not set(row["current"]) <= set(row["members"]):
            raise ValueError("current must belong to request members")
    return versions, checks, requests


def latest_results(checks: list[dict]) -> dict[frozenset[str], bool]:
    latest = {}
    for check in checks:
        latest[frozenset((check["left"], check["right"]))] = check["passed"]
    return latest


def eligible(versions: list[dict], members: list[str]) -> list[str]:
    return [v["version_id"] for v in versions if v["active"] and v["version_id"] in members]
