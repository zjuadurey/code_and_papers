"""Fault injection and complete 25-slot rehearsal, with no model calls."""
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
def campaign(tmp_path):
    folder = tmp_path / "campaign"
    c.prepare(folder, simulation=True)
    return folder


def authorize(folder):
    c.save(folder / "authorization.json", {"protocol_sha256": c.sha(folder / "protocol.json"),
           "maximum_model_calls": 25, "model": "gpt-5.6-sol", "reasoning_effort": "medium",
           "simulation": True, "user_instruction": "SIMULATION ONLY: unit-test fixture, not live approval"})


def review(folder, slot, binding=True):
    raw = c.raw_path(folder, slot).read_text()
    return {"response_sha256": c.claims.response_digest(raw),
            "reviewer": {"identity": "Codex coordinator", "status": "AI_REVIEW_PENDING"},
            "review_seconds": 2.5, "unbound_reason": None if binding else "No supported pivot claim",
            "binding": c.load_document(c.V2 / "evidence/historical-binding.json") if binding else None}


def fake(raw=None, **overrides):
    def run(folder, entry, p):
        target = c.raw_path(folder, entry["case_id"])
        target.parent.mkdir(parents=True)
        target.write_text(HISTORICAL.read_text() if raw is None else raw)
        meta = {"input_sha256": entry["sha256"], "raw_output_sha256": c.sha(target),
                "exit_code": 0, "timeout": False, "errors": [], "tool_items": [],
                "turn_completed": True, "usage": [{"input_tokens": 10, "output_tokens": 10}],
                "elapsed_seconds": 0.01, **overrides}
        c.save(target.parent / "metadata.json", meta)
    return run


def initial_review(folder):
    authorize(folder)
    assert c.run_next(folder, fake())["status"] == "valid_response"
    c.stage_review(folder, "01-initial", review(folder, "01-initial"))


def test_denies_unapproved_call_before_creating_attempt(campaign):
    with pytest.raises(ValueError, match="await_authorization"):
        c.run_next(campaign, fake())
    assert not (campaign / "attempts").exists()


def test_protocol_hash_receipt_required(campaign):
    authorize(campaign)
    p = c.load_document(campaign / "protocol.json")
    p["model"] = "another-model"
    (campaign / "protocol.json").write_text(json.dumps(p))
    with pytest.raises(ValueError, match="Authorization"):
        c.run_next(campaign, fake())


def test_simulation_cannot_fall_through_to_live(campaign):
    authorize(campaign)
    with pytest.raises(ValueError, match="Simulation"):
        c.run_next(campaign)
    assert not (campaign / "attempts").exists()


def test_same_draft_all_four_arms_and_no_reserved_feedback(campaign, monkeypatch):
    authorize(campaign)
    c.run_next(campaign, fake())
    original = c.load_document
    def guarded(path):
        assert Path(path).name != "evaluator-reserved.json", "Reserved suite read during review"
        return original(path)
    monkeypatch.setattr(c, "load_document", guarded)
    c.stage_review(campaign, "01-initial", review(campaign, "01-initial"))
    prompts = original(campaign / "reviews/01-initial/prompts.json")
    for arm, (a, v) in c.workflow.ARMS.items():
        prompt = prompts[arm]
        assert json.dumps(HISTORICAL.read_text(), ensure_ascii=False) in prompt
        observations = json.loads(prompt.split("OBSERVATIONS (JSON array):\n")[1].split("\nReturn")[0])
        assert [o["kind"] for o in observations] == (["lexical_dependency_inventory"] if a else []) + (["semantic_feedback"] if v else [])
        assert "evaluator-reserved" not in prompt
    assert original(campaign / "reviews/01-initial/observations.json")["analysis"]["regions"]


def test_review_hash_and_reviewer_required_without_poisoning_retry(campaign):
    authorize(campaign)
    c.run_next(campaign, fake())
    r = review(campaign, "01-initial")
    bad = deepcopy(r)
    bad["response_sha256"] = "wrong"
    with pytest.raises(ValueError, match="different response"):
        c.stage_review(campaign, "01-initial", bad)
    assert c.state(campaign)["state"] == "await_development_review"
    c.stage_review(campaign, "01-initial", r)
    assert c.state(campaign)["state"] == "ready_call"


@pytest.mark.parametrize("raw", ["{truncated", '{"schema_version":"0.2.0","case_id":"lit-009","case_id":"lit-009"}', "[]", "NaN"])
def test_invalid_initial_retained_and_four_dependents_skipped(campaign, raw):
    authorize(campaign)
    assert c.run_next(campaign, fake(raw))["status"] == "invalid_response"
    for _ in range(4):
        assert c.run_next(campaign, fake())["status"] == "not_run_parent_failure"
    assert c.state(campaign)["slot"]["id"] == "02-initial"
    assert len(list((campaign / "attempts").glob("*.json"))) == 1


def test_invalid_revision_does_not_skip_independent_sibling(campaign):
    initial_review(campaign)
    assert c.run_next(campaign, fake("{}"))["status"] == "invalid_response"
    assert c.state(campaign)["slot"]["id"] == "01-analysis_only"
    assert c.run_next(campaign, fake())["status"] == "valid_response"


@pytest.mark.parametrize("override", [{"exit_code": 1}, {"tool_items": [{"type": "command_execution"}]},
                                     {"timeout": True}, {"turn_completed": False}, {"invalid_event_lines": 1}])
def test_infrastructure_failure_stops_all_remaining_calls(campaign, override):
    authorize(campaign)
    assert c.run_next(campaign, fake(**override))["status"] == "infrastructure_failure"
    current = c.state(campaign)
    assert current["state"] == "stopped" and len(current["records"]) == 25
    with pytest.raises(ValueError, match="stopped"):
        c.run_next(campaign, fake())
    assert c.collect_final(campaign)["attempts"] == 1


def test_interrupted_attempt_never_reissued(campaign):
    authorize(campaign)
    count = []
    def interrupted(*args):
        count.append(1)
        raise RuntimeError("Injected process interruption")
    with pytest.raises(RuntimeError, match="Injected"):
        c.run_next(campaign, interrupted)
    with pytest.raises(RuntimeError, match="Never reissue"):
        c.run_next(campaign, interrupted)
    assert len(count) == 1


def test_completed_transport_recovered_without_another_call(campaign):
    authorize(campaign)
    def crash_after_transport(*args):
        fake()(*args)
        raise RuntimeError("After response, before result publication")
    with pytest.raises(RuntimeError):
        c.run_next(campaign, crash_after_transport)
    assert c.run_next(campaign, lambda *args: pytest.fail("Reissued"))["status"] == "valid_response"


def test_early_final_evaluation_denied(campaign):
    initial_review(campaign)
    with pytest.raises(ValueError, match="revisions remain"):
        c.collect_final(campaign)
    with pytest.raises(ValueError, match="Finish the model queue"):
        c.bind_final(campaign, "01-self_review", {})


def test_mutated_branch_prompt_denied(campaign):
    initial_review(campaign)
    with (campaign / "reviews/01-initial/prompts.json").open("a") as stream:
        stream.write(" ")
    with pytest.raises(ValueError, match="Frozen review"):
        c.run_next(campaign, fake())
    assert len(list((campaign / "attempts").glob("*.json"))) == 1


def test_unknown_claim_is_not_manufactured_counterexample(campaign):
    authorize(campaign)
    c.run_next(campaign, fake())
    c.stage_review(campaign, "01-initial", review(campaign, "01-initial", binding=False))
    v = c.load_document(campaign / "reviews/01-initial/observations.json")["verification"]
    assert v["status"] == "insufficient_evidence" and v["interpretations"] == []


def test_full_25_slot_rehearsal_final_binding_barrier_fixed_denominators(campaign):
    authorize(campaign)
    for _ in range(30):
        current = c.state(campaign)
        if current["state"] == "all_slots_terminal":
            break
        if current["state"] == "await_development_review":
            initial = current["slot"]["depends_on"][0]
            c.stage_review(campaign, initial, review(campaign, initial))
        else:
            c.run_next(campaign, fake())
    assert c.state(campaign)["state"] == "all_slots_terminal"
    with pytest.raises(c.DataError):
        c.collect_final(campaign)
    for s in c.load_document(campaign / "protocol.json")["slots"]:
        if s["arm"] != "initial":
            c.bind_final(campaign, s["id"], review(campaign, s["id"]))
    result = c.collect_final(campaign)
    assert result["attempts"] == 25 and result["simulation"] is True
    for arm in ["initial", *c.workflow.ARMS]:
        assert sum(r["arm"] == arm for r in result["rows"]) == 5
    assert all(r["evaluation"]["status"] == "all_interpretations_contradicted" for r in result["rows"])
    with pytest.raises(ValueError, match="all_slots_terminal"):
        c.run_next(campaign, fake())


def test_concurrent_runner_lock(campaign):
    with c.locked(campaign):
        with pytest.raises(BlockingIOError):
            c.run_next(campaign, fake())


@pytest.mark.parametrize("placement", ["tools", "additional_tools"])
def test_wire_check_detects_tools_in_both_serialization_formats(placement):
    request = {"model": "gpt-5.6-sol", "reasoning": {"effort": "medium"},
               "input": [{"role": "developer", "content": [{"text": c.transport.WRAPPER}]},
                         {"role": "user", "content": [{"text": "public task"}]}]}
    preflight.validate_wire(request, "public task")
    if placement == "tools":
        request["tools"] = [{"type": "function", "name": "shell"}]
    else:
        request["input"].append({"type": "additional_tools", "tools": [{"type": "namespace", "name": "functions", "tools": [{"name": "exec"}]}]})
    with pytest.raises(ValueError, match="includes tools"):
        preflight.validate_wire(request, "public task")


def test_catalog_changes_only_declared_tool_metadata(campaign):
    p = c.verify(campaign)
    bundled = c.load_document(c.HERE / "bundled-sol-metadata.json")
    entry = c.load_document(c.HERE / "tool-free-sol-catalog.json")["models"][0]
    assert {k for k in bundled if bundled[k] != entry[k]} == set(p["catalog_overrides"])
    assert entry["slug"] == "gpt-5.6-sol"


def test_failed_result_alone_stops_after_crash_before_stop_publication(campaign):
    c.save(c.result_path(campaign, "01-initial"), {"slot": "01-initial", "arm": "initial", "replicate": 1,
                                                  "status": "infrastructure_failure"})
    assert not (campaign / "STOP.json").exists()
    assert c.state(campaign)["state"] == "stopped"
    assert len(c.state(campaign)["records"]) == 25
