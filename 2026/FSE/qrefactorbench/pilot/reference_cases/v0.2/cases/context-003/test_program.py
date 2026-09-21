"""Named-rule truth-table oracle; no reuse of clause compilation or production predicate."""

from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

import pytest
import program


def oracle(request):
    names = request["features"]
    reports = []
    for profile in request["profiles"]:
        possible = False
        for bits in product((False, True), repeat=len(names)):
            settings = dict(zip(names, bits))
            fixed = all(settings[name] for name in profile["enabled"]) and all(not settings[name] for name in profile["disabled"])
            rules = (all(not settings[a] or settings[b] for a, b in request["requires"])
                     and all(not (settings[a] and settings[b]) for a, b in request["excludes"])
                     and all(any(settings[name] for name in group) for group in request["at_least_one"]))
            possible |= fixed and rules
        reports.append({"profile_id": profile["profile_id"],
                        "enabled": [name for name in names if name in profile["enabled"]],
                        "disabled": [name for name in names if name in profile["disabled"]],
                        "unfixed_features": [name for name in names if name not in profile["enabled"] + profile["disabled"]],
                        "completion_exists": possible})
    return {"feature_count": len(names), "profile_count": len(reports), "profiles": reports,
            "compatible_profile_ids": [row["profile_id"] for row in reports if row["completion_exists"]],
            "incompatible_profile_ids": [row["profile_id"] for row in reports if not row["completion_exists"]]}


def test_bounded_named_rule_catalogues_and_all_partial_profiles():
    decisions = requests = 0
    for n in range(3):
        names = [f"option-{n-i}" for i in range(n)]
        pairs = [None] + [list(pair) for pair in product(names, repeat=2)]
        groups = [None] + [[name for name, chosen in zip(names, flags) if chosen]
                           for flags in product((False, True), repeat=n)]
        profiles = [{"profile_id": str(i), "enabled": [name for name, flag in zip(names, flags) if flag == 1][::-1],
                     "disabled": [name for name, flag in zip(names, flags) if flag == -1][::-1]}
                    for i, flags in enumerate(product((-1, 0, 1), repeat=n))]
        for requires, excludes, group in product(pairs, pairs, groups):
            request = {"features": names, "requires": [] if requires is None else [requires],
                       "excludes": [] if excludes is None else [excludes],
                       "at_least_one": [] if group is None else [group], "profiles": profiles}
            before = deepcopy(request)
            assert program.review_profiles(request) == oracle(request)
            assert request == before
            decisions += len(profiles)
            requests += 1
    assert (requests, decisions) == (139, 1163)


def test_example_full_report():
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    report = program.review_profiles(request)
    assert report == oracle(request)
    assert report["compatible_profile_ids"] == ["connected", "offline-only"]
    assert report["incompatible_profile_ids"] == ["conflicting"]


def test_duplicates_and_more_than_sixteen_features_are_not_rejected():
    request = {"features": [str(i) for i in range(17)], "requires": [["0", "1"], ["0", "1"]],
               "excludes": [], "at_least_one": [], "profiles": [{"profile_id": "none-fixed", "enabled": [], "disabled": []}]}
    assert program.review_profiles(request)["profiles"][0]["completion_exists"] is True
    request = {"features": ["a"], "requires": [], "excludes": [], "at_least_one": [["a", "a"]],
               "profiles": [{"profile_id": "p", "enabled": [], "disabled": []}]}
    assert program.review_profiles(request) == oracle(request)


def invalid_requests():
    valid = {"features": ["a", "b"], "requires": [], "excludes": [], "at_least_one": [], "profiles": []}
    yield None
    yield {}
    yield dict(valid, extra=1)
    for names in [None, "ab", ["a", "a"], [""], [False]]:
        yield dict(valid, features=names)
    for key in ["requires", "excludes"]:
        for pairs in [None, [["a"]], [["a", "unknown"]], [["a", []]], [["a", "b"], ["missing", "b"]]]:
            yield dict(valid, **{key: pairs})
    for groups in [None, ["a"], [["unknown"]], [[False]]]:
        yield dict(valid, at_least_one=groups)
    profile = {"profile_id": "p", "enabled": [], "disabled": []}
    for rows in [None, [{}], [profile, profile], [dict(profile, enabled=["unknown"])],
                 [dict(profile, enabled=["a", "a"])], [dict(profile, enabled=["a"], disabled=["a"])],
                 [dict(profile, profile_id="")], [dict(profile, disabled=None)],
                 [profile, dict(profile, profile_id="later", enabled=[False])]]:
        yield dict(valid, profiles=rows)


@pytest.mark.parametrize("payload", list(invalid_requests()))
def test_invalid_full_request_rejected_before_solving(payload, monkeypatch):
    monkeypatch.setattr(program, "has_assignment", lambda *_: pytest.fail("Validate all profiles first"))
    before = deepcopy(payload)
    with pytest.raises(ValueError):
        program.review_profiles(payload)
    assert payload == before


def test_ignored_fixed_settings_are_detected(monkeypatch):
    request = {"features": ["a"], "requires": [], "excludes": [], "at_least_one": [["a"]],
               "profiles": [{"profile_id": "blocked", "enabled": [], "disabled": ["a"]}]}
    monkeypatch.setattr(program, "clauses_for_profile", lambda _names, clauses, _profile: clauses)
    assert program.review_profiles(request) != oracle(request)


def test_misplaced_profile_decisions_are_detected(monkeypatch):
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    monkeypatch.setattr(program, "has_assignment", lambda *_: False)
    assert program.review_profiles(request) != oracle(request)


def test_cli_and_empty_profile_list():
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("program.py"))],
                            input=json.dumps(request), text=True, capture_output=True, check=True)
    assert json.loads(result.stdout) == oracle(request)
    request["profiles"] = []
    assert program.review_profiles(request) == oracle(request)
