from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("n055_routing", HERE / "routing.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
CASE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-009"
SOURCES = {name: (CASE / name).read_text() for name in ["program.py", "kernel.py", "common.py"]}


def region(first, last, function="solve", file="kernel.py"):
    return {"file": file, "function": function, "start_line": first, "end_line": last}


def test_empty_is_not_a_negative_verdict_and_catalog_is_complete():
    result = r.analyze(SOURCES, [])
    assert result["status"] == "no_nomination" and result["routes"] == []
    assert not result["candidate_discovery_performed"] and result["eligibility_verdict"] is None
    assert [f["file"] for f in result["source_catalog"]] == list(SOURCES)
    assert [f["function"] for f in result["source_catalog"][1]["functions"]] == ["solve", "residual"]


@pytest.mark.parametrize("span,status,seed", [((12, 16), "region_outline", None),
    ((13, 13), "statement_inventory", 13), ((9, 26), "function_outline", None),
    ((12, 20), "statement_inventory", 12), ((14, 15), "statement_inventory", 14),
    ((13, 16), "region_outline", None)])
def test_span_is_preserved_without_silent_seed_changes(span, status, seed):
    requested = region(*span)
    result = r.analyze(SOURCES, [requested])["routes"][0]
    assert result["declared_region"] == requested and result["status"] == status
    assert (result["seed_statement"]["start_line"] if result["seed_statement"] else None) == seed
    assert result["analysis_scope"]["start_line"] == 9 and result["analysis_scope"]["end_line"] == 26
    if span == (12, 16):
        assert any(s["start_line"] == 12 and s["end_line"] == 20 and
                   s["relation"] == "contains_declared" for s in result["boundary_statements"])


def test_exact_statement_keeps_loop_carried_inventory():
    result = r.analyze(SOURCES, [region(13, 13)])["routes"][0]
    assert {11, 12, 13, 16, 17, 18, 19, 20} <= {s["line"] for s in result["inventory"]["statements"]}


@pytest.mark.parametrize("bad", [region(0, 1), region(16, 12), region(True, 13),
    region("13", 13), {"file": "kernel.py"}, None])
def test_malformed_region_is_retained_not_dropped(bad):
    result = r.analyze(SOURCES, [bad])["routes"][0]
    assert result["declared_region"] == bad and result["status"] == "invalid_region"


@pytest.mark.parametrize("path", ["../case.json", "/etc/passwd", "case.json", "test_program.py"])
def test_unknown_file_cannot_escape_source_allowlist(path):
    result = r.analyze(SOURCES, [region(13, 13, file=path)])["routes"][0]
    assert result["status"] == "file_not_in_public_allowlist" and result["inventory"] is None


@pytest.mark.parametrize("reg", [region(8, 13), region(25, 30), region(13, 13, "missing")])
def test_outside_or_unknown_function_keeps_unknown(reg):
    assert r.analyze(SOURCES, [reg])["routes"][0]["status"] == "outside_or_unknown_function"


def test_no_source_execution_and_no_nested_scope_confusion(tmp_path):
    marker = tmp_path / "never-created"
    source = f"open({str(marker)!r}, 'w').write('x')\ndef f(x):\n    def g():\n        return 42\n    y = x+1\n    return y\n"
    result = r.analyze({"s.py": source}, [region(5, 5, "f", "s.py")])
    statements = result["source_catalog"][0]["functions"][0]["statements"]
    assert not marker.exists() and not any(s["start_line"] == 4 for s in statements)
    assert result["routes"][0]["status"] == "inventory_unsupported"


def test_same_line_statements_not_arbitrarily_chosen():
    source = "def f():\n    x=1; y=2\n    return x+y\n"
    route = r.analyze({"s.py": source}, [region(2, 2, "f", "s.py")])["routes"][0]
    assert route["status"] == "ambiguous_statement_span" and route["seed_statement"] is None


def test_multiple_regions_keep_order_and_inputs_unchanged():
    requests = [region(9, 26), region(13, 13), region(13, 13, file="secret")]
    before = deepcopy(requests)
    result = r.analyze(SOURCES, requests)
    assert requests == before and [x["declared_region"] for x in result["routes"]] == before


def test_historical_five_initials_have_expected_routes():
    statuses = []
    for n in range(1, 6):
        raw = ROOT / f"pilot/enhancement/state-workflow-v0.3/campaign/runs/gpt-5.6-sol/{n:02d}-initial/response.txt"
        result = r.analyze(SOURCES, json.loads(raw.read_text())["candidate_regions"])
        statuses.append(result["routes"][0]["status"] if result["routes"] else result["status"])
    assert statuses == ["region_outline", "statement_inventory", "no_nomination", "function_outline", "statement_inventory"]


@pytest.mark.parametrize("span,status", [((2, 2), "region_outline"),
    ((2, 4), "statement_inventory"), ((3, 3), "region_outline")])
def test_multiline_statement_requires_full_span(span, status):
    source = "def f(x):\n    y = (\n        x + 1\n    )\n    return y\n"
    route = r.analyze({"s.py": source}, [region(*span, "f", "s.py")])["routes"][0]
    assert route["status"] == status


def test_duplicate_function_name_uses_declared_span():
    source = "def f():\n    return 1\ndef f():\n    return 2\n"
    route = r.analyze({"s.py": source}, [region(4, 4, "f", "s.py")])["routes"][0]
    assert route["analysis_scope"]["start_line"] == 3
    assert route["inventory"]["statements"][0]["source_line"] == "return 2"


def test_class_methods_are_not_confused_with_top_level_functions():
    source = "class C:\n    def f(self):\n        return 1\n"
    result = r.analyze({"s.py": source}, [region(3, 3, "f", "s.py")])
    assert result["routes"][0]["status"] == "outside_or_unknown_function"
    assert result["source_catalog"][0]["functions"] == []


def test_syntax_failure_is_not_reported_as_no_candidate():
    with pytest.raises(SyntaxError):
        r.analyze({"s.py": "def broken(:"}, [])
