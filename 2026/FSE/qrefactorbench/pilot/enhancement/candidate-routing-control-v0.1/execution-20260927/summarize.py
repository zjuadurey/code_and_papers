"""Summarize completed frozen results, preserving paired planned populations and unknowns."""
from collections import Counter
import csv
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import campaign as c


def main() -> None:
    folder = c.HERE / "campaign"
    result = c.load_document(folder / "final-results.json")
    if result["simulation"] or result["planned_slots"] != 15:
        raise ValueError("Expected this live fifteen-slot experiment")
    arms = []
    for arm, denominator in c.DENOMINATORS.items():
        rows = [r for r in result["rows"] if r["arm"] == arm]
        assert len(rows) == denominator
        usage = [u for r in rows for u in r.get("usage", [])]
        arms.append({"arm": arm, "planned": denominator,
                     "response_status": dict(Counter(r["status"] for r in rows)),
                     "evaluation_status": dict(Counter(r.get("evaluation", {}).get("status", "not_evaluated") for r in rows)),
                     **{k: sum(u.get(k, 0) for u in usage) for k in
                        ["input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"]},
                     "model_seconds": round(sum(r.get("model_seconds") or 0 for r in rows), 3),
                     "review_wall_seconds": round(sum(r.get("review_seconds") or 0 for r in rows), 3),
                     "evaluation_seconds": sum(r.get("evaluation_tool_seconds", 0) for r in rows)})
    pairs = []
    lookup = {(r["replicate"], r["arm"]): r for r in result["rows"]}
    for left, right, replicas in [("self_review", "catalog_only", range(1, 6)), ("catalog_only", "routed_analysis", range(1, 6))]:
        for replicate in replicas:
            a, b = lookup[replicate, left], lookup[replicate, right]
            pairs.append({"replicate": replicate, "left": left, "right": right,
                          "left_status": a.get("evaluation", {}).get("status", "not_evaluated"),
                          "right_status": b.get("evaluation", {}).get("status", "not_evaluated"),
                          "scope": "known_regression_local_claim_not_whole_task"})
    summary = {"source_sha256": c.sha(folder / "final-results.json"),
               "protocol_sha256": result["protocol_sha256"], "attempts": result["attempts"],
               "planned_slots": 15, "mother_cases": 1, "arms": arms, "pairs": pairs,
               "task_pass": None, "evaluation_role": c.REGRESSION_ROLE,
               "cost_notes": ["Cached tokens are part of input; reasoning tokens are not added again to output.",
                              "Reviewer wall time includes coordination; not independent human annotation time.",
                              "Historical initial-draft cost is excluded from these incremental revision costs.",
                              "Different lengths and caches; no equal-token or latency causal comparison."]}
    c.save(HERE / "summary.json", summary)
    with (HERE / "pairs.csv").open("x") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(pairs[0]))
        writer.writeheader()
        writer.writerows(pairs)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
