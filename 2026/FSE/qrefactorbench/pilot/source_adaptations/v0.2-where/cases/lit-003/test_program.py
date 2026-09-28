"""Independent participant-domain oracle and observable branch/boundary mistakes."""

from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path

import pytest
import program


def example():
    return json.loads(Path(__file__).with_name("example_request.json").read_text())


def oracle(request):
    sessions, slots, current = request["sessions"], request["slots"], request["current"]
    def conflict(i, j):
        return sorted(set(sessions[i]["participants"]) & set(sessions[j]["participants"]))
    def describe(assigned):
        missing = [s["session_id"] for s, v in zip(sessions, assigned) if v is None]
        clashes = [{"first": sessions[i]["session_id"], "second": sessions[j]["session_id"], "participants": conflict(i, j)}
                   for i, j in combinations(range(len(sessions)), 2)
                   if assigned[i] is not None and assigned[i] == assigned[j] and conflict(i, j)]
        return {"assignment": list(assigned), "unassigned": missing, "conflicts": clashes,
                "feasible": not missing and not clashes,
                "slots": [{"slot": v, "sessions": [s["session_id"] for s, val in zip(sessions, assigned) if val == v]} for v in slots]}
    report = {"session_count": len(sessions), "current": describe(current), "preview": None,
              "proposed": None, "status": "inspected", "moves": []}
    if request["mode"] == "inspect":
        return report
    if report["current"]["feasible"]:
        report.update(status="retained", proposed=describe(current))
        return report
    partial = []
    for i in range(len(sessions)):
        allowed = [v for v in slots if not any(v == partial[j] and conflict(i, j) for j in range(i))]
        if not allowed:
            break
        partial.append(allowed[0])
    if len(partial) == len(sessions):
        report.update(preview={"status": "ready", "assignment": partial}, status="preview")
        chosen = partial
    else:
        report["preview"] = {"status": "blocked", "assignment": None}
        chosen = next((list(a) for a in product(slots, repeat=len(sessions)) if describe(a)["feasible"]), None)
        report["status"] = "completed" if chosen is not None else "unavailable"
        if chosen is None:
            return report
    report["proposed"] = describe(chosen)
    report["moves"] = [{"session_id": s["session_id"], "from": old, "to": new}
                       for s, old, new in zip(sessions, current, chosen) if old != new]
    return report


def request_for_graph(n, edges, k):
    sessions = [{"session_id": f"s{n-i}", "participants": [f"p{a}-{b}" for a, b in edges if i in (a, b)]} for i in range(n)]
    return {"slots": [f"t{i}" for i in range(k)], "sessions": sessions, "current": [None]*n, "mode": "complete"}


def test_all_graphs_through_four_sessions_and_slot_counts():
    count = 0
    for n in range(5):
        pairs = list(combinations(range(n), 2))
        for flags in product((False, True), repeat=len(pairs)):
            edges = [p for p, flag in zip(pairs, flags) if flag]
            for k in range(4):
                request = request_for_graph(n, edges, k)
                before = deepcopy(request)
                assert program.review_agenda(request) == oracle(request)
                assert request == before
                count += 1
    assert count == 304


def test_preview_blocks_but_complete_arrangement_exists():
    report = program.review_agenda(example())
    assert report == oracle(example())
    assert report["preview"] == {"status": "blocked", "assignment": None}
    assert report["status"] == "completed"
    assert report["proposed"]["assignment"] == ["morning", "afternoon", "afternoon", "morning"]


@pytest.mark.parametrize("mode", ["inspect", "complete"])
def test_inspection_and_valid_current_do_not_reach_either_solver(mode, monkeypatch):
    request = example()
    request["mode"] = mode
    request["current"] = ["afternoon", "morning", "morning", "afternoon"]
    monkeypatch.setattr(program, "preview", lambda *_: pytest.fail("preview must not run"))
    monkeypatch.setattr(program, "complete", lambda *_: pytest.fail("complete must not run"))
    assert program.review_agenda(request) == oracle(request)


def test_ready_preview_does_not_run_completion(monkeypatch):
    request = request_for_graph(2, [(0, 1)], 2)
    monkeypatch.setattr(program, "complete", lambda *_: pytest.fail("already has preview"))
    assert program.review_agenda(request) == oracle(request)


def test_replacing_preview_with_complete_changes_observable_report(monkeypatch):
    original = program.complete
    monkeypatch.setattr(program, "preview", lambda matrix, k: original({i: [j for j, v in enumerate(row) if v] for i, row in enumerate(matrix)}, k))
    actual = program.review_agenda(example())
    assert actual["proposed"] == oracle(example())["proposed"]
    assert actual != oracle(example())  # Same final assignment does not preserve preview/status.


def test_dropping_participant_dependencies_is_detected(monkeypatch):
    monkeypatch.setattr(program, "relations", lambda sessions: ([[0]*len(sessions) for _ in sessions], {i: [] for i in range(len(sessions))}))
    assert program.review_agenda(example()) != oracle(example())


def test_turning_preview_failure_into_infeasibility_is_detected(monkeypatch):
    def reject(*_):
        raise ValueError("no arrangement")
    monkeypatch.setattr(program, "complete", reject)
    assert program.review_agenda(example()) != oracle(example())


def test_later_invalid_record_before_any_solving(monkeypatch):
    request = example()
    request["sessions"][-1]["participants"].append(1)
    monkeypatch.setattr(program, "preview", lambda *_: pytest.fail("validate first"))
    with pytest.raises(ValueError):
        program.review_agenda(request)


@pytest.mark.parametrize("field,value", [("slots", ["a", "a"]), ("slots", [False]), ("sessions", None),
    ("current", []), ("current", ["unknown"]*4), ("mode", "repair"), ("extra", 1)])
def test_invalid_fields(field, value):
    request = dict(example(), **{field: value})
    with pytest.raises(ValueError):
        program.review_agenda(request)


def test_duplicates_conflict_reporting_and_partial_current_are_not_fixed():
    request = example()
    request["current"] = [None, "morning", None, "morning"]
    assert program.review_agenda(request) == oracle(request)
    assert program.review_agenda(request)["proposed"]["assignment"][1] == "afternoon"
    request["sessions"].append(deepcopy(request["sessions"][0]))
    request["current"].append(None)
    with pytest.raises(ValueError):
        program.review_agenda(request)
