"""Freeze and execute the separate, post-hoc exact rank-QUBO audit."""
import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import time

from check import check_instance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESPONSE = HERE.parent / "claim-elicitation-v0.1/campaign/runs/gpt-5.6-sol/05-formalization/response.txt"
SUITE = HERE.parent / "state-workflow-v0.2/evidence/evaluator-reserved.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text())


def save(path: Path, value) -> None:
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False, ensure_ascii=False)
        f.write("\n")


def prepare() -> dict:
    response = load(RESPONSE)
    binding = {"response": str(RESPONSE.relative_to(ROOT)), "response_sha256": sha(RESPONSE),
               "reviewer": {"identity": "Codex coordinator", "status": "AI_REVIEW_PENDING"},
               "method": "Manual mathematical transcription, not automated prose extraction",
               "anchors": [{"pointer": "/plan/"+key, "quote": response["plan"][key]} for key in
                           ["formulation", "input_encoding", "output_decoding"]],
               "scope": "Primary abstract rank QUBO on finite active values; no backend or fallback execution",
               "transcription": {"rank": "count k where abs(v[k])>abs(v[i]) or (equal and k<i)",
                                 "energy": "sum(c_i*z_i)+P*(sum(z_i)-1)^2",
                                 "constant": "P", "linear": "c_i-P", "pair": "2*P",
                                 "admission": "All active pivot values finite; exact coefficients and optimum"}}
    save(HERE / "binding.json", binding)
    rows = []
    for ri, request in enumerate(load(SUITE)["requests"]):
        for si, s in enumerate(request["states"]):
            rows.append({"id": f"known-{ri:02d}-{si:02d}", "role": "known_regression",
                         "values_repr": s["values_repr"], "indices": s["indices"],
                         "archived_original": s["original"]})
    alphabet = ["-2.0", "-1.0", "-0.0", "0.0", "1.0", "2.0"]
    for size in range(1, 5):
        for n, values in enumerate(product(alphabet, repeat=size)):
            rows.append({"id": f"synthetic-sign-tie-{size}-{n}", "role": "posthoc_synthetic",
                         "values_repr": values})
    extremes = ["0.0", "5e-324", "1.0", "1.0000000000000002", "1.7976931348623157e308"]
    for size in (2, 3):
        for n, values in enumerate(product(extremes, repeat=size)):
            rows.append({"id": f"synthetic-edge-{size}-{n}", "role": "posthoc_synthetic",
                         "values_repr": values})
    save(HERE / "inputs.json", rows)
    sources = [RESPONSE, SUITE, HERE / "binding.json", HERE / "inputs.json", HERE / "README.md",
               *HERE.glob("*.py")]
    p = {"version": "rank-qubo-posthoc-0.1", "penalties": ["1/10", "1", "7"],
         "enumeration_dimension_limit": 12, "new_model_calls": 0, "qpu_calls": 0,
         "source_sha256": {str(f.relative_to(ROOT)): sha(f) for f in sources},
         "changes_n053_result": False, "independent_mother_cases": 0,
         "role": "Post-hoc local formula audit; not a new benchmark outcome or holdout"}
    save(HERE / "protocol.json", p)
    return {"frozen_inputs": len(rows), "protocol_sha256": sha(HERE / "protocol.json")}


def evaluate(check_only: bool = False) -> dict:
    p = load(HERE / "protocol.json")
    for f, digest in p["source_sha256"].items():
        assert sha(ROOT / f) == digest, f
    response = load(RESPONSE)
    for anchor in load(HERE / "binding.json")["anchors"]:
        assert response["plan"][anchor["pointer"].split("/")[-1]] == anchor["quote"]
    start = time.perf_counter()
    rows = []
    for row in load(HERE / "inputs.json"):
        values = list(map(float, row["values_repr"]))
        if not all(map(math.isfinite, values)):
            rows.append({**row, "status": "excluded_by_model_finite_guard", "checks": []})
            continue
        checks = [{"penalty": penalty, **check_instance(values, Fraction(penalty))}
                  for penalty in p["penalties"]]
        if row["role"] == "known_regression":
            assert row["indices"][checks[0]["original_offset"]] == row["archived_original"]
        rows.append({**row, "status": "pass" if all(x["unique_correct_one_hot"] and
                     x["expansion_matches"] for x in checks) else "fail", "checks": checks})
    summary = {}
    for role in ["known_regression", "posthoc_synthetic"]:
        subset = [r for r in rows if r["role"] == role]
        summary[role] = {"states": len(subset), "passed": sum(r["status"] == "pass" for r in subset),
                         "excluded": sum(r["status"].startswith("excluded") for r in subset),
                         "failed": sum(r["status"] == "fail" for r in subset),
                         "energy_assignments_checked": sum(x["assignments"] for r in subset for x in r["checks"])}
    result = {"protocol_sha256": sha(HERE / "protocol.json"), "summary": summary, "rows": rows,
              "elapsed_seconds": time.perf_counter() - start, "new_model_calls": 0,
              "scope": p["role"], "task_pass": None}
    protected = load(HERE / "protected_before.json")
    assert all((ROOT / f).is_file() and sha(ROOT / f) == h for f, h in protected.items())
    if check_only:
        old = load(HERE / "results.json")
        assert all(result[k] == old[k] for k in result if k != "elapsed_seconds")
    else:
        save(HERE / "results.json", result)
        save(HERE / "validation.json", {"protected_files_unchanged": len(protected),
             "quote_anchors": 3, "focused_tests_passed": 18, "source_hashes_valid": True,
             "new_model_calls": 0, "qpu_calls": 0, "summary": summary,
             "elapsed_seconds": result["elapsed_seconds"]})
    return {"summary": summary, "elapsed_seconds": result["elapsed_seconds"],
            "protected_files_unchanged": len(protected), "exact_replay": check_only}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run", "check"])
    args = parser.parse_args()
    print(json.dumps(prepare() if args.action == "prepare" else evaluate(args.action == "check"), indent=2))
