"""Offline N-049 evidence crosswalk and prompt design; contains no model transport."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = HERE.parent / "state-workflow-v0.3"
CAMPAIGN = OLD / "campaign"
EXECUTION = OLD / "execution-20260926"
CASE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-009"
TASK = ROOT / "pilot/reference_completion/v0.1.1/review_inputs/lit-009-C.txt"
WORKFLOW = HERE.parent / "state-workflow-v0.1/workflow.py"

# Coordinator-authored design categories, not new correctness labels or an NLP classifier.
GROUPS = {
    "missing_rule": ["01-initial", "01-analysis_only", "01-verification_only",
                     "03-verification_only", "03-analysis_and_verification"],
    "no_nomination": ["03-initial", "03-self_review", "03-analysis_only"],
    "broad_region_no_plan": ["04-initial", "04-self_review", "04-analysis_only",
                             "04-analysis_and_verification"],
    "qubo_not_constructed": ["05-initial", "05-self_review", "05-verification_only"],
    "ambiguous_operator": ["02-self_review", "05-analysis_only"],
    "explicit_local_rule": ["01-self_review", "01-analysis_and_verification", "02-initial",
                            "02-analysis_only", "02-verification_only",
                            "02-analysis_and_verification", "04-verification_only",
                            "05-analysis_and_verification"],
}
QUESTIONS = {
    "missing_rule": "若继续主张这份映射，请在既有plan字段写明候选域、读取的程序状态、实际比较规则或更新步骤、初始值、遍历与并列规则；仅重述原程序目标不等于给出构造。尚未解决的部分可明确保留未知。",
    "no_nomination": "目前没有候选；如需进一步分析，可给出公开源码中的分析范围及理由，也可保留无候选和不确定性。分析请求不等于认可可迁移性，不要求补造映射。",
    "broad_region_no_plan": "请区分供分析的函数范围与实际提出改写的计算。若尚无具体映射，可以只保留分析范围和未决问题；不要把函数边界调整计为语义修复。",
    "qubo_not_constructed": "若继续主张该QUBO，请给出变量域、目标及系数的构造、约束与罚项界、解码和并列规则、输入表示及适用条件；未构造的部分保持未知，不要求改成另一家族。",
    "ambiguous_operator": "请用明确运算符、量词范围和状态适用条件替代有多种解释的比较措辞；说明声明的是主要方案还是补充主张。不要由审核者代选一种解释。",
    "explicit_local_rule": "已有可转录的局部规则；无需为提高覆盖而补问。保留其条件、反例或有限通过结果，并分别记录实现、回退和成本的未决义务。",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pointer(document: Any, path: str) -> Any:
    for part in path.lstrip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        document = document[int(part)] if isinstance(document, list) else document[part]
    return document


def without_witness(feedback: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(feedback)
    for interpretation in result["interpretations"]:
        interpretation.pop("first_counterexample", None)
    return result


def build(output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    inputs: dict[str, str] = {}

    def read(path: Path) -> str:
        data = path.read_bytes()
        inputs[str(path.relative_to(ROOT))] = sha(data)
        return data.decode()

    def load(path: Path) -> Any:
        return json.loads(read(path))

    def save(name: str, value: Any) -> None:
        with (output / name).open("x") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")

    read(WORKFLOW)
    spec = importlib.util.spec_from_file_location("offline_revision_format", WORKFLOW)
    assert spec and spec.loader
    workflow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workflow)
    groups = {slot: group for group, slots in GROUPS.items() for slot in slots}
    assert len(groups) == sum(map(len, GROUPS.values())) == 25
    rows = load(EXECUTION / "row-audit.json")
    assert set(groups) == {row["slot"] for row in rows}
    mapped = []
    for row in rows:
        slot = row["slot"]
        raw = read(CAMPAIGN / "runs/gpt-5.6-sol" / slot / "response.txt")
        document = json.loads(raw)
        review_path = (CAMPAIGN / "reviews" / slot / "review.json" if row["arm"] == "initial"
                       else CAMPAIGN / "final-bindings" / f"{slot}.json")
        review = load(review_path)
        binding = review["binding"]
        assert review["response_sha256"] == binding["response_sha256"] == sha(raw.encode())
        assert binding["resolution"] == row["binding_resolution"]
        for anchor in binding["anchors"]:
            assert pointer(document, anchor["pointer"]) == anchor["quote"]
        mapped.append({**row, "design_category": groups[slot],
                       "review_path": str(review_path.relative_to(ROOT)),
                       "response_sha256": review["response_sha256"],
                       "anchors": binding["anchors"], "review_rationale": binding["rationale"],
                       "proposed_clarification_not_sent": QUESTIONS[groups[slot]],
                       "main_qubo_unverified": slot.startswith("05-"),
                       "review_status": "AI_REVIEW_PENDING"})
    save("response-crosswalk.json", mapped)

    sources = {name: read(CASE / name) for name in ["program.py", "kernel.py", "common.py"]}
    outline = {name: [{"name": node.name, "start_line": node.lineno,
                       "end_line": node.end_lineno,
                       "body_statements": [{"syntax": type(s).__name__, "line": s.lineno,
                                            "end_line": s.end_lineno} for s in node.body]}
                      for node in ast.parse(source).body
                      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
               for name, source in sources.items()}
    save("public-source-outline.json", {"status": "syntax_only_not_candidate_discovery",
                                          "files": outline})
    probes = []
    original = read(TASK)
    slots = []
    # Round-robin ordering of the three shared arms, one extra witness arm only where one exists.
    arms = ["self_review", "cue_only", "assessment_summary"]
    for replicate in range(1, 6):
        initial = f"{replicate:02d}-initial"
        raw = read(CAMPAIGN / "runs/gpt-5.6-sol" / initial / "response.txt")
        observations = load(CAMPAIGN / "reviews" / initial / "observations.json")
        feedback = observations["verification"]
        scope = {"kind": "scope_notice", "scope": feedback["scope"]}
        summary = without_witness(feedback)
        summary.pop("scope")
        full = deepcopy(feedback)
        full.pop("scope")
        payloads = {"self_review": [], "cue_only": [scope], "assessment_summary": [scope, summary]}
        witnesses = [i for i in full["interpretations"] if i.get("first_counterexample") is not None]
        if witnesses:
            payloads["with_witness"] = [scope, full]
            assert without_witness(full) == summary
        order = arms[(replicate - 1) % 3:] + arms[:(replicate - 1) % 3]
        if witnesses:
            order.insert(0, "with_witness")  # Predeclared, not randomized or balanced for n=1.
        for arm in order:
            prompt = workflow.revision_prompt(original, raw, payloads[arm])
            name = f"{replicate:02d}-{arm}.txt"
            with (output / name).open("x") as stream:
                stream.write(prompt)
            slots.append({"id": name[:-4], "initial": initial, "arm": arm,
                          "prompt": name, "prompt_sha256": sha(prompt.encode()),
                          "initial_sha256": sha(raw.encode()), "observations": payloads[arm],
                          "state": "design_not_run", "attempt_limit_proposed": 1})
        for region in observations["analysis"]["regions"]:
            declared = region["declared_region"]
            tree = ast.parse(sources[declared["file"]])
            nodes = [n for n in ast.walk(tree) if isinstance(n, ast.stmt)
                     and n.lineno == declared["start_line"]]
            probes.append({"initial": initial, "declared_region": declared,
                           "legacy_status": region["inventory"].get("status", "inventory_returned"),
                           "legacy_reason": region["inventory"].get("reason"),
                           "syntax_at_start": [{"type": type(n).__name__, "end_line": n.end_lineno}
                                               for n in nodes],
                           "proposed_routing": "retain_original_span_and_offer_syntax_outline"})
        if not observations["analysis"]["regions"]:
            probes.append({"initial": initial, "declared_region": None,
                           "legacy_status": "empty_inventory_from_empty_nomination",
                           "proposed_routing": "public_function_outline_only_no_automatic_nomination"})
    assert len(slots) == 16
    assert Counter(s["arm"] for s in slots) == {
        "self_review": 5, "cue_only": 5, "assessment_summary": 5, "with_witness": 1}
    save("candidate-routing-audit.json", probes)
    save("prompt-design.json", {"status": "DRAFT_OFFLINE_NOT_EXECUTABLE_PROTOCOL",
                               "run_authorization": None, "maximum_new_calls_proposed": 16,
                               "model_proposed": "gpt-5.6-sol", "reasoning_effort_proposed": "medium",
                               "timeout_seconds_proposed": 600, "retries_proposed": 0,
                               "slots": slots})
    save("source-manifest.json", inputs)
    summary_result = {"responses_mapped": len(mapped),
                      "categories": dict(Counter(r["design_category"] for r in mapped)),
                      "anchors_checked": sum(len(r["anchors"]) for r in mapped),
                      "initial_routes": len(probes), "draft_prompts": len(slots),
                      "new_model_calls": 0, "effect_on_model_quality": None,
                      "source_files_hashed": len(inputs)}
    save("summary.json", summary_result)
    return summary_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True, help="New directory; refuses overwrite")
    args = parser.parse_args()
    print(json.dumps(build(args.output), ensure_ascii=False, indent=2))
