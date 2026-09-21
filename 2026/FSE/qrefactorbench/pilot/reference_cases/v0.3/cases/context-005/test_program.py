"""Independent subset-of-lot oracle with filtering, order and validation checks."""

from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path

import pytest
import program


def oracle(request):
    reports = []
    for row in request["requests"]:
        lots = [lot for lot in request["lots"] if lot["site"] in row["sites"] and lot["held"] is False]
        possible = any(sum(lot["units"] for lot in subset) == row["target"]
                       for k in range(len(lots) + 1) for subset in combinations(lots, k))
        reports.append({"request_id": row["request_id"], "target": row["target"],
                        "eligible_lot_ids": [lot["lot_id"] for lot in lots],
                        "available_units": sum(lot["units"] for lot in lots), "exact_capacity_exists": possible})
    return {"lot_count": len(request["lots"]), "requests": reports,
            "possible_request_ids": [r["request_id"] for r in reports if r["exact_capacity_exists"]]}


def example():
    return json.loads(Path(__file__).with_name("example_request.json").read_text())


def test_all_small_inventories_and_capacity_queries():
    count = 0
    for n in range(4):
        for units in product((1, 2, 3), repeat=n):
            for held in product((False, True), repeat=n):
                lots = [{"lot_id": str(i), "units": u, "site": "east" if i % 2 else "west", "held": held[i]}
                        for i, u in enumerate(units)]
                requests = [{"request_id": f"{s}-{t}", "target": t, "sites": sites}
                            for s, sites in enumerate(([], ["east"], ["west", "east"], ["unknown"]))
                            for t in range(sum(units) + 2)]
                request = {"lots": lots, "requests": requests}
                before = deepcopy(request)
                assert program.review_requests(request) == oracle(request)
                assert request == before
                count += 1
    assert count == 259


def test_example_independent_requests_and_no_greedy_shortcut():
    request = example()
    assert program.review_requests(request) == oracle(request)
    assert program.review_requests(request)["possible_request_ids"] == ["six", "six-again", "empty"]
    assert program.review_requests(request)["requests"][2]["available_units"] >= 5
    assert not program.review_requests(request)["requests"][2]["exact_capacity_exists"]


def test_no_added_lot_limit_and_large_exact_integers():
    lots = [{"lot_id": str(i), "units": 10**80, "site": "a", "held": False} for i in range(17)]
    request = {"lots": lots, "requests": [{"request_id": "r", "target": 0, "sites": ["a"]}]}
    assert program.review_requests(request)["possible_request_ids"] == ["r"]
    request["lots"] = lots[:2]
    request["requests"][0]["target"] = 2 * 10**80
    assert program.review_requests(request) == oracle(request)


def invalid_requests():
    yield None
    yield {}
    for key, value in [("lots", None), ("requests", {}), ("extra", 1)]:
        yield dict(example(), **{key: value})
    for key, value in [("units", 0), ("units", True), ("units", -1), ("site", ""), ("held", 1), ("lot_id", [])]:
        request = example()
        request["lots"][-1][key] = value
        yield request
    request = example()
    request["lots"].append(deepcopy(request["lots"][0]))
    yield request
    for key, value in [("target", False), ("target", -1), ("target", 1.5), ("sites", "east"),
                       ("sites", ["east", "east"]), ("sites", [[]]), ("request_id", "")]:
        request = example()
        request["requests"][-1][key] = value
        yield request
    request = example()
    request["requests"].append(deepcopy(request["requests"][0]))
    yield request


@pytest.mark.parametrize("payload", list(invalid_requests()))
def test_validate_entire_input_before_deciding(payload, monkeypatch):
    request = payload
    monkeypatch.setattr(program, "has_total", lambda *_: pytest.fail("solver called before full validation"))
    before = deepcopy(request)
    with pytest.raises(ValueError):
        program.review_requests(request)
    assert request == before


def test_including_held_lots_is_detected(monkeypatch):
    request = {"lots": [{"lot_id": "held", "units": 1, "held": True, "site": "a"}],
               "requests": [{"request_id": "r", "target": 1, "sites": ["a"]}]}
    monkeypatch.setattr(program, "eligible_lots", lambda lots, sites: lots)
    assert program.review_requests(request) != oracle(request)


def test_available_total_is_not_an_existence_test(monkeypatch):
    monkeypatch.setattr(program, "has_total", lambda values, target: sum(values) >= target)
    assert program.review_requests(example()) != oracle(example())
