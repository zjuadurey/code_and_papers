"""Generate a fresh, local demonstration result; never submit a QPU/model job."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.metadata
import itertools
import json
import os
from pathlib import Path
import platform
import statistics
from time import perf_counter

import numpy as np
from qiskit import qasm2, transpile
from scipy.linalg import solve as scipy_solve

from demo.lit009_end_to_end import hybrid as h


def request(matrix, rhs=None):
    n = len(matrix)
    return dict(variables=[f"x{i}" for i in range(n)], matrix=matrix,
                rhs=[1.] * n if rhs is None else rhs, current=[0.] * n,
                mode="solve", residual_limit=1.)


def snapshot(value):
    return json.dumps(value, sort_keys=True, allow_nan=True)


def outcome(function, value):
    copied = deepcopy(value)
    before = snapshot(copied)
    try:
        result = {"return": function(copied)}
    except Exception as exc:
        result = {"exception": type(exc).__name__, "message": str(exc)}
    if snapshot(copied) != before:
        raise AssertionError("input mutation")
    return result


def fixtures():
    for i, values in enumerate(itertools.product((-1., 0., 1.), repeat=4)):
        yield f"matrix2-{i}", request([list(values[:2]), list(values[2:])], [1., 2.])
    traces = json.loads((h.ROOT / "pilot/enhancement/lit009-review-v0.1/evidence/trace.json").read_text())
    for key in ("normal_control", "archived_witness", "reviewer_sensitivity_probe"):
        yield key, traces[key]["input"]
    yield "empty", request([])
    data = request([[0., 0.], [0., 0.]])
    data["mode"] = "inspect"
    yield "inspect_singular", data
    for field, value in (("rhs", [True, 2]), ("matrix", [[1], [2]]),
                         ("current", [float("nan"), 0]), ("residual_limit", -1),
                         ("mode", "other"), ("variables", ["a", "a"]),
                         ("rhs", [10**400, 1])):
        data = request([[1., 0.], [0., 1.]])
        data[field] = value
        yield "invalid_"+field+str(type(value).__name__), data
    for sign in (-1, 1):
        data = request([[1e-308]], [float(sign)])
        data["current"] = [-sign * 1e308]
        yield f"delta_overflow_{sign}", data


def semantic_check():
    records = []
    routes = Counter()
    for name, value in fixtures():
        original = outcome(h.ORIGINAL.review, value)
        for seed in h.PROTOCOL["semantic_seeds"]:
            selector = h.PivotSelector(seed)
            actual = outcome(h.make_review(selector), value)
            passed = snapshot(actual) == snapshot(original)
            records.append(dict(case=name, seed=seed, passed=passed, outcome=actual))
            routes.update(event["route"] for event in selector.events)
    return {"comparisons": len(records), "passed": sum(r["passed"] for r in records),
            "routes": dict(routes), "records": records,
            "scope": "finite differential checks; not a whole-domain formal proof"}


def scipy_kernel(matrix, rhs):
    return scipy_solve(np.asarray(matrix), np.asarray(rhs), assume_a="gen",
                       check_finite=True).tolist()


def measure():
    """Warm-process API to complete report, no disk I/O/imports in timed region."""
    rows = []
    rng = np.random.default_rng(20260928)
    for n in h.PROTOCOL["benchmark_sizes"]:
        matrix = rng.integers(-3, 4, size=(n, n)).astype(float)
        matrix += np.eye(n) * (4*n)
        data = request(matrix.tolist(), rng.integers(-5, 6, size=n).astype(float).tolist())
        reference = h.ORIGINAL.review(data)
        events = []

        def hybrid_review(value):
            selector = h.PivotSelector(h.PROTOCOL["benchmark_seed"])
            answer = h.make_review(selector)(value)
            events[:] = selector.events
            return answer

        functions = {"original": h.ORIGINAL.review, "hybrid_simulator": hybrid_review,
                     "scipy_quality_only": h.replace_solver(scipy_kernel)}
        for function in functions.values():
            function(data)
        samples = {key: [] for key in functions}
        outputs = {}
        keys = list(functions)
        for repeat in range(h.PROTOCOL["benchmark_repeats"]):
            for key in keys[repeat % 3:] + keys[:repeat % 3]:
                batch = 1 if key == "hybrid_simulator" else h.PROTOCOL["classical_batch"]
                started = perf_counter()
                for _ in range(batch):
                    answer = functions[key](data)
                samples[key].append((perf_counter()-started)/batch)
                outputs[key] = answer
        median = {key: statistics.median(value) for key, value in samples.items()}
        solver_quality = {}
        for key, value in outputs.items():
            x = np.asarray(list(value["proposal"].values()))
            b = np.asarray(data["rhs"])
            denominator = np.linalg.norm(matrix, np.inf)*np.linalg.norm(x, np.inf)+np.linalg.norm(b, np.inf)
            solver_quality[key] = {"relative_backward_error": float(np.linalg.norm(matrix@x-b, np.inf)/denominator),
                                   "exact_report_match": snapshot(value) == snapshot(reference)}
        rows.append(dict(n=n, input=data, seconds_per_call=samples, median_seconds=median,
                         hybrid_over_original=median["hybrid_simulator"]/median["original"],
                         hybrid_over_scipy=median["hybrid_simulator"]/median["scipy_quality_only"],
                         quality=solver_quality, pivot_events=deepcopy(events)))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = perf_counter()
    semantics = semantic_check()
    if semantics["passed"] != semantics["comparisons"]:
        raise AssertionError("Semantic checks failed")
    timings = measure()
    resources = []
    for n in h.PROTOCOL["benchmark_sizes"]:
        values = [float(i) for i in range(n-1, -1, -1)]
        oracle, circuit = h.search_circuit(values)
        compiled = transpile(circuit, basis_gates=h.PROTOCOL["basis_gates"], optimization_level=0, seed_transpiler=0)
        measured = compiled.copy()
        measured.measure_all()
        (args.output / f"search-{n}.qasm").write_text(qasm2.dumps(measured)+"\n")
        (args.output / f"search-{n}.txt").write_text(str(measured.draw(output="text"))+"\n")
        resources.append(dict(active_rows=n, values=values, qubits=compiled.num_qubits,
                              oracle_predicate_evaluations=n, depth=compiled.depth(),
                              operations=dict(compiled.count_ops()), shots=4, measurements_per_shot=compiled.num_qubits,
                              total_gate_applications_four_shots=4*sum(compiled.count_ops().values()),
                              scope="logical u/cx, no coupling map/noise/QEC; classical compilation and certification additional"))
    result = dict(protocol=h.PROTOCOL, versions={p: importlib.metadata.version(p) for p in
                  ("qiskit", "numpy", "scipy", "pytest")}, python=platform.python_version(),
                  platform=platform.platform(), machine=platform.machine(), cpu_count=os.cpu_count(),
                  elapsed_seconds=perf_counter()-started, semantics=semantics, benchmarks=timings,
                  resources=resources, quantum_hardware_executed=False, new_model_calls=0,
                  source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                  (h.SOURCE/"kernel.py", h.SOURCE/"program.py", h.SOURCE/"common.py")})
    (args.output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    lines = ["# lit-009 本地端到端演示结果", "", "本轮为工程实现，非模型成绩；所有量子执行均为理想状态向量模拟。", "",
             f"整程序有限差分检查：{semantics['passed']}/{semantics['comparisons']}；包括返回值、异常类型/消息和输入不变。",
             "", "| n | 原程序 ms | hybrid 模拟器 ms | SciPy ms | hybrid/原程序 |", "|---|---:|---:|---:|---:|"]
    for row in timings:
        t = row["median_seconds"]
        lines.append(f"| {row['n']} | {t['original']*1000:.4f} | {t['hybrid_simulator']*1000:.4f} | {t['scipy_quality_only']*1000:.4f} | {row['hybrid_over_original']:.1f} |")
    lines.extend(["", "各项为7轮中位数；经典每轮100次摊销，hybrid每轮1次，轮换顺序，一次预热。",
                  "计入原程序输入校验、转换/AST装配、oracle合成、u/cx编译、模拟采样、经典认证/回退、完整报告；",
                  "不含进程启动、库导入、磁盘JSON序列化或最终证据导出。模块初始化成本不在本表。",
                  "SciPy/LAPACK沿用报告包装，但不保证逐位输出及异常合同一致，仅为质量层面的优化经典对照。",
                  "检查quality字段中的实际差异，不能把该列称为完整合同等价对比或领域最优基线。",
                  "", "结论：此有界实现包含线性oracle构造与必做的经典argmax认证，无端到端渐近加速依据。",
                  "模拟器时间不代表QPU时间；本报告不验证也不否定其它数据访问模型或量子算法的优势。",
                  "没有噪声、硬件运行、纠错资源或真机端到端性能证据。"])
    (args.output / "REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"output": str(args.output), "semantic_passed": semantics["passed"],
                      "semantic_total": semantics["comparisons"], "elapsed_seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
