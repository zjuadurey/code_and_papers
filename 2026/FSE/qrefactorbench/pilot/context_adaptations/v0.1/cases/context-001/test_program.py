"""Full API checks with an independent named-request oracle; no quantum claims."""

from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys

import pytest

import maintenance
from program import review_schedule


def oracle(request):
    """Use raw requirements and Cartesian products, not production matrix/helpers."""
    names = request["equipment"]
    options = []
    for bits in product((0, 1), repeat=len(names)):
        assigned = dict(zip(names, bits))
        cost = sum(item["weight"] for item in request["requirements"]
                   if assigned[item["first"]] == assigned[item["second"]])
        mask = sum(bit * 2**i for i, bit in enumerate(bits))
        options.append((cost, mask, bits))
    _, _, chosen = min(options)
    old = {name: group for group, window in enumerate(request["current_windows"]) for name in window}
    new = {name: 0 if bit else 1 for name, bit in zip(names, chosen)}

    def describe(assignment):
        conflicts = []
        for first, second in combinations(names, 2):
            weight = sum(item["weight"] for item in request["requirements"]
                         if {item["first"], item["second"]} == {first, second})
            if weight and assignment[first] == assignment[second]:
                conflicts.append({"first": first, "second": second, "weight": weight})
        cost = sum(item["weight"] for item in conflicts)
        return {"windows": [[name for name in names if assignment[name] == group] for group in (0, 1)],
                "conflict_weight": cost,
                "separated_weight": sum(item["weight"] for item in request["requirements"]) - cost,
                "conflicts": conflicts}

    current, proposed = describe(old), describe(new)
    return {"equipment_count": len(names), "requirement_count": len(request["requirements"]),
            "current": current, "proposed": proposed,
            "changes": {
                "moved_equipment": [{"equipment": name, "from_window": old[name], "to_window": new[name]}
                                    for name in names if old[name] != new[name]],
                "conflict_reduction": current["conflict_weight"] - proposed["conflict_weight"],
                "resolved_conflicts": [item for item in current["conflicts"] if item not in proposed["conflicts"]],
                "introduced_conflicts": [item for item in proposed["conflicts"] if item not in current["conflicts"]]}}


def test_example_full_report():
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    before = deepcopy(request)
    result = review_schedule(request)
    assert result == oracle(request)
    assert result["current"]["conflict_weight"] == 8
    assert result["proposed"]["windows"] == [["fan"], ["pump", "chiller"]]
    assert result["proposed"]["conflict_weight"] == 1
    assert result["changes"]["conflict_reduction"] == 7
    assert [item["equipment"] for item in result["changes"]["moved_equipment"]] == ["pump", "chiller"]
    assert request == before


@pytest.mark.parametrize("n", range(5))
def test_all_small_graphs_and_all_current_assignments(n):
    names = [f"equipment-{i}" for i in range(n)]
    pairs = list(combinations(names, 2))
    for present in product((False, True), repeat=len(pairs)):
        requirements = [{"first": u, "second": v, "weight": 1}
                        for (u, v), include in zip(pairs, present) if include]
        for current_bits in product((0, 1), repeat=n):
            request = {"equipment": names, "requirements": requirements,
                       "current_windows": [[name for name, bit in zip(names, current_bits) if bit == group]
                                           for group in (0, 1)]}
            before = deepcopy(request)
            assert review_schedule(request) == oracle(request)
            assert request == before


def test_weighted_duplicate_reversed_requirements_and_current_order():
    for weights in product((0, 1, 3), repeat=3):
        request = {"equipment": ["z", "a", "m"], "requirements": [
            {"first": "z", "second": "a", "weight": weights[0]},
            {"first": "a", "second": "z", "weight": weights[1]},
            {"first": "a", "second": "m", "weight": weights[2]}],
            "current_windows": [["m", "z"], ["a"]]}
        assert review_schedule(request) == oracle(request)


def test_improvement_can_introduce_a_lower_weight_conflict():
    request = {"equipment": ["a", "b", "c"], "requirements": [
        {"first": "a", "second": "b", "weight": 5},
        {"first": "b", "second": "c", "weight": 4},
        {"first": "a", "second": "c", "weight": 1}],
        "current_windows": [["a", "b"], ["c"]]}
    result = review_schedule(request)
    assert result == oracle(request)
    assert result["changes"]["conflict_reduction"] == 4
    assert result["changes"]["introduced_conflicts"] == [{"first": "a", "second": "c", "weight": 1}]


def test_optimal_current_can_move_due_to_inherited_tie_rule():
    request = {"equipment": ["a", "b"],
               "requirements": [{"first": "a", "second": "b", "weight": 3}],
               "current_windows": [["b"], ["a"]]}
    result = review_schedule(request)
    assert result == oracle(request)
    assert result["changes"]["conflict_reduction"] == 0
    assert len(result["changes"]["moved_equipment"]) == 2


def test_no_edges_and_empty_input():
    for names in ([], ["z", "a"]):
        request = {"equipment": names, "requirements": [], "current_windows": [list(names), []]}
        result = review_schedule(request)
        assert result == oracle(request)
        assert result["proposed"]["windows"] == [[], names]


@pytest.mark.parametrize("bad_windows", [
    None, [], [["a", "b"]], [["a"], ["b"], []], ["a", ["b"]],
    [["a"], []], [["a"], ["a", "b"]], [["a", "a"], ["b"]],
    [["a"], ["unknown"]], [["a"], [1]], [["a"], [[]]],
])
def test_invalid_current_assignments(bad_windows):
    payload = {"equipment": ["a", "b"], "requirements": [], "current_windows": bad_windows}
    before = deepcopy(payload)
    with pytest.raises(ValueError):
        review_schedule(payload)
    assert payload == before


@pytest.mark.parametrize("bad_requirement", [
    None, {}, {"first": "a", "second": "b", "weight": True},
    {"first": "a", "second": "b", "weight": -1},
    {"first": "a", "second": "b", "weight": 1.0},
    {"first": "a", "second": "a", "weight": 1},
    {"first": "a", "second": "missing", "weight": 0},
    {"first": [], "second": "b", "weight": 1},
    {"first": "a", "second": "b", "weight": 1, "extra": 0},
])
def test_invalid_requirement_after_valid_prefix(bad_requirement):
    payload = {"equipment": ["a", "b"], "requirements": [
        {"first": "a", "second": "b", "weight": 2}, bad_requirement],
        "current_windows": [["a"], ["b"]]}
    before = deepcopy(payload)
    with pytest.raises(ValueError):
        review_schedule(payload)
    assert payload == before


@pytest.mark.parametrize("payload", [
    None, {}, {"equipment": [], "requirements": [], "current_windows": [[], []], "extra": 1},
    {"equipment": ["a", "a"], "requirements": [], "current_windows": [[], []]},
    {"equipment": [""], "requirements": [], "current_windows": [[], []]},
    {"equipment": [[]], "requirements": [], "current_windows": [[], []]},
    {"equipment": "a", "requirements": [], "current_windows": [[], []]},
    {"equipment": list(map(str, range(17))), "requirements": [], "current_windows": [[], []]},
    {"equipment": [], "requirements": {}, "current_windows": [[], []]},
])
def test_invalid_request(payload):
    with pytest.raises(ValueError):
        review_schedule(payload)


def test_upper_bound_validation_and_large_exact_weights():
    names = list(map(str, range(16)))
    maintenance.prepare_request({"equipment": names, "requirements": [], "current_windows": [names, []]})
    request = {"equipment": ["a", "b"], "requirements": [
        {"first": "a", "second": "b", "weight": 10**40}], "current_windows": [["a", "b"], []]}
    assert review_schedule(request) == oracle(request)


def test_result_does_not_alias_request():
    request = {"equipment": ["a", "b"], "requirements": [
        {"first": "a", "second": "b", "weight": 3}], "current_windows": [["a", "b"], []]}
    before = deepcopy(request)
    result = review_schedule(request)
    result["current"]["windows"][0].clear()
    result["current"]["conflicts"][0]["weight"] = -1
    assert request == before


def test_reporting_mutant_detected(monkeypatch):
    request = {"equipment": ["a", "b"], "requirements": [
        {"first": "a", "second": "b", "weight": 3}], "current_windows": [["a", "b"], []]}
    import program
    original = program.compare_assignments

    def omit_moves(*args):
        result = original(*args)
        result["moved_equipment"] = []
        return result

    monkeypatch.setattr(program, "compare_assignments", omit_moves)
    wrong = review_schedule(request)
    expected = oracle(request)
    assert wrong["proposed"]["separated_weight"] == expected["proposed"]["separated_weight"]
    assert wrong != expected


def test_cli_valid_and_invalid():
    script = Path(__file__).with_name("program.py")
    request = json.loads(script.with_name("example_request.json").read_text())
    valid = subprocess.run([sys.executable, str(script)], input=json.dumps(request),
                           text=True, capture_output=True, timeout=10)
    assert valid.returncode == 0
    assert json.loads(valid.stdout) == oracle(request)
    invalid = subprocess.run([sys.executable, str(script)], input='{}',
                             text=True, capture_output=True, timeout=10)
    assert invalid.returncode != 0
    assert invalid.stdout == ""
