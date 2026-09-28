"""Independent subset-list oracle for capacity, optimum, ties and full reports."""

from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path

import pytest
import program


def oracle(request):
    items, capacity = request["items"], request["capacity"]
    feasible = [subset for k in range(len(items)+1) for subset in combinations(range(len(items)), k)
                if sum(items[i]["size"] for i in subset) <= capacity]
    chosen = min(feasible, key=lambda subset: (-sum(items[i]["priority"] for i in subset), subset))
    selected = [items[i]["item_id"] for i in chosen]
    def describe(ids):
        used = sum(item["size"] for item in items if item["item_id"] in ids)
        return {"selected": [i["item_id"] for i in items if i["item_id"] in ids], "used": used,
                "priority": sum(i["priority"] for i in items if i["item_id"] in ids), "feasible": used <= capacity,
                "remaining_capacity": capacity-used}
    return {"item_count": len(items), "capacity": capacity, "current": describe(request["current"]),
            "proposed": describe(selected),
            "changes": {"add": [n for n in selected if n not in request["current"]],
                        "remove": [i["item_id"] for i in items if i["item_id"] in request["current"] and i["item_id"] not in selected]},
            "manifest": [{"item_id": items[i]["item_id"], "offset": sum(items[j]["size"] for j in chosen[:p]),
                          "length": items[i]["size"]} for p, i in enumerate(chosen)]}


def example():
    return json.loads(Path(__file__).with_name("example_request.json").read_text())


def test_bounded_items_capacities_and_all_current_sets():
    item_sets = 0
    for n in range(4):
        for specs in product(((1, 0), (1, 2), (2, 0), (2, 2)), repeat=n):
            items = [{"item_id": f"item-{n-i}", "size": size, "priority": value} for i, (size, value) in enumerate(specs)]
            item_sets += 1
            for capacity in range(sum(i["size"] for i in items)+2):
                for k in range(n+1):
                    for current in combinations([i["item_id"] for i in items], k):
                        request = {"items": items, "capacity": capacity, "current": list(reversed(current))}
                        before = deepcopy(request)
                        assert program.review_archive(request) == oracle(request)
                        assert request == before
    assert item_sets == 85


def test_example_can_replace_infeasible_current_and_tie_is_not_minimum_change():
    request = example()
    report = program.review_archive(request)
    assert report == oracle(request)
    assert report["current"]["feasible"] is False
    assert report["proposed"]["selected"] == ["notes", "index"]
    request = {"items": [{"item_id": "zero", "size": 1, "priority": 0}, {"item_id": "useful", "size": 1, "priority": 2}],
               "capacity": 2, "current": ["useful"]}
    assert program.review_archive(request) == oracle(request)
    assert program.review_archive(request)["proposed"]["selected"] == ["zero", "useful"]
    request["items"][1]["priority"] = 0
    assert program.review_archive(request)["proposed"]["selected"] == []


def test_large_integer_priority_is_exact():
    request = {"items": [{"item_id": "a", "size": 1, "priority": 10**90},
                         {"item_id": "b", "size": 1, "priority": 10**90+1}], "capacity": 1, "current": []}
    assert program.review_archive(request) == oracle(request)
    assert program.review_archive(request)["proposed"]["selected"] == ["b"]


def invalid_requests():
    yield None
    yield {}
    for key, value in [("capacity", -1), ("capacity", True), ("capacity", 1.0), ("items", None), ("current", {}), ("extra", 0)]:
        yield dict(example(), **{key: value})
    for key, value in [("item_id", ""), ("item_id", []), ("size", 0), ("size", True), ("priority", -1), ("priority", False)]:
        request = example()
        request["items"][-1][key] = value
        yield request
    request = example()
    request["items"].append(deepcopy(request["items"][0]))
    yield request
    for current in [["missing"], ["notes", "notes"], [[]]]:
        yield dict(example(), current=current)


@pytest.mark.parametrize("payload", list(invalid_requests()))
def test_full_validation_before_selection(payload, monkeypatch):
    request = payload
    monkeypatch.setattr(program, "select_items", lambda *_: pytest.fail("invalid input reached solver"))
    with pytest.raises(ValueError):
        program.review_archive(request)


@pytest.mark.parametrize("chosen", [(0,), (0, 1, 2), ()])
def test_infeasible_or_suboptimal_substitutes_detected(chosen, monkeypatch):
    monkeypatch.setattr(program, "select_items", lambda *_: chosen)
    assert program.review_archive(example()) != oracle(example())


def test_wrong_tie_and_corrupted_manifest_are_detected(monkeypatch):
    request = {"items": [{"item_id": "a", "size": 1, "priority": 2}, {"item_id": "b", "size": 1, "priority": 2}],
               "capacity": 1, "current": []}
    monkeypatch.setattr(program, "select_items", lambda *_: (1,))
    assert program.review_archive(request) != oracle(request)
    monkeypatch.undo()
    monkeypatch.setattr(program, "transfer_manifest", lambda *_: [])
    assert program.review_archive(example()) != oracle(example())
