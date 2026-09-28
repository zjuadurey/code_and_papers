"""Terminal walkthrough: saved analysis, local hybrid execution, semantic checks."""

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from demo.hybrid_search import ROOT, load_original, run_hybrid
from qrefactorbench.evaluator.semantics import SemanticOracles

SAVED = ROOT / "pilot/baseline-v0.1/conditional-plan-diagnostic/parsed"


def label(value: bool | None) -> str:
    return {True: "YES", False: "NO", None: "UNCERTAIN"}[value]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a new JSON demo report (no overwrite)")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error("Output already exists; choose a new path to preserve earlier evidence")
    import qiskit

    print("QRefactorBench | 本地终端 DEMO | 非 benchmark 分数")
    print("分析/计划：已有模型输出回放；混合实现：本次 AI 辅助编写；执行：本地 Qiskit Statevector")
    print("本次无模型调用、无 QPU；不宣称加速或科学标签正确。\n")
    report = {"kind": "demo_not_benchmark", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "qiskit": qiskit.__version__,
              "model_calls": 0, "prediction_replays": {}, "execution_checks": [],
              "limitations": ["Saved predictions are not ground truth or fresh analysis.",
                              "Implementation is AI-assisted, not automatically generated from the plan.",
                              "One Grover iteration / 16 shots is a demo budget, not a success guarantee.",
                              "Exactness uses classical witness verification and exhaustive fallback.",
                              "Finite tests and simulator resources do not prove quantum advantage."]}
    for case_id in ("pilot-001", "pilot-002"):
        path = SAVED / f"{case_id}.json"
        prediction = json.loads(path.read_text())
        report["prediction_replays"][case_id] = prediction
        print(f"{'=' * 66}\n{case_id} | WHERE / WHETHER / HOW [历史输出回放]")
        source = ROOT / "cases/pilot" / case_id / "program.py"
        for line, text in enumerate(source.read_text().splitlines(), 1):
            print(f" {line:>2}  {text}")
        spans = [f"{r['function']}:{r['start_line']}-{r['end_line']}"
                 for r in prediction["candidate_regions"]]
        print("WHERE:", ", ".join(spans) or "NONE")
        print(f"结构={label(prediction['structural_eligibility'])} | "
              f"实际适用={label(prediction['practical_suitability'])} | "
              f"建议={prediction['decision']}")
        print("计算意图:", prediction["computational_intent"])
        plan = prediction["plan"]
        if plan:
            print("条件 HOW:", plan["migration_family"], "/", plan["quantum_algorithm_family"])
            print("编码:", plan["input_encoding"])
            print("解码与语义义务:", plan["output_decoding"])
        else:
            print("HOW: null；保留原程序。")
        print()

    print("[实际执行] pilot-001 条件实现演示（原建议仍是 REMAIN_CLASSICAL）")
    original = load_original("pilot-001")
    oracle = SemanticOracles()
    scenarios = [("有解", 3, [[1], [2], [3]]),
                 ("无解：必须认证 false", 3, [[1], [-1]]),
                 ("空合取", 0, []), ("空子句", 0, [[]]),
                 ("重复文字/重言式", 2, [[1, 1], [2, -2]])]
    for name, n, clauses in scenarios:
        expected = original.has_assignment(n, clauses)
        trace = run_hybrid(n, clauses)
        check = oracle.evaluate({"kind": "deterministic_equality", "config": {"expected": expected}},
                                trace["output"])
        passed = check.passed is True and type(trace["output"]) is bool
        report["execution_checks"].append(dict(name=name, n=n, clauses=clauses,
                                               expected=expected, passed=passed, **trace))
        print(f"  {'PASS' if passed else 'FAIL'} {name}: classical={expected}, hybrid={trace['output']}; "
              f"quantum={trace['quantum_executed']}, fallback={trace['classical_fallback']}, "
              f"witness={trace['witness']}")
        if trace["resources"]:
            r = trace["resources"]
            print(f"       qubits={r['num_qubits']}, depth={r['depth']}, "
                  f"CX={r['two_qubit_gate_count']}, shots={r['shots']} [u/cx 分解，非硬件成本]")

    print("\n[实际执行] pilot-002 原经典实现；保留回调和顺序")
    events = [b"created", b"approved", b"closed"]
    seen = []
    digest = load_original("pilot-002").ledger_digest(events, lambda i, d: seen.append((i, d)))
    expected_digest = bytes(32)
    expected_calls = []
    for i, event in enumerate(events):
        expected_digest = hashlib.sha256(expected_digest + event).digest()
        expected_calls.append((i, expected_digest.hex()))
    retained = digest == expected_digest.hex() and seen == expected_calls
    report["classical_retention"] = {"passed": retained, "callback_count": len(seen),
                                     "callbacks": seen, "digest": digest, "transformed": False}
    print(f"  {'PASS' if retained else 'FAIL'} digest 一致，{len(seen)} 次回调内容/顺序一致；未量子化。")
    paths = [ROOT / "demo/hybrid_search.py", ROOT / "demo/run.py"]
    for case_id in ("pilot-001", "pilot-002"):
        paths.extend([SAVED / f"{case_id}.json", ROOT / "cases/pilot" / case_id / "program.py"])
    report["input_hashes"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in paths}
    success = retained and all(row["passed"] for row in report["execution_checks"])
    report["all_demo_checks_passed"] = success
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(f"\nJSON 报告: {args.output.resolve()}")
    print("\n" + ("DEMO PASS" if success else "DEMO FAIL") +
          " | 仅以上输入的运行验证；经典兜底成本必须计入，未建立量子优势。")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
