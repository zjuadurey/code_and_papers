"""Independent request-level oracle, boundary cases, and integration fault checks."""

from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys

import pytest
import program


def oracle(request):
    names = request["stations"]
    unordered = {frozenset(pair) for pair in request["connections"]}
    pairs = [list(pair) for pair in combinations(names, 2) if frozenset(pair) in unordered]
    valid = []
    for bits in product((False, True), repeat=len(names)):
        choice = {name for name, chosen in zip(names, bits) if chosen}
        if all(choice.intersection(pair) for pair in pairs):
            valid.append(tuple(i for i, chosen in enumerate(bits) if chosen))
    best = min(valid, key=lambda selected: (len(selected), selected))

    def report(chosen):
        owners = [next((name for name in names if name in chosen and name in pair), None)
                  for pair in pairs]
        return {"selected_stations": [name for name in names if name in chosen],
                "selected_count": len(chosen), "covered_connection_count": sum(owner is not None for owner in owners),
                "uncovered_connections": [pair for pair, owner in zip(pairs, owners) if owner is None],
                "checklists": [{"station": name, "connections": [pair for pair, owner in zip(pairs, owners)
                                                                 if owner == name]}
                               for name in names if name in chosen]}, owners

    old, old_owners = report(set(request["current_stations"]))
    new, new_owners = report({names[i] for i in best})
    return {"station_count": len(names), "connection_count": len(pairs), "current": old, "proposed": new,
            "changes": {"add_stations": [name for name in new["selected_stations"] if name not in old["selected_stations"]],
                        "remove_stations": [name for name in old["selected_stations"] if name not in new["selected_stations"]],
                        "selected_count_delta": new["selected_count"] - old["selected_count"],
                        "newly_covered_connections": [pair for pair, a, b in zip(pairs, old_owners, new_owners)
                                                       if a is None and b is not None],
                        "reassigned_connections": [{"connection": pair, "from_station": a, "to_station": b}
                                                   for pair, a, b in zip(pairs, old_owners, new_owners) if a != b]}}


def test_all_small_graphs_and_current_selections():
    checked = 0
    for n in range(5):
        names = [f"s{n-i}" for i in range(n)]  # Input order differs from lexical order.
        pairs = list(combinations(names, 2))
        for edge_bits in product((False, True), repeat=len(pairs)):
            edges = [list(pair) for pair, present in zip(pairs, edge_bits) if present]
            for current_bits in product((False, True), repeat=n):
                request = {"stations": names, "connections": edges,
                           "current_stations": [name for name, chosen in zip(names, current_bits) if chosen][::-1]}
                before = deepcopy(request)
                assert program.review_inspections(request) == oracle(request)
                assert request == before
                checked += 1
    assert checked == 1099


def test_example_deactivations_and_task_transfer():
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    report = program.review_inspections(request)
    assert report == oracle(request)
    assert report["proposed"]["selected_stations"] == ["north", "west"]
    assert report["changes"]["remove_stations"] == ["south", "east"]
    assert report["changes"]["reassigned_connections"] == [
        {"connection": ["south", "west"], "from_station": "south", "to_station": "west"}]


def test_current_gaps_can_require_more_stations():
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    request["current_stations"] = ["north"]
    report = program.review_inspections(request)
    assert report == oracle(request)
    assert report["changes"]["selected_count_delta"] == 1
    assert report["changes"]["newly_covered_connections"] == [["south", "west"], ["west", "east"]]
    assert all(row["from_station"] is None for row in report["changes"]["reassigned_connections"])


@pytest.mark.parametrize("n", [0, 1, 7, 16])
def test_empty_connections_and_full_input_boundary(n):
    names = [str(i) for i in range(n)]
    request = {"stations": names, "connections": [], "current_stations": names[::-1]}
    result = program.review_inspections(request)
    assert result["proposed"]["selected_stations"] == []
    assert result["changes"]["remove_stations"] == names
    assert all(row["connections"] == [] for row in result["current"]["checklists"])


def invalid_requests():
    valid = {"stations": ["z", "a"], "connections": [["z", "a"]], "current_stations": []}
    yield None
    yield []
    yield {}
    yield dict(valid, extra=True)
    for names in [None, "za", ["z", "z"], [""], [False], list(map(str, range(17)))]:
        yield dict(valid, stations=names)
    for edges in [None, "za", [["z"]], [["z", "a", "z"]], [["z", "z"]], [["z", "unknown"]],
                  [["z", []]], [["z", "a"], ["z", "unknown"]]]:
        yield dict(valid, connections=edges)
    for selected in [None, "z", ["unknown"], ["z", "z"], [[]], [False]]:
        yield dict(valid, current_stations=selected)
    yield {"stations": [], "connections": [], "current_stations": ["unknown"]}


@pytest.mark.parametrize("request_data", list(invalid_requests()))
def test_reject_invalid_before_solver(request_data, monkeypatch):
    monkeypatch.setattr(program, "min_vertex_cover_bruteforce", lambda *_: pytest.fail("Validation must finish first"))
    before = deepcopy(request_data)
    with pytest.raises(ValueError):
        program.review_inspections(request_data)
    assert request_data == before


@pytest.mark.parametrize("selected", [{0, 1}, {1}, set()])
def test_oracle_detects_feasible_nonminimal_wrong_tie_and_uncovered_outputs(selected, monkeypatch):
    request = {"stations": ["z", "a"], "connections": [["z", "a"]], "current_stations": []}
    monkeypatch.setattr(program, "min_vertex_cover_bruteforce", lambda *_: selected)
    assert program.review_inspections(request) != oracle(request)


def test_objective_only_check_misses_corrupt_checklists(monkeypatch):
    request = {"stations": ["z", "a"], "connections": [["z", "a"]], "current_stations": ["z"]}
    real = program.describe_plan

    def corrupt(*args):
        result = real(*args)
        for row in result["checklists"]:
            row["connections"] = []
        return result

    monkeypatch.setattr(program, "describe_plan", corrupt)
    report = program.review_inspections(request)
    assert report["proposed"]["selected_count"] == oracle(request)["proposed"]["selected_count"]
    assert report != oracle(request)


def test_cli_valid_and_invalid():
    request = Path(__file__).with_name("example_request.json").read_text()
    command = [sys.executable, str(Path(__file__).with_name("program.py"))]
    result = subprocess.run(command, input=request, text=True, capture_output=True, check=True)
    assert json.loads(result.stdout) == oracle(json.loads(request))
    failure = subprocess.run(command, input='{}', text=True, capture_output=True)
    assert failure.returncode != 0 and not failure.stdout.strip()
