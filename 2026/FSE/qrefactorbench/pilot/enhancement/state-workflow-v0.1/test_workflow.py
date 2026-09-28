"""Check scientific isolation and evidence boundaries, not generated answer quality."""
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("state_workflow", HERE / "workflow.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


def test_inventory_tracks_loop_carried_mutation_and_dependencies():
    source = (w.CASE / "kernel.py").read_text()
    result = w.analyze_source(source, "solve", 13)
    statements = {s["line"]: s for s in result["statements"]}
    assert {11, 12, 13, 16, 17, 18, 19, 20} <= statements.keys()
    assert statements[20]["writes_or_mutates"] == ["rows"]
    assert {"rows", "factor", "col", "n"} <= set(result["mentioned_names"])
    assert "status" not in result and "task_pass" not in result


def test_inventory_does_not_execute_input_or_pull_unrelated_assignment(tmp_path):
    marker = tmp_path / "must-not-exist"
    source = f"open({str(marker)!r}, 'w').write('bad')\ndef f(x):\n    unrelated = 42\n    y = x + 1\n    return y\n"
    result = w.analyze_source(source, "f", 5)
    assert not marker.exists()
    assert {s["line"] for s in result["statements"]} == {4, 5}


@pytest.mark.parametrize("function,line", [("missing", 13), ("solve", 99), ("solve", 8)])
def test_invalid_candidate_rejected(function, line):
    with pytest.raises(ValueError):
        w.analyze_source((w.CASE / "kernel.py").read_text(), function, line)


def test_arbitrary_new_prose_is_unknown_not_replayed_failure():
    trace = json.loads((w.REVIEW / "evidence/trace.json").read_text())
    result = w.bound_feedback('{"plan": {"formulation": "a different legitimate mapping"}}', trace)
    assert result["status"] == "insufficient_evidence"
    assert result["task_pass"] is None and "reachable_state" not in result


def test_bound_feedback_has_actual_witness_but_no_repair_or_analysis():
    trace = json.loads((w.REVIEW / "evidence/trace.json").read_text())
    raw = (w.ROOT / trace["provenance"]["response_path"]).read_text()
    feedback = w.bound_feedback(raw, trace)
    assert feedback["status"] == "local_claim_contradicted"
    assert feedback["reachable_state"]["values"] == ["nan", "nan"]
    assert feedback["reachable_state"]["literal_marked"] == []
    assert feedback["reachable_state"]["excluding_self_marked"] == []
    assert "ordered_scan_control" not in json.dumps(feedback)
    assert "statements" not in feedback and feedback["task_pass"] is None


@pytest.mark.parametrize("arm", list(w.ARMS))
def test_ablation_only_removes_requested_observations(arm):
    a, v = w.ARMS[arm]
    observations = ([{"kind": "analysis", "data": "ANALYSIS_SENTINEL"}] if a else [])
    observations += ([{"kind": "verification", "data": "VERIFIER_SENTINEL"}] if v else [])
    prompt = w.revision_prompt("TASK_SENTINEL", "DRAFT_SENTINEL", observations)
    assert ("ANALYSIS_SENTINEL" in prompt) == a
    assert ("VERIFIER_SENTINEL" in prompt) == v
    assert "TASK_SENTINEL" in prompt and "DRAFT_SENTINEL" in prompt
    assert arm not in prompt and "withheld" not in prompt and "hidden result" not in prompt


def test_demo_preserves_fixed_branches_unknown_outcomes_and_refuses_overwrite(tmp_path):
    output = tmp_path / "demo"
    summary = w.prepare_demo(output)
    assert summary["experiment_completed"] is False
    assert summary["new_model_calls"] == 0 and summary["effect_on_model_quality"] is None
    assert {r["arm"] for r in summary["records"]} == set(w.ARMS)
    assert len({r["initial_sha256"] for r in summary["records"]}) == 1
    assert all(r["task_pass"] is None and r["repair_success"] is None for r in summary["records"])
    assert all(r["state"] == "awaiting_model_not_run" for r in summary["records"])
    assert all(r["revision_call_limit"] == 1 for r in summary["records"])
    before = (output / "summary.json").read_bytes()
    with pytest.raises(FileExistsError):
        w.prepare_demo(output)
    assert (output / "summary.json").read_bytes() == before
