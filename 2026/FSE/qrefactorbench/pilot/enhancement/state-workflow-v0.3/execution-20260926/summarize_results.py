"""Summarize frozen final rows; preserve unknowns, missing slots and cost fields."""
from collections import Counter
import csv
from pathlib import Path
from run_frozen import campaign as c

HERE = Path(__file__).resolve().parent


def summarize():
    folder = c.HERE / "campaign"
    result = c.load_document(folder / "final-results.json")
    if result["simulation"] or result["planned_slots"] != 25:
        raise ValueError("Expected this live 25-slot campaign")
    summaries = []
    for arm in ["initial", *c.workflow.ARMS]:
        rows = [r for r in result["rows"] if r["arm"] == arm]
        if len(rows) != 5:
            raise ValueError("Fixed denominator changed")
        usage = [u for r in rows for u in r.get("usage", [])]
        summaries.append({"arm": arm, "planned": 5,
             "attempted": sum((folder / "attempts" / f"{r['slot']}.json").exists() for r in rows),
             "response_status": dict(Counter(r["status"] for r in rows)),
             "evaluation_status": dict(Counter(r.get("evaluation", {}).get("status", "not_evaluated") for r in rows)),
             "input_tokens": sum(u.get("input_tokens", 0) for u in usage),
             "cached_input_tokens": sum(u.get("cached_input_tokens", 0) for u in usage),
             "output_tokens": sum(u.get("output_tokens", 0) for u in usage),
             "reasoning_output_tokens": sum(u.get("reasoning_output_tokens", 0) for u in usage),
             "model_seconds": round(sum(r.get("model_seconds") or 0 for r in rows), 3),
             "review_wall_seconds": round(sum(r.get("review_seconds") or 0 for r in rows), 3),
             "development_tool_seconds": sum(r.get("development_tool_seconds", 0) for r in rows),
             "evaluation_tool_seconds": sum(r.get("evaluation_tool_seconds", 0) for r in rows)})
    pairs = []
    for row in result["rows"]:
        if row["arm"] == "initial":
            continue
        initial = next(r for r in result["rows"] if r["arm"] == "initial" and r["replicate"] == row["replicate"])
        before = initial.get("evaluation", {}).get("status", "not_evaluated")
        after = row.get("evaluation", {}).get("status", "not_evaluated")
        # Finite unguarded passes concern this local input/output relation, never the full task.
        outcome = ("finite_local_repair_candidate" if before in ("contradicted", "all_interpretations_contradicted") and after == "finite_scope_pass"
                   else "finite_local_regression_candidate" if before == "finite_scope_pass" and after in ("contradicted", "all_interpretations_contradicted")
                   else "conditional_scope" if after == "finite_guarded_pass"
                   else "no_repair_regression_claim")
        pairs.append({"replicate": row["replicate"], "arm": row["arm"], "initial_status": before,
                      "revision_status": after, "comparison": outcome,
                      "note": "Candidate transitions still require prose/guard scope review; not whole-task outcomes."})
    summary = {"source_sha256": c.sha(folder / "final-results.json"), "protocol_sha256": result["protocol_sha256"],
               "attempts": result["attempts"], "fixed_slots": 25, "mother_cases": 1,
               "arms": summaries, "pairs": pairs, "task_pass": None, "model_quality_effect_automatically_established": False,
               "cost_notes": ["Cached input is a subset of input; reasoning output is not added again to output.",
                              "Reviewer wall time includes coordination/tool latency; AI review is not independent human annotation.",
                              "Tool cost is measured wall time, not end-to-end quantum speedup or equal-token matching."]}
    c.save(HERE / "summary.json", summary)
    with (HERE / "pairs.csv").open("x") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(pairs[0]))
        writer.writeheader()
        writer.writerows(pairs)
    return summary


if __name__ == "__main__":
    import json
    print(json.dumps(summarize(), ensure_ascii=False, indent=2))
