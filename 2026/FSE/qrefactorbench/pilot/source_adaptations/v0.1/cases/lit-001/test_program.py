"""Classical contract tests, not quantumization ground truth."""

from copy import deepcopy
from itertools import combinations, product

import pytest

from program import schedule


def oracle(request):
    names = request["equipment"]
    candidates = []
    for bits in product((0, 1), repeat=len(names)):
        assigned = dict(zip(names, bits))
        value = sum(e["weight"] for e in request["requirements"]
                    if assigned[e["first"]] != assigned[e["second"]])
        identifier = sum(bit * 2**i for i, bit in enumerate(bits))
        candidates.append((-value, identifier, bits))
    negative, _, bits = min(candidates)
    return {"separated_weight": -negative,
            "windows": [[name for name, bit in zip(names, bits) if bit == group]
                        for group in (1, 0)], "equipment_count": len(names)}


def test_duplicate_weights_names_and_no_mutation():
    request = {"equipment": ["z", "a", "m"], "requirements": [
        {"first": "z", "second": "a", "weight": 2},
        {"first": "a", "second": "z", "weight": 3},
        {"first": "a", "second": "m", "weight": 1}]}
    before = deepcopy(request)
    assert schedule(request) == {"separated_weight": 6,
                                 "windows": [["a"], ["z", "m"]], "equipment_count": 3}
    assert request == before


@pytest.mark.parametrize("n", range(5))
def test_all_small_unweighted_graphs(n):
    names = [f"device-{i}" for i in range(n)]
    pairs = list(combinations(names, 2))
    for present in product((False, True), repeat=len(pairs)):
        request = {"equipment": names, "requirements": [
            {"first": u, "second": v, "weight": 1}
            for (u, v), include in zip(pairs, present) if include]}
        assert schedule(request) == oracle(request)


def test_weighted_triangles():
    pairs = [("z", "a"), ("a", "m"), ("z", "m")]
    for weights in product((0, 1, 3), repeat=3):
        request = {"equipment": ["z", "a", "m"], "requirements": [
            {"first": u, "second": v, "weight": w} for (u, v), w in zip(pairs, weights)]}
        assert schedule(request) == oracle(request)


@pytest.mark.parametrize("payload", [
    None, {}, {"equipment": ["a", "a"], "requirements": []},
    {"equipment": [""], "requirements": []},
    {"equipment": [[]], "requirements": []},
    {"equipment": [str(i) for i in range(17)], "requirements": []},
    {"equipment": [], "requirements": {}},
    {"equipment": ["a", "b"], "requirements": [{"first": "a", "second": "b", "weight": True}]},
    {"equipment": ["a", "b"], "requirements": [{"first": "a", "second": "b", "weight": -1}]},
    {"equipment": ["a", "b"], "requirements": [{"first": "a", "second": "b", "weight": 1.0}]},
    {"equipment": ["a"], "requirements": [{"first": "a", "second": "a", "weight": 1}]},
    {"equipment": ["a"], "requirements": [{"first": "a", "second": "missing", "weight": 0}]},
    {"equipment": ["a"], "requirements": [{"first": [], "second": "a", "weight": 1}]},
    {"equipment": ["a"], "requirements": [{"first": "a"}]},
    {"equipment": [], "requirements": [], "extra": 1},
])
def test_invalid_inputs_raise_value_error_without_mutation(payload):
    before = deepcopy(payload)
    with pytest.raises(ValueError):
        schedule(payload)
    assert payload == before


def test_valid_prefix_does_not_hide_invalid_suffix():
    with pytest.raises(ValueError):
        schedule({"equipment": ["a", "b"], "requirements": [
            {"first": "a", "second": "b", "weight": 1},
            {"first": "a", "second": "missing", "weight": 0}]})


def test_zero_weight_tie_keeps_all_equipment_in_second_window():
    assert schedule({"equipment": ["b", "a"], "requirements": []}) == {
        "separated_weight": 0, "windows": [[], ["b", "a"]], "equipment_count": 2}
