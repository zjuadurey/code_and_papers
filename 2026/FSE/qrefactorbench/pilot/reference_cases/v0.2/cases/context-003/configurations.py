"""Validate named configuration rules and assess partial profile requests."""

from typing import Any


def prepare_request(request: Any) -> tuple[list[str], list[list[int]], list[dict]]:
    """Validate every rule/profile before assessing any profile."""
    required = {"features", "requires", "excludes", "at_least_one", "profiles"}
    if not isinstance(request, dict) or set(request) != required:
        raise ValueError("Expected features, requires, excludes, at_least_one, profiles")
    names = request["features"]
    if not isinstance(names, list) or any(not isinstance(n, str) or not n for n in names):
        raise ValueError("features must contain nonempty strings")
    if len(set(names)) != len(names):
        raise ValueError("Feature names must be unique")
    index = {name: i + 1 for i, name in enumerate(names)}
    clauses = []
    for kind in ("requires", "excludes"):
        if not isinstance(request[kind], list):
            raise ValueError("Pair rules must be lists")
        for pair in request[kind]:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError("Pair rules need two features")
            if any(not isinstance(name, str) or name not in index for name in pair):
                raise ValueError("Rule references an unknown feature")
            first, second = (index[name] for name in pair)
            clauses.append([-first, second] if kind == "requires" else [-first, -second])
    if not isinstance(request["at_least_one"], list):
        raise ValueError("at_least_one must be a list")
    for group in request["at_least_one"]:
        if not isinstance(group, list) or any(not isinstance(name, str) or name not in index for name in group):
            raise ValueError("Group references an unknown feature")
        clauses.append([index[name] for name in group])
    if not isinstance(request["profiles"], list):
        raise ValueError("profiles must be a list")
    profiles, seen = [], set()
    for profile in request["profiles"]:
        if not isinstance(profile, dict) or set(profile) != {"profile_id", "enabled", "disabled"}:
            raise ValueError("Profiles need profile_id, enabled and disabled")
        identifier = profile["profile_id"]
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("Profile IDs must be unique nonempty strings")
        seen.add(identifier)
        selected = {}
        for field in ("enabled", "disabled"):
            values = profile[field]
            if not isinstance(values, list) or any(not isinstance(name, str) or name not in index for name in values):
                raise ValueError("Profile references an unknown feature")
            if len(set(values)) != len(values):
                raise ValueError("Profile feature selections must be unique")
            selected[field] = set(values)
        if selected["enabled"] & selected["disabled"]:
            raise ValueError("A feature cannot be fixed both ways")
        profiles.append({"profile_id": identifier,
                         "enabled": [name for name in names if name in selected["enabled"]],
                         "disabled": [name for name in names if name in selected["disabled"]]})
    return list(names), clauses, profiles


def clauses_for_profile(names: list[str], clauses: list[list[int]], profile: dict) -> list[list[int]]:
    positions = {name: i + 1 for i, name in enumerate(names)}
    return [list(clause) for clause in clauses] + [[positions[name]] for name in profile["enabled"]] + [
        [-positions[name]] for name in profile["disabled"]]


def describe_profile(names: list[str], profile: dict, completion_exists: bool) -> dict:
    fixed = set(profile["enabled"]) | set(profile["disabled"])
    return {**profile, "unfixed_features": [name for name in names if name not in fixed],
            "completion_exists": completion_exists}


def satisfies(mask: int, clauses: list[list[int]]) -> bool:
    return all(
        any(bool(mask & (1 << (abs(literal) - 1))) == (literal > 0)
            for literal in clause)
        for clause in clauses
    )


def has_assignment(n: int, clauses: list[list[int]]) -> bool:
    for mask in range(1 << n):
        if satisfies(mask, clauses):
            return True
    return False
