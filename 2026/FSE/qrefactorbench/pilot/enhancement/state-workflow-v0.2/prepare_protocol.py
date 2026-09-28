"""Create a reviewable 25-call D/S/A/V/AV plan, without invoking any transport."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BRANCHES = ("self_review", "analysis_only", "verification_only", "analysis_and_verification")


def prepare(output: Path) -> dict:
    if output.exists():
        raise FileExistsError(output)
    slots = []
    for rep in range(1, 6):
        initial_id = f"{rep:02}-initial"
        slots.append({"id": initial_id, "replicate": rep, "arm": "initial", "depends_on": [],
                      "state": "not_run", "attempt_limit": 1})
        rotation = (rep - 1) % len(BRANCHES)
        for arm in BRANCHES[rotation:] + BRANCHES[:rotation]:
            slots.append({"id": f"{rep:02}-{arm}", "replicate": rep, "arm": arm,
                          "depends_on": [initial_id, f"{rep:02}-development-review"],
                          "state": "not_run", "attempt_limit": 1})
    protected = [HERE / name for name in ("claims.py", "build.py", "review.py", "prepare_protocol.py",
                                         "test_claims.py", "evidence/development.json", "evidence/evaluator-reserved.json")]
    protected += [HERE.parent / "state-workflow-v0.1/workflow.py",
                  ROOT / "pilot/reference_completion/v0.1.1/review_inputs/lit-009-C.txt",
                  ROOT / "schemas/phase1_prediction.schema.json",
                  ROOT / "pilot/model_comparison/20260922-c-v0.1/run.py"]
    protocol = {
        "version": "state-workflow-0.2-proposal", "run_authorization": None,
        "model": "gpt-5.6-sol", "reasoning_effort": "medium", "access": "existing ChatGPT subscription",
        "task": "unchanged lit-009 C initial input; separately versioned Phase-1 revisions",
        "mother_cases": 1, "replicates": 5, "maximum_model_calls": 25, "maximum_concurrency": 1,
        "timeout_seconds_per_call": 600, "operator_retries": 0,
        "model_tools": [], "model_seed": None, "temperature": None, "server_snapshot": None,
        "slots": slots,
        "development_review": {
            "performed_by": "Codex coordinator; AI_REVIEW_PENDING, not independent human review",
            "required_before_branch_execution": True,
            "record": "Exact anchors, formal interpretation(s), scope/guard, unknown or withdrawal; wall time separately.",
            "no_supported_binding": "insufficient_evidence observation, never a fabricated counterexample",
            "analysis_region": "All declared candidate regions in allowed public files; unsupported inventory scopes return unknown.",
            "feedback_semantic_scope": "Only lit009 pivot-selection claims; other candidate mappings remain unjudged.",
        },
        "branch_policy": "Every delivered initial draft enters all four revisions, irrespective of correctness; no filtering or response sharing.",
        "final_policy": "Bind claims before final evaluation; final results are collected only after all model revisions, never feedback.",
        "failure_policy": {
            "transport_or_isolation_error": "Stop remaining slots; retain called and unrun slots, no retries.",
            "invalid_or_budget_initial": "Retain failed initial and mark dependent revisions not_run_parent_failure; no substituted draft.",
            "invalid_revision": "Retain failure; continue independent preplanned branches if infrastructure intact.",
            "checker_binding_failure": "Stop for offline correction; do not silently score a model error or reissue a request.",
        },
        "reporting": ["All five replicate slots per arm, including missing/invalid outputs.",
                      "Finite local claims, ambiguity, guard exclusions, withdrawal and unknown separately.",
                      "Repair/regression only for comparable scopes; changing scope is its own outcome.",
                      "Reviewer overhead, classical tool cost, model usage and latency separately; not equal-token comparison.",
                      "No whole-task pass, scientific gold, model ranking, significance or independent-mother generalization."],
        "limitations": ["Explicit reviewer transcription remains part of this diagnostic workflow.",
                        "AST inventory is lexical, not sound slicing, range inference or reachability analysis.",
                        "Reserved requests are same-mother development evaluation, not an independent held-out program set.",
                        "Runner adapter and isolation preflight must be completed before live execution; this file is not a launcher."],
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected},
    }
    with output.open("x") as stream:
        stream.write(json.dumps(protocol, indent=2, ensure_ascii=False) + "\n")
    return protocol


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = prepare(args.output)
    print(json.dumps({"planned_slots": len(result["slots"]), "run_authorization": result["run_authorization"], "executed": 0}))
