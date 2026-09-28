"""Independent combination/evidence oracle; selectors have distinct contracts."""

from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path

import pytest
import program


def example():
    return json.loads(Path(__file__).with_name("example_request.json").read_text())


def oracle(request):
    allnames = [v["version_id"] for v in request["versions"]]
    active = {v["version_id"] for v in request["versions"] if v["active"]}
    def outcome(a, b):
        relevant = [row for row in request["checks"] if {row["left"], row["right"]} == {a, b}]
        return relevant[-1]["passed"] if relevant else None
    def good(group):
        return all(outcome(a, b) is True for a, b in combinations(group, 2))
    def describe(group):
        selected = [n for n in allnames if n in group]
        inactive = [n for n in selected if n not in active]
        missing = [{"left": a, "right": b, "reason": "failed" if outcome(a, b) is False else "unverified"}
                   for a, b in combinations(selected, 2) if outcome(a, b) is not True]
        return {"selected": selected, "size": len(selected), "inactive": inactive, "missing_pairs": missing,
                "eligible_and_compatible": not inactive and not missing}
    reports = []
    for row in request["requests"]:
        names = [n for n in allnames if n in active and n in row["members"]]
        quick = []
        for n in names:
            if good(quick + [n]):
                quick.append(n)
        report = {"request_id": row["request_id"], "eligible": names, "current": describe(row["current"]),
                  "preview": describe(quick), "proposed": None, "changes": None}
        if row["mode"] == "select":
            groups = [g for k in range(len(names)+1) for g in combinations(names, k) if good(g)]
            chosen = min(groups, key=lambda g: (-len(g), sum(2**names.index(n) for n in g)))
            report["proposed"] = describe(chosen)
            report["changes"] = {"add": [n for n in allnames if n in chosen and n not in row["current"]],
                                 "remove": [n for n in allnames if n in row["current"] and n not in chosen]}
        reports.append(report)
    pairs = {tuple(sorted((r["left"], r["right"]))) for r in request["checks"]}
    return {"version_count": len(allnames), "check_count": len(request["checks"]), "pair_count": len(pairs),
            "superseded_check_count": len(request["checks"])-len(pairs), "requests": reports}


def test_all_small_relations_with_filters_and_both_request_modes():
    graphs = 0
    for n in range(5):
        names = [f"v{n-i}" for i in range(n)]
        pairs = list(combinations(names, 2))
        for flags in product((False, True), repeat=len(pairs)):
            checks = [{"left": a, "right": b, "passed": flag} for (a, b), flag in zip(pairs, flags)]
            for policy in ("all", "alternate", "none"):
                versions = [{"version_id": name, "active": policy == "all" or (policy == "alternate" and i % 2 == 0)} for i, name in enumerate(names)]
                requests = [{"request_id": mode, "members": list(reversed(names)), "current": list(reversed(names)), "mode": mode}
                            for mode in ("inspect", "select")]
                request = {"versions": versions, "checks": checks, "requests": requests}
                before = deepcopy(request)
                assert program.review_releases(request) == oracle(request)
                assert request == before
            graphs += 1
    assert graphs == 76


def test_example_preview_is_smaller_and_history_order_matters():
    request = example()
    report = program.review_releases(request)
    assert report == oracle(request)
    assert report["requests"][1]["preview"]["selected"] == ["legacy"]
    assert report["requests"][1]["proposed"]["selected"] == ["a", "b", "c"]
    assert report["superseded_check_count"] == 1
    request["checks"][:2] = request["checks"][:2][::-1]
    assert program.review_releases(request) == oracle(request)
    assert program.review_releases(request) != report


def test_inspect_path_has_no_complete_enumeration(monkeypatch):
    request = example()
    request["requests"] = request["requests"][:1]
    monkeypatch.setattr(program, "compatible", lambda *_: pytest.fail("no full selection in inspect"))
    assert program.review_releases(request) == oracle(request)


def test_replacing_preview_with_largest_group_changes_report(monkeypatch):
    monkeypatch.setattr(program, "preview", lambda matrix: [1, 2, 3])
    actual = program.review_releases(example())
    assert actual["requests"][1]["proposed"] == oracle(example())["requests"][1]["proposed"]
    assert actual != oracle(example())


def test_dropping_latest_check_dependency_is_detected(monkeypatch):
    original = program.latest_results
    monkeypatch.setattr(program, "latest_results", lambda checks: original(checks[::-1]))
    assert program.review_releases(example()) != oracle(example())


def test_ignoring_predicate_or_active_filter_is_detected(monkeypatch):
    monkeypatch.setattr(program, "compatible", lambda *_: True)
    assert program.review_releases(example()) != oracle(example())
    monkeypatch.undo()
    monkeypatch.setattr(program, "eligible", lambda versions, members: [v["version_id"] for v in versions if v["version_id"] in members])
    request = {"versions": [{"version_id": "retired", "active": False}], "checks": [],
               "requests": [{"request_id": "r", "members": ["retired"], "current": [], "mode": "select"}]}
    assert program.review_releases(request) != oracle(request)


def test_singleton_unknown_pairs_and_mask_tie():
    request = {"versions": [{"version_id": n, "active": True} for n in "abcd"],
               "checks": [{"left": "a", "right": "d", "passed": True}, {"left": "b", "right": "c", "passed": True}],
               "requests": [{"request_id": "r", "members": list("dcba"), "current": [], "mode": "select"}]}
    assert program.review_releases(request) == oracle(request)
    # mask 6 (b,c) precedes mask 9 (a,d), despite lexicographic tuple ordering.
    assert program.review_releases(request)["requests"][0]["proposed"]["selected"] == ["b", "c"]
    request["checks"] = []
    assert program.review_releases(request)["requests"][0]["proposed"]["selected"] == ["a"]


def test_late_invalid_query_before_any_computation(monkeypatch):
    request = example()
    request["requests"][-1]["members"].append("unknown")
    monkeypatch.setattr(program, "latest_results", lambda *_: pytest.fail("validate every request first"))
    with pytest.raises(ValueError):
        program.review_releases(request)


@pytest.mark.parametrize("kind", ["duplicate_version", "self_check", "nonboolean_check", "bad_current", "duplicate_query", "bad_mode", "extra"])
def test_invalid_inputs(kind):
    request = example()
    if kind == "duplicate_version": request["versions"].append(deepcopy(request["versions"][0]))
    elif kind == "self_check": request["checks"][-1]["right"] = request["checks"][-1]["left"]
    elif kind == "nonboolean_check": request["checks"][-1]["passed"] = 1
    elif kind == "bad_current": request["requests"][0]["current"] = ["missing"]
    elif kind == "duplicate_query": request["requests"].append(deepcopy(request["requests"][0]))
    elif kind == "bad_mode": request["requests"][0]["mode"] = "deploy"
    else: request["extra"] = 1
    with pytest.raises(ValueError):
        program.review_releases(request)
