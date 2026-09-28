"""No live model calls: paired-input audits, fault injection, review barrier and full rehearsal."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import campaign as c
import preflight

HISTORICAL = c.ROOT / "pilot/model_comparison/20260923-four-model-c-v0.1/runs/gpt-5.6-sol/lit-009/response.txt"


@pytest.fixture
def folder(tmp_path):
    result = tmp_path / "campaign"
    c.prepare(result, simulation=True)
    return result


def authorize(folder, **overrides):
    c.save(folder / "authorization.json", {"protocol_sha256": c.sha(folder / "protocol.json"),
           "maximum_model_calls": 15, "model": "gpt-5.6-sol", "reasoning_effort": "medium",
           "simulation": True, "user_instruction": "SIMULATION ONLY: fixture, not live approval", **overrides})


def fake(raw=None, missing=False, **overrides):
    def run(folder, entry, p):
        target = c.raw_path(folder, entry["case_id"])
        target.parent.mkdir(parents=True)
        if not missing:
            target.write_text(HISTORICAL.read_text() if raw is None else raw)
        c.save(target.parent / "metadata.json", {
            "input_sha256": entry["sha256"], "raw_output_sha256": None if missing else c.sha(target),
            "exit_code": 0, "timeout": False, "errors": [], "tool_items": [], "turn_completed": True,
            "usage": [{"input_tokens": 1, "output_tokens": 1}], "elapsed_seconds": 0.01, **overrides})
    return run


def review(folder, slot):
    return {"response_sha256": c.sha(c.raw_path(folder, slot)),
            "reviewer": {"identity": "Codex coordinator", "status": "AI_REVIEW_PENDING"},
            "review_seconds": 1.0,
            "binding": c.load_document(c.base.V2 / "evidence/historical-binding.json")}


def finish_all(folder):
    authorize(folder)
    for _ in range(15):
        assert c.run_next(folder, fake())["status"] == "valid_response"


def test_no_approval_no_attempt(folder):
    with pytest.raises(ValueError, match="await_authorization"):
        c.run_next(folder, fake())
    assert not (folder / "attempts").exists()


@pytest.mark.parametrize("overrides", [{"maximum_model_calls": 25}, {"protocol_sha256": "old"},
                                       {"simulation": False}, {"user_instruction": ""}])
def test_old_or_wrong_receipt_rejected(folder, overrides):
    authorize(folder, **overrides)
    with pytest.raises(ValueError, match="Authorization"):
        c.run_next(folder, fake())
    assert not (folder / "attempts").exists()


def test_fake_mode_cannot_call_live_transport(folder):
    authorize(folder)
    with pytest.raises(ValueError, match="Simulation"):
        c.run_next(folder)
    assert not (folder / "attempts").exists()


def test_live_mode_requires_protocol_bound_preflight(tmp_path, monkeypatch):
    folder = tmp_path / "live"
    c.prepare(folder)
    authorize(folder, simulation=False)
    monkeypatch.setattr(c.transport, "run_case", lambda *a: pytest.fail("Live dispatch forbidden"))
    with pytest.raises(c.base.DataError):
        c.run_next(folder)
    c.save(folder / "preflight/passed.json", {"passed": True, "protocol_sha256": "wrong"})
    with pytest.raises(ValueError, match="preflight"):
        c.run_next(folder)
    assert not (folder / "attempts").exists()


def test_exact_same_draft_and_information_differences(folder):
    import design_inputs as d
    assert [s["arm"] for s in c.verify(folder)["slots"]] == [
        "self_review", "catalog_only", "routed_analysis",
        "catalog_only", "routed_analysis", "self_review",
        "routed_analysis", "self_review", "catalog_only",
        "self_review", "catalog_only", "routed_analysis",
        "catalog_only", "routed_analysis", "self_review"]
    packets = {}
    for s in c.verify(folder)["slots"]:
        text = (folder / "frozen-inputs" / f"{s['id']}.txt").read_text()
        task = json.loads(text.split("TASK SNAPSHOT (JSON string):\n")[1].split("\nCANDIDATE")[0])
        draft = json.loads(text.split("CANDIDATE (JSON string):\n")[1].split("\nOBSERVATIONS")[0])
        assert task == c.base.ORIGINAL.read_text()
        assert draft == c.raw_path(c.BASE / "campaign", s["historical_initial"]).read_text()
        obs = json.loads(text.split("OBSERVATIONS (JSON array):\n")[1].split("\nReturn")[0])
        packets[s["id"]] = obs
        assert "evaluator-reserved" not in text and "first_counterexample" not in text
        assert "specification_request" not in text
    for n in range(1,6):
        assert packets[f"{n:02d}-self_review"] == []
        cat = packets[f"{n:02d}-catalog_only"][0]
        routed = packets[f"{n:02d}-routed_analysis"][0]
        assert cat["source_catalog"] == routed["source_catalog"]
        assert cat["routes"] == [] and cat["eligibility_verdict"] is None
        assert routed == c.load_document(d.ROUTING / "audit" / f"{n:02d}-initial.json")
        assert cat == d.catalog_packet(routed)
    assert len({json.dumps(packets[f"{n:02d}-catalog_only"], sort_keys=True) for n in range(1,6)}) == 1


@pytest.mark.parametrize("raw", ["{truncated", "{}", "[]", "NaN",
                                       '{"case_id":"lit-009","case_id":"lit-009"}'])
def test_invalid_answer_retained_next_independent_slot_runs(folder, raw):
    authorize(folder)
    assert c.run_next(folder, fake(raw))["status"] == "invalid_response"
    assert c.state(folder)["slot"]["id"] == "01-catalog_only"
    assert c.run_next(folder, fake())["status"] == "valid_response"
    assert len(list((folder / "attempts").glob("*.json"))) == 2


def test_missing_answer_not_silently_retried(folder):
    authorize(folder)
    assert c.run_next(folder, fake(missing=True))["status"] == "missing_response"
    assert c.state(folder)["slot"]["id"] == "01-catalog_only"


@pytest.mark.parametrize("override", [{"timeout": True}, {"exit_code": 1}, {"turn_completed": False},
    {"errors": [{"type": "turn.failed"}]}, {"tool_items": [{"type": "command_execution"}]},
    {"invalid_event_lines": 1}])
def test_transport_failure_stops_and_retains_all15_positions(folder, override):
    authorize(folder)
    assert c.run_next(folder, fake(**override))["status"] == "infrastructure_failure"
    assert c.state(folder)["state"] == "stopped"
    result = c.collect_final(folder)
    assert len(result["rows"]) == 15 and result["attempts"] == 1
    assert sum(r["status"] == "not_run_infrastructure_stop" for r in result["rows"]) == 14
    assert result["denominators_by_arm"] == c.DENOMINATORS
    with pytest.raises(ValueError, match="stopped"):
        c.run_next(folder, fake())


def test_interruption_before_metadata_never_reissues(folder):
    authorize(folder)
    calls = []
    def interrupted(*args):
        calls.append(1)
        raise RuntimeError("Injected crash")
    with pytest.raises(RuntimeError, match="Injected"):
        c.run_next(folder, interrupted)
    with pytest.raises(RuntimeError, match="Never reissue"):
        c.run_next(folder, interrupted)
    assert len(calls) == 1


def test_completed_transport_recovers_without_new_call(folder):
    authorize(folder)
    def crash(*args):
        fake()(*args)
        raise RuntimeError("Injected post-response crash")
    with pytest.raises(RuntimeError):
        c.run_next(folder, crash)
    assert c.run_next(folder, lambda *a: pytest.fail("Reissued"))["status"] == "valid_response"


def test_failed_result_without_stop_file_still_stops(folder):
    c.save(c.result_path(folder, "01-self_review"), {"slot": "01-self_review",
           "arm": "self_review", "replicate": 1, "status": "infrastructure_failure"})
    assert c.state(folder)["state"] == "stopped"
    assert len(c.state(folder)["records"]) == 15


def test_final_gate_and_complete_rehearsal(folder, monkeypatch):
    real_load = c.load_document
    def no_regression(path):
        assert Path(path).name != "evaluator-reserved.json", "Regression read too early"
        return real_load(path)
    monkeypatch.setattr(c, "load_document", no_regression)
    with pytest.raises(ValueError, match="revisions remain"):
        c.collect_final(folder)
    with pytest.raises(ValueError, match="Finish the model queue"):
        c.bind_final(folder, "01-self_review", {})
    finish_all(folder)
    with pytest.raises(c.base.DataError):
        c.collect_final(folder)
    slots = c.verify(folder)["slots"]
    for s in slots[:-1]:
        c.bind_final(folder, s["id"], review(folder, s["id"]))
    with pytest.raises(c.base.DataError):
        c.collect_final(folder)
    c.bind_final(folder, slots[-1]["id"], review(folder, slots[-1]["id"]))
    monkeypatch.setattr(c, "load_document", real_load)
    result = c.collect_final(folder)
    assert result["simulation"] and result["attempts"] == len(result["rows"]) == 15
    assert result["paired_comparisons"]["routed_minus_catalog"] == [1, 2, 3, 4, 5]
    assert all(r["evaluation"]["split"] == "known_regression" for r in result["rows"])
    assert all(r["evaluation"]["status"] == "all_interpretations_contradicted" for r in result["rows"])
    assert all(r["task_pass"] is None for r in result["rows"])
    with pytest.raises(FileExistsError):
        c.bind_final(folder, slots[0]["id"], review(folder, slots[0]["id"]))
    with pytest.raises(FileExistsError):
        c.collect_final(folder)
    with pytest.raises(ValueError, match="all_slots_terminal"):
        c.run_next(folder, fake())


@pytest.mark.parametrize("change", ["prompt", "slots", "timeout", "config"])
def test_mutations_rejected_before_attempt(folder, change):
    authorize(folder)
    if change == "prompt":
        path = folder / "frozen-inputs/01-catalog_only.txt"
        path.write_text(path.read_text() + "private answer")
    else:
        p = c.load_document(folder / "protocol.json")
        if change == "slots": p["slots"].reverse()
        if change == "timeout": p["timeout_seconds_per_call"] = 1
        if change == "config": p["transport_config"].append('features.shell_tool=true')
        (folder / "protocol.json").write_text(json.dumps(p))
    with pytest.raises(ValueError, match="Frozen"):
        c.run_next(folder, fake())
    assert not (folder / "attempts").exists()


def test_mismatched_review_and_response_mutation_rejected(folder):
    finish_all(folder)
    bad = review(folder, "01-self_review"); bad["response_sha256"] = "wrong"
    with pytest.raises(ValueError, match="different response"):
        c.bind_final(folder, "01-self_review", bad)
    c.raw_path(folder, "01-self_review").write_text("{}")
    with pytest.raises(ValueError, match="changed after classification"):
        c.bind_final(folder, "01-self_review", review(folder, "01-self_review"))


def test_lock_excludes_second_runner(folder):
    with c.locked(folder):
        with pytest.raises(BlockingIOError):
            c.run_next(folder, fake())


@pytest.mark.parametrize("placement", ["tools", "additional_tools"])
def test_wire_tools_rejected(placement):
    # validate_wire needs only the transport wrapper from its campaign facade.
    request = {"model": "gpt-5.6-sol", "reasoning": {"effort": "medium"}, "input": [
        {"role": "developer", "content": [{"text": c.transport.WRAPPER}]},
        {"role": "user", "content": [{"text": "prompt"}]}]}
    preflight.legacy.validate_wire(request, "prompt")
    if placement == "tools": request["tools"] = [{"type": "function", "name": "shell"}]
    else: request["input"].append({"type": "additional_tools", "tools": [{"name": "exec"}]})
    with pytest.raises(ValueError, match="includes tools"):
        preflight.legacy.validate_wire(request, "prompt")
