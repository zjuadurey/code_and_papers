"""Enumerate named catalogue subsets independently of the coefficient compiler."""

from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path

import pytest
import program


def oracle(request):
    names = [c["name"] for c in request["components"]]
    def describe(selected):
        costs = sum(c["cost"] for c in request["components"] if c["name"] in selected)
        applied = [i for i, p in enumerate(request["adjustments"]) if all(n in selected for n in p["members"])]
        adjustment = sum(request["adjustments"][i]["cost"] for i in applied)
        return {"selected": [n for n in names if n in selected], "component_cost": costs,
                "applied_adjustment_indices": applied, "adjustment_cost": adjustment,
                "total_cost": request["base_cost"] + costs + adjustment}
    lowest = min(describe(subset)["total_cost"] for k in range(len(names)+1) for subset in combinations(names, k))
    current = describe(request["current"])
    return {"component_count": len(names), "base_cost": request["base_cost"], "current": current,
            "lowest_cost": lowest, "avoidable_cost": current["total_cost"]-lowest}


def example():
    return json.loads(Path(__file__).with_name("example_request.json").read_text())


def test_small_catalogues_and_every_current_selection():
    catalogues = comparisons = 0
    for n in range(4):
        names = [f"part-{n-i}" for i in range(n)]
        pairs = list(combinations(names, 2))
        for costs in product((-1, 2), repeat=n):
            for adjustments in product((-3, 0, 2), repeat=len(pairs)):
                catalogues += 1
                request = {"base_cost": 17, "components": [{"name": name, "cost": cost} for name, cost in zip(names, costs)],
                           "adjustments": [{"members": list(pair), "cost": cost} for pair, cost in zip(pairs, adjustments)],
                           "current": []}
                for k in range(n+1):
                    for chosen in combinations(names, k):
                        request["current"] = list(reversed(chosen))
                        before = deepcopy(request)
                        assert program.review_package(request) == oracle(request)
                        assert request == before
                        comparisons += 1
    assert (catalogues, comparisons) == (231, 1781)


def test_example_duplicate_reversed_adjustments_and_signed_large_costs():
    request = example()
    assert program.review_package(request) == oracle(request)
    assert program.review_package(request)["lowest_cost"] == 97
    request["base_cost"] = -(10**100)
    request["components"][0]["cost"] = 10**90
    request["adjustments"].append({"members": ["telemetry", "cache"], "cost": -(10**91)})
    assert program.review_package(request) == oracle(request)


def invalid_requests():
    yield None
    yield {}
    for key, value in [("base_cost", True), ("components", {}), ("adjustments", None), ("current", "cache"), ("extra", 1)]:
        yield dict(example(), **{key: value})
    for key, value in [("name", ""), ("name", []), ("cost", 0.5), ("cost", False)]:
        request = example()
        request["components"][-1][key] = value
        yield request
    request = example()
    request["components"].append(deepcopy(request["components"][0]))
    yield request
    for members in [[], ["cache"], ["cache", "cache"], ["cache", "unknown"], [[], "cache"]]:
        request = example()
        request["adjustments"][-1]["members"] = members
        yield request
    for current in [["unknown"], ["cache", "cache"], [[]]]:
        yield dict(example(), current=current)
    request = example()
    request["adjustments"].append({"members": ["cache", "telemetry"], "cost": True})
    yield request


@pytest.mark.parametrize("payload", list(invalid_requests()))
def test_full_validation_precedes_solver(payload, monkeypatch):
    request = payload
    monkeypatch.setattr(program, "minimum_energy", lambda *_: pytest.fail("invalid request reached solver"))
    with pytest.raises(ValueError):
        program.review_package(request)


def test_dropped_adjustments_are_detected(monkeypatch):
    monkeypatch.setattr(program, "coefficients", lambda components, adjustments: ([c["cost"] for c in components], []))
    assert program.review_package(example()) != oracle(example())


def test_negative_avoidable_cost_is_not_permitted_by_correct_contract(monkeypatch):
    monkeypatch.setattr(program, "minimum_energy", lambda *_: 1000)
    assert program.review_package(example()) != oracle(example())
