"""Evidence binding, equivalent claims, outcome categories and feedback isolation."""
from copy import deepcopy
from argparse import Namespace
import itertools
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    import claims as c
    import build as b
finally:
    sys.path.remove(str(HERE))


@pytest.fixture(scope="module")
def suites():
    return b.make_suites()


@pytest.mark.parametrize("name", ["nan_aware_predicate", "equivalent_ordered_scan"])
def test_correct_and_equivalent_controls_pass_all_reachable_states(suites, name):
    raw, binding = b.controls()[name]
    for suite in suites:
        result = c.evaluate(raw, binding, suite)
        assert result["status"] == "finite_scope_pass"
        assert result["task_pass"] is None and result["fallback_execution"] is None
        assert result["interpretations"][0]["checked_states"] > 0


@pytest.mark.parametrize("name", ["inclusive_bug", "exclusive_bug", "missing_tie", "last_tie_scan", "first_only"])
def test_wrong_controls_rejected_by_reserved_suite(suites, name):
    raw, binding = b.controls()[name]
    result = c.evaluate(raw, binding, suites[1])
    assert result["status"] == "contradicted"
    assert result["interpretations"][0]["failures"]


def test_reserved_set_exposes_first_only_development_blind_spot(suites):
    raw, binding = b.controls()["first_only"]
    assert c.evaluate(raw, binding, suites[0])["status"] == "finite_scope_pass"
    assert c.evaluate(raw, binding, suites[1])["status"] == "contradicted"


def test_nan_aware_expression_matches_independent_python_max_exhaustively():
    # 780 synthetic abstract states; evaluator regression, NOT reachable model tests.
    expression = c.Expression(b.NAN_AWARE, {"i"})
    for n in range(1, 5):
        for values in itertools.product([float("nan"), float("inf"), 0.0, 1.0, 2.0], repeat=n):
            indices = list(range(3, 3 + n))
            env = {"indices": indices, "values": dict(zip(indices, values))}
            marked = [i for i in indices if expression.boolean({**env, "i": i})]
            assert marked == [max(indices, key=env["values"].__getitem__)]


def test_guard_does_not_convert_excluded_states_or_fallback_into_success(suites):
    raw, binding = b.controls()["guarded_finite"]
    result = c.evaluate(raw, binding, suites[1])
    assert result["status"] == "finite_guarded_pass"
    assert result["interpretations"][0]["excluded_states"] > 0
    assert result["task_pass"] is None and result["fallback_execution"] is None
    raw, binding = b.controls()["guard_always_false"]
    assert c.evaluate(raw, binding, suites[1])["status"] == "not_exercised"


@pytest.mark.parametrize("resolution,status", [("withdrawn", "claim_withdrawn"), ("unsupported", "insufficient_evidence")])
def test_nontranscribed_resolutions_are_not_errors_or_passes(suites, resolution, status):
    raw, binding = b.controls()[resolution]
    result = c.evaluate(raw, binding, suites[1])
    assert result["status"] == status and result["interpretations"] == []
    assert result["task_pass"] is None


def test_fresh_response_uses_its_own_reviewed_binding(suites):
    raw = json.dumps({"plan": {"formulation": "A newly phrased ordered scan: retain the incumbent unless a later absolute value is strictly greater."}})
    binding = b.bind(raw, [b.interpretation("values[candidate] > values[incumbent]", mode="ordered_scan")])
    assert c.evaluate(raw, binding, suites[1])["status"] == "finite_scope_pass"
    assert c.evaluate(raw, None, suites[1])["status"] == "insufficient_evidence"


@pytest.mark.parametrize("corruption", ["hash", "quote", "pointer", "reviewer", "origin", "scope"])
def test_bad_binding_cannot_silently_score_response(suites, corruption):
    raw, original = b.controls()["nan_aware_predicate"]
    binding = deepcopy(original)
    if corruption == "hash": binding["response_sha256"] = "bad"
    elif corruption == "quote": binding["anchors"][0]["quote"] = "not what the model said"
    elif corruption == "pointer": binding["anchors"][0]["pointer"] = "/missing"
    elif corruption == "reviewer": binding["reviewer"] = {}
    else: binding[corruption] = "invalid"
    with pytest.raises(c.InvalidClaim):
        c.evaluate(raw, binding, suites[1])


def test_ambiguous_singleton_is_not_forced_to_wrong_interpretation(suites):
    raw = json.dumps({"plan": {"formulation": "At least every candidate magnitude, with no earlier equal."}})
    binding = b.bind(raw, [b.interpretation(b.INCLUSIVE, ident="self"), b.interpretation(b.EXCLUSIVE, ident="other")], resolution="ambiguous")
    old = suites[0]["requests"][1]
    singleton = c.seal_suite("development", [{**old, "states": [old["states"][-1]]}])
    result = c.evaluate(raw, binding, singleton)
    assert result["status"] == "ambiguous_interpretation"
    assert {r["status"] for r in result["interpretations"]} == {"contradicted", "finite_scope_pass"}
    assert c.evaluate(raw, binding, suites[0])["status"] == "all_interpretations_contradicted"


@pytest.mark.parametrize("expression", ["__import__('os').system('echo bad')", "values.__class__", "[i for i in indices]", "open('x')", "sum(values)", "all(values[i] > 0 for i in indices)", "all(True for k in range(999999))"])
def test_rejects_nonwhitelisted_or_shadowed_expressions(expression):
    with pytest.raises(c.InvalidClaim):
        c.Expression(expression, {"i"})


def test_expression_budget_and_nonboolean_result():
    with pytest.raises(c.ClaimBudget):
        c.Expression(" " * 2049, {"i"})
    with pytest.raises(c.InvalidClaim):
        c.Expression("1", set()).boolean({"values": {}, "indices": []})


def test_feedback_rejects_reserved_and_tampered_role(suites):
    raw, binding = b.controls()["inclusive_bug"]
    with pytest.raises(ValueError, match="reserved"):
        c.development_feedback(raw, binding, suites[1])
    forged = deepcopy(suites[1])
    forged["role"] = "development"
    with pytest.raises(ValueError, match="integrity"):
        c.development_feedback(raw, binding, forged)


def test_final_changes_cannot_change_development_feedback(suites):
    raw, binding = b.controls()["inclusive_bug"]
    before = c.development_feedback(raw, binding, suites[0])
    altered = deepcopy(suites[1])
    altered["requests"][0]["id"] = "RESERVED_CANARY_NEVER_SEND"
    c.evaluate(raw, binding, c.seal_suite("evaluator_reserved", altered["requests"]))
    after = c.development_feedback(raw, binding, suites[0])
    assert before == after and "RESERVED_CANARY_NEVER_SEND" not in json.dumps(after)
    assert "expression" not in json.dumps(after) and "ordered_scan" not in json.dumps(after)


def test_development_and_reserved_requests_disjoint_and_original_outcomes_retained(suites):
    dev, final = suites
    assert not {r["input_sha256"] for r in dev["requests"]} & {r["input_sha256"] for r in final["requests"]}
    assert all(r["input_unchanged"] for suite in suites for r in suite["requests"])
    assert any(r["outcome"].get("message") == "singular system" for r in final["requests"])
    empty = next(r for r in final["requests"] if not r["input"]["rhs"])
    assert empty["states"] == [] and empty["outcome"]["report"]["proposal"] == {}


@pytest.mark.parametrize("field", ["input_sha256", "original"])
def test_suite_does_not_accept_corrupt_request_or_oracle(suites, field):
    suite = deepcopy(suites[1])
    if field == "input_sha256":
        suite["requests"][0][field] = "bad"
    else:
        state = suite["requests"][0]["states"][0]
        state[field] = state["indices"][0]
    with pytest.raises(ValueError):
        c.validate_suite(c.seal_suite("evaluator_reserved", suite["requests"]))


def test_build_retains_history_and_no_model_results(tmp_path):
    output = tmp_path / "new"
    b.build(output)
    summary = json.loads((output / "summary.json").read_text())
    assert summary["new_model_calls"] == 0 and summary["task_pass"] is None
    assert len(summary["prompts"]) == 4
    assert all(p["state"] == "awaiting_model_not_run" for p in summary["prompts"])
    for expected in (HERE / "evidence").glob("*"):
        if expected.is_file():
            assert (output / expected.name).read_bytes() == expected.read_bytes(), expected.name
    with pytest.raises(FileExistsError):
        b.build(output)


def test_review_template_requires_actual_review_before_scoring(tmp_path, suites):
    review = b.load_module("test_n046_review", HERE / "review.py")
    raw, _ = b.controls()["nan_aware_predicate"]
    response = tmp_path / "response.json"
    response.write_text(raw)
    output = tmp_path / "unreviewed.json"
    review.run(Namespace(action="template", response=response, pointer="/plan/formulation", output=output))
    template = json.loads(output.read_text())
    assert template["reviewer"]["status"] == "UNREVIEWED"
    assert template["resolution"] is None
    with pytest.raises(c.InvalidClaim):
        c.evaluate(raw, template, suites[0])


def test_review_feedback_entry_refuses_reserved_and_existing_output(tmp_path, suites):
    review = b.load_module("test_n046_review_io", HERE / "review.py")
    raw, binding = b.controls()["inclusive_bug"]
    response, bound, suite_file = [tmp_path / name for name in ("response.json", "binding.json", "suite.json")]
    response.write_text(raw)
    bound.write_text(json.dumps(binding))
    suite_file.write_text(json.dumps(suites[1]))
    output = tmp_path / "feedback.json"
    args = Namespace(action="feedback", response=response, binding=bound, suite=suite_file, output=output)
    with pytest.raises(ValueError):
        review.run(args)
    assert not output.exists()
    suite_file.write_text(json.dumps(suites[0]))
    review.run(args)
    assert json.loads(output.read_text())["status"] == "contradicted"
    with pytest.raises(FileExistsError):
        review.run(args)


def test_protocol_keeps_twenty_five_fixed_slots_and_no_run_authorization(tmp_path):
    prepare = b.load_module("test_n046_prepare", HERE / "prepare_protocol.py")
    path = tmp_path / "proposal.json"
    protocol = prepare.prepare(path)
    assert len(protocol["slots"]) == protocol["maximum_model_calls"] == 25
    assert len({s["id"] for s in protocol["slots"]}) == 25
    assert protocol["run_authorization"] is None
    assert all(s["state"] == "not_run" and s["attempt_limit"] == 1 for s in protocol["slots"])
    for rep in range(1, 6):
        slots = [s for s in protocol["slots"] if s["replicate"] == rep]
        assert {s["arm"] for s in slots} == {"initial", *prepare.BRANCHES}
        assert all(s["depends_on"][0] == f"{rep:02}-initial" for s in slots[1:])
    with pytest.raises(FileExistsError):
        prepare.prepare(path)
