"""Offline integrity and exact evaluator replay after final collection, never invokes a model."""
from datetime import datetime
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import campaign as c


def main(check_only: bool = False) -> None:
    folder = c.HERE / "campaign"
    p = c.verify(folder)
    c.authorized(folder, p)
    result = c.load_document(folder / "final-results.json")
    assert not result["simulation"] and result["planned_slots"] == 10
    assert result["protocol_sha256"] == c.sha(folder / "protocol.json")
    attempts = list((folder / "attempts").glob("*.json"))
    assert len(attempts) == result["attempts"] <= 10
    assert {r["slot"] for r in result["rows"]} == {s["id"] for s in p["slots"]}
    metadata = {}
    for s in p["slots"]:
        attempt_path = folder / "attempts" / f"{s['id']}.json"
        if not attempt_path.exists():
            continue
        attempt = c.load_document(attempt_path)
        meta = c.load_document(c.raw_path(folder, s["id"]).parent / "metadata.json")
        assert attempt["protocol_sha256"] == result["protocol_sha256"]
        assert attempt["input_sha256"] == meta["input_sha256"] == s["prompt_sha256"]
        assert c.sha(folder / "inputs" / f"{s['id']}.txt") == s["prompt_sha256"]
        metadata[s["id"]] = meta
    last_finished = max(datetime.fromisoformat(m["finished_utc"]) for m in metadata.values())
    barrier = c.load_document(HERE / "bindings-frozen-before-evaluation.json")
    assert barrier["final_results_exist"] is False
    assert datetime.fromisoformat(barrier["utc"]) >= last_finished
    suite = c.load_document(c.ROOT / p["evaluation_suite"])
    replayed = 0
    row_audit = []
    for row in result["rows"]:
        sid = row["slot"]
        if row["status"] != "valid_response":
            row_audit.append({"slot": sid, "status": row["status"]})
            continue
        rawpath = c.raw_path(folder, sid)
        assert c.sha(rawpath) == row["response_sha256"] == metadata[sid]["raw_output_sha256"]
        reviewpath = folder / "final-bindings" / f"{sid}.json"
        assert c.sha(reviewpath) == barrier["bindings_sha256"][sid]
        review = c.load_document(reviewpath)
        assert datetime.fromisoformat(review["review_started_utc"]) >= last_finished
        assert datetime.fromisoformat(review["review_submitted_utc"]) <= datetime.fromisoformat(barrier["utc"])
        c.base.check_review(rawpath.read_text(), review)
        expected = c.claims.evaluate(rawpath.read_text(), review.get("binding"), suite)
        expected["source_suite_role"] = expected["split"]
        expected["split"] = "known_regression"
        assert expected == row["evaluation"]
        assert row["task_pass"] is None
        replayed += 1
        document = c.load_document(rawpath)
        row_audit.append({"slot": sid, "replicate": row["replicate"], "arm": row["arm"],
                          "status": row["status"], "has_plan": document["plan"] is not None,
                          "regions": document["candidate_regions"],
                          "structural_eligibility": document["structural_eligibility"],
                          "migration_family": document["migration_family"], "decision": document["decision"],
                          "binding_resolution": review["binding"]["resolution"],
                          "evaluation_status": expected["status"], "task_pass": None})
    protected = c.load_document(c.HERE / "protected_before.json")
    changed = [path for path, digest in protected.items()
               if not (c.ROOT / path).is_file() or c.sha(c.ROOT / path) != digest]
    assert not changed, changed
    audit = {"utc": c.now(), "planned_slots": 10, "attempts": len(attempts),
             "valid_responses": replayed, "all_valid_evaluations_replayed_exactly": True,
             "all_reviews_after_model_queue": True, "all_bindings_before_evaluation": True,
             "tool_events": sum(len(m.get("tool_items", [])) for m in metadata.values()),
             "transport_errors": sum(len(m.get("errors", [])) for m in metadata.values()),
             "operator_retries": sum(m["operator_retries"] for m in metadata.values()),
             "protected_files_unchanged": len(protected), "changed_protected_files": changed,
             "protocol_sha256": result["protocol_sha256"], "paper_edited": False, "qpu_calls": 0,
             "evaluation_role": c.REGRESSION_ROLE,
             "model_seconds_sum": sum(m["elapsed_seconds"] for m in metadata.values()),
             "call_window_seconds": (last_finished - min(datetime.fromisoformat(m["started_utc"])
                                                          for m in metadata.values())).total_seconds()}
    if not check_only:
        c.save(HERE / "row-audit.json", row_audit)
        c.save(HERE / "execution-validation.json", audit)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Replay checks without writing artifacts")
    main(parser.parse_args().check_only)
