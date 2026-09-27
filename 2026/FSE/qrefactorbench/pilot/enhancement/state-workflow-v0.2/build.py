"""Prepare new local suites/claim controls without model calls or old-file writes."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

from claims import digest, evaluate, response_digest, seal_suite, development_feedback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / "state-workflow-v0.1"
REVIEW = HERE.parent / "lit009-review-v0.1"
CASE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-009"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path: Path, value: Any) -> None:
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def request(matrix: list[list[float]], rhs: list[float]) -> dict[str, Any]:
    return {"variables": [f"x{i}" for i in range(len(rhs))], "matrix": matrix, "rhs": rhs,
            "current": [0.0] * len(rhs), "mode": "solve", "residual_limit": 1.0}


def suite_requests() -> tuple[list[tuple[str, dict[str, Any]]], list[tuple[str, dict[str, Any]]]]:
    old = json.loads((REVIEW / "evidence/trace.json").read_text())
    development = [("dev-normal", old["normal_control"]["input"]),
                   ("dev-archived-five", old["archived_witness"]["input"]),
                   ("dev-reviewed-six", old["reviewer_sensitivity_probe"]["input"])]
    reserved = [
        ("reserved-row-swap", request([[0.0, 2.0], [4.0, 1.0]], [2.0, 5.0])),
        ("reserved-first-tie", request([[2.0, 1.0], [-2.0, 3.0]], [1.0, 2.0])),
        ("reserved-singular-zero", request([[0.0, 0.0], [0.0, 1.0]], [0.0, 1.0])),
        ("reserved-three-diagonal", request([[2.0, -0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 4.0]], [2.0, 6.0, 8.0])),
        ("reserved-three-later-maximum", request([[1.0, 0.0, 0.0], [2.0, 1.0, 0.0], [3.0, 0.0, 1.0]], [1.0, 2.0, 4.0])),
        ("reserved-empty-context", request([], [])),
    ]
    original = old["archived_witness"]["input"]
    signs = [[round(v / 2.5e307) for v in row] for row in original["matrix"]]
    for number, (scale, size) in enumerate(((2.3e307, 5), (2.7e307, 5), (2.9e307, 5), (2.4e307, 6), (2.6e307, 7))):
        matrix = [[scale * value for value in row] + [0.0] * (size - 5) for row in signs]
        for i in range(5, size):
            matrix.append([2.0 if j == i else 0.0 for j in range(size)])
        reserved.append((f"reserved-growth-{number}", request(matrix, [1.0] * size)))
    reserved.append(("reserved-reversed-rows", request(list(reversed(original["matrix"])), [1.0] * 5)))
    assert not {digest(r) for _, r in development} & {digest(r) for _, r in reserved}
    assert len({digest(r) for _, r in reserved}) == len(reserved)
    return development, reserved


def make_suites() -> tuple[dict[str, Any], dict[str, Any]]:
    audit = load_module("n046_trusted_trace", REVIEW / "audit.py")
    saved = json.loads((ROOT / "pilot/model_comparison/20260923-four-model-c-v0.1/pivot-witness/result.json").read_text())
    for relative, expected in saved["source_sha256"].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError("Protected original source changed")
    prior = {name: sys.modules.get(name) for name in ("common", "kernel", "program")}
    try:
        for name in prior:
            sys.modules[name] = load_module(name, CASE / f"{name}.py")
        suites = []
        for role, requests in zip(("development", "evaluator_reserved"), suite_requests()):
            entries = []
            for ident, value in requests:
                trace = audit.trace_request(sys.modules["program"], sys.modules["kernel"], value)
                entries.append({"id": ident, "input": value, "input_sha256": digest(value),
                                "outcome": trace["outcome"], "input_unchanged": trace["input_unchanged"],
                                "states": [{"indices": list(range(p["column"], len(value["rhs"]))),
                                            "values_repr": p["values"], "original": p["original"]}
                                           for p in trace["pivots"]]})
            suites.append(seal_suite(role, entries))
        return suites[0], suites[1]
    finally:
        for name, value in prior.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


INCLUSIVE = "all(values[i] >= values[k] for k in indices) and not any(values[j] == values[i] for j in indices if j < i)"
EXCLUSIVE = "all(values[i] >= values[k] for k in indices if k != i) and not any(values[j] == values[i] for j in indices if j < i)"
NAN_AWARE = "(isnan(values[indices[0]]) and i == indices[0]) or (not isnan(values[indices[0]]) and not isnan(values[i]) and all(isnan(values[k]) or values[i] >= values[k] for k in indices) and not any(values[j] == values[i] for j in indices if j < i))"


def interpretation(expression: str, *, ident: str = "literal", mode: str = "predicate", guard: str = "True") -> dict[str, Any]:
    return {"id": ident, "meaning": "Execute the explicitly transcribed expression on absolute pivot values.",
            "mode": mode, "expression": expression, "guard": guard,
            "outside_guard": "classical_fallback_declared" if guard != "True" else "unresolved"}


def bind(raw: str, interpretations: list[dict[str, Any]], *, origin: str = "synthetic_control",
         resolution: str = "transcribed") -> dict[str, Any]:
    return {"version": "0.2", "response_sha256": response_digest(raw), "scope": "lit009_pivot_selection",
            "origin": origin, "reviewer": {"identity": "Codex coordinator", "status": "AI_REVIEW_PENDING"},
            "anchors": [{"pointer": "/plan/formulation", "quote": json.loads(raw)["plan"]["formulation"]}],
            "resolution": resolution, "rationale": "Explicit reviewer transcription; no automatic prose-equivalence proof.",
            "interpretations": interpretations}


def controls() -> dict[str, tuple[str, dict[str, Any]]]:
    recipes = {
        "nan_aware_predicate": interpretation(NAN_AWARE),
        "equivalent_ordered_scan": interpretation("values[candidate] > values[incumbent]", mode="ordered_scan"),
        "inclusive_bug": interpretation(INCLUSIVE),
        "exclusive_bug": interpretation(EXCLUSIVE),
        "missing_tie": interpretation("all(isnan(values[k]) or values[i] >= values[k] for k in indices)"),
        "last_tie_scan": interpretation("values[candidate] >= values[incumbent]", mode="ordered_scan"),
        "first_only": interpretation("i == indices[0]"),
        "guarded_finite": interpretation(INCLUSIVE, guard="all(isfinite(values[k]) for k in indices)"),
        "guard_always_false": interpretation(INCLUSIVE, guard="False"),
    }
    result = {}
    for name, claim in recipes.items():
        raw = json.dumps({"plan": {"formulation": f"SYNTHETIC CONTROL {name}: {claim['expression']}; guard: {claim['guard']}"}})
        result[name] = raw, bind(raw, [claim])
    for resolution in ("unsupported", "withdrawn"):
        raw = json.dumps({"plan": {"formulation": f"SYNTHETIC CONTROL: {resolution} mapping claim."}})
        result[resolution] = raw, bind(raw, [], resolution=resolution)
    return result


def build(output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    development, reserved = make_suites()
    output.mkdir(parents=True)
    save(output / "development.json", development)
    save(output / "evaluator-reserved.json", reserved)
    results = {}
    for name, (raw, binding) in controls().items():
        results[name] = {"development": evaluate(raw, binding, development),
                         "evaluator_reserved": evaluate(raw, binding, reserved)}
    save(output / "control-results.json", results)
    old = json.loads((REVIEW / "evidence/trace.json").read_text())
    raw_path = ROOT / old["provenance"]["response_path"]
    raw = raw_path.read_text()
    historical = bind(raw, [interpretation(INCLUSIVE, ident="including_self"),
                            interpretation(EXCLUSIVE, ident="excluding_self")],
                      origin="model_response", resolution="ambiguous")
    save(output / "historical-binding.json", historical)
    save(output / "historical-development.json", evaluate(raw, historical, development))
    save(output / "historical-reserved.json", evaluate(raw, historical, reserved))
    feedback = development_feedback(raw, historical, development)
    save(output / "historical-feedback.json", feedback)
    old_workflow = load_module("n046_previous_workflow", PREVIOUS / "workflow.py")
    analysis = old_workflow.analyze_source((CASE / "kernel.py").read_text(), "solve", 13)
    public_path = ROOT / "pilot/reference_completion/v0.1.1/review_inputs/lit-009-C.txt"
    prompt_records = []
    for arm, (use_a, use_v) in old_workflow.ARMS.items():
        observations = ([analysis] if use_a else []) + ([feedback] if use_v else [])
        prompt = old_workflow.revision_prompt(public_path.read_text(), raw, observations)
        path = output / f"{arm}.txt"
        path.write_text(prompt)
        prompt_records.append({"arm": arm, "path": path.name,
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                               "observation_kinds": [o["kind"] for o in observations],
                               "state": "awaiting_model_not_run", "new_model_calls": 0})
    save(output / "summary.json", {
        "development_requests": len(development["requests"]),
        "reserved_requests": len(reserved["requests"]),
        "development_states": sum(len(r["states"]) for r in development["requests"]),
        "reserved_states": sum(len(r["states"]) for r in reserved["requests"]),
        "requests_disjoint_by_canonical_json": True,
        "independent_mother_case_holdout": False, "new_model_calls": 0,
        "historical_analysis_is_post_hoc": True, "task_pass": None,
        "control_statuses": {k: {split: report["status"] for split, report in v.items()} for k, v in results.items()},
        "prompts": prompt_records,
    })
    print(json.dumps({"output": str(output), "development_requests": len(development["requests"]),
                      "reserved_requests": len(reserved["requests"]), "new_model_calls": 0}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    build(parser.parse_args().output)
