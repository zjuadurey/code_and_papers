"""Check feasibility, exact size, stable ties and the surrounding API separately."""

from copy import deepcopy
from itertools import combinations, product

import pytest

from program import inspection_plan


def oracle(request):
    names = request["stations"]
    eligible = []
    for bits in product((False, True), repeat=len(names)):
        chosen = {name for name, bit in zip(names, bits) if bit}
        if all(u in chosen or v in chosen for u, v in request["connections"]):
            indices = tuple(i for i, bit in enumerate(bits) if bit)
            eligible.append((len(indices), indices))
    count, indices = min(eligible)
    connections = {frozenset(pair) for pair in request["connections"]}
    return {"selected_stations": [names[i] for i in indices],
            "station_count": count, "connection_count": len(connections)}


@pytest.mark.parametrize("n", range(5))
def test_all_small_graphs(n):
    names = [f"station-{i}" for i in range(n)]
    pairs = list(combinations(names, 2))
    for present in product((False, True), repeat=len(pairs)):
        request = {"stations": names, "connections": [list(pair)
                   for pair, include in zip(pairs, present) if include]}
        result = inspection_plan(request)
        chosen = set(result["selected_stations"])
        assert all(u in chosen or v in chosen for u, v in request["connections"])
        assert result == oracle(request)


def test_duplicates_reversal_order_and_no_mutation():
    request = {"stations": ["z", "a", "isolated"],
               "connections": [["z", "a"], ["a", "z"], ["z", "a"]]}
    before = deepcopy(request)
    assert inspection_plan(request) == {"selected_stations": ["z"],
                                        "station_count": 1, "connection_count": 1}
    assert request == before


def test_tie_is_by_input_position_not_name():
    request = {"stations": ["z", "a", "m"],
               "connections": [["z", "a"], ["a", "m"], ["z", "m"]]}
    assert inspection_plan(request)["selected_stations"] == ["z", "a"]


@pytest.mark.parametrize("payload", [
    None, {}, {"stations": ["a", "a"], "connections": []},
    {"stations": [""], "connections": []}, {"stations": [[]], "connections": []},
    {"stations": [str(i) for i in range(17)], "connections": []},
    {"stations": [], "connections": {}},
    {"stations": ["a"], "connections": [["a", "a"]]},
    {"stations": ["a"], "connections": [["a", "missing"]]},
    {"stations": ["a"], "connections": [[[], "a"]]},
    {"stations": ["a"], "connections": [["a"]]},
    {"stations": ["a"], "connections": [("a", "a")]},
    {"stations": [], "connections": [], "extra": 1},
])
def test_invalid_inputs_raise_value_error_without_mutation(payload):
    before = deepcopy(payload)
    with pytest.raises(ValueError):
        inspection_plan(payload)
    assert payload == before


def test_valid_prefix_does_not_hide_invalid_suffix():
    with pytest.raises(ValueError):
        inspection_plan({"stations": ["a", "b"],
                         "connections": [["a", "b"], ["a", "missing"]]})


def test_empty_connections_select_nothing():
    assert inspection_plan({"stations": ["a"], "connections": []}) == {
        "selected_stations": [], "station_count": 0, "connection_count": 0}
