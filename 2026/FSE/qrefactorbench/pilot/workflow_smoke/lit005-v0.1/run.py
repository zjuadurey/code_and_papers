"""One development case, actual QDK backend, no subagent/model/QPU calls."""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-005"
PRIOR = ROOT / "pilot/benefit_analysis/lit005-v0.1"
sys.path[:0] = [str(ROOT), str(CASE), str(PRIOR)]
import program
import kernel
from analysis import build_oracle, prefix_repair, assignments
from qrefactorbench.resource_workflow import analyze_resources


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_instance(request: dict):
    features = request["features"]
    clauses = [[(features.index(lit["feature"]), lit["enabled"]) for lit in r["any"]]
               for r in request["rules"]]
    locks = {features.index(k): v for k, v in request["locked"].items()}
    oracle = build_oracle(len(features), clauses, locks)
    k = len(oracle.free)
    if not 1 <= k <= 3 or oracle.constant is not None:
        raise ValueError("This smoke circuit requires 1..3 free variables and nonconstant CNF")
    gates = [("H", (i,)) for i in range(k)] + list(oracle.gates)
    gates += [("H", (i,)) for i in range(k)]
    gates += [("X", (i,)) for i in range(k)]
    if k == 1:
        gates.append(("Z", (0,)))
    else:
        gates += [("H", (k - 1,)), ("CX" if k == 2 else "CCX", tuple(range(k))),
                  ("H", (k - 1,))]
    gates += [("X", (i,)) for i in range(k)]
    gates += [("H", (i,)) for i in range(k)]
    names = {"H": "h", "X": "x", "Z": "z", "CX": "cx", "CCX": "ccx"}
    lines = ['OPENQASM 3.0;', 'include "stdgates.inc";',
             f'qubit[{oracle.width}] q;', f'bit[{k}] result;']
    lines += [f'{names[name]} ' + ', '.join(f'q[{i}]' for i in ids) + ';' for name, ids in gates]
    lines += [f'result[{i}] = measure q[{i}];' for i in range(k)]
    return oracle, clauses, locks, gates, '\n'.join(lines) + '\n'


def simulate(gates):
    """Sparse ideal state-vector simulation of the exact emitted primitive gates."""
    state = {0: 1.0}
    for name, ids in gates:
        new = defaultdict(float)
        for bits, amplitude in state.items():
            bit = 1 << ids[-1]
            if name == "H":
                new[bits & ~bit] += amplitude / math.sqrt(2)
                new[bits | bit] += amplitude / math.sqrt(2) * (-1 if bits & bit else 1)
            elif name == "Z":
                new[bits] += amplitude * (-1 if bits & bit else 1)
            else:
                target = bits ^ bit if all(bits & (1 << i) for i in ids[:-1]) else bits
                new[target] += amplitude
        state = {b: a for b, a in new.items() if abs(a) > 1e-14}
    assert abs(sum(a * a for a in state.values()) - 1) < 1e-10
    return {b: a * a for b, a in state.items()}


def check_semantics(request, oracle, clauses, locks, gates):
    k = len(oracle.free)
    probs = simulate(gates)
    assert all(b < (1 << k) for b in probs), "Ancillas not clean"
    expected = program.review(request)
    reference_complete = program.complete
    proposals = list(assignments(len(request["features"]), locks)) + [None]
    observations = []
    try:
        for proposed in proposals:
            calls = []
            def complete(n, c, fixed):
                calls.append(True)
                return prefix_repair(n, c, fixed, proposed)[0]
            program.complete = complete
            before = deepcopy(request)
            got = program.review(request)
            assert got == expected and request == before
            for mode, current in [('inspect', request['current']),
                                  ('complete', [False, True, True])]:
                calls.clear()
                quick = deepcopy(request)
                quick.update(mode=mode, current=current)
                program.review(quick)
                assert not calls, "Quantum callback used on fast path"
            observations.append({"sample": proposed, "output": got,
                                 "predicate_calls": prefix_repair(len(request['features']), clauses, locks, proposed)[1]})
    finally:
        program.complete = reference_complete
    outcomes = []
    first = kernel.complete(len(request['features']), clauses, locks)
    for bits, probability in sorted(probs.items()):
        decoded = [bool(bits & (1 << i)) for i in range(k)]
        outcomes.append({"feature_order_bits": decoded, "probability": probability,
                         "direct_output_matches_required_first": decoded == first})
    return {"reference_output": expected, "ideal_outcomes": outcomes,
            "arbitrary_witness_negative_control_rejected": any(not x['direct_output_matches_required_first'] for x in outcomes),
            "repaired_wrapper_all_samples_pass": True, "samples_checked": len(observations),
            "fast_paths_checked": 2 * len(observations), "repair_details": observations,
            "scope": "one development instance; all Boolean measurement outputs plus absent sample; no general-program proof"}


def measure(fn, repeats=1000):
    fn()
    samples = []
    for _ in range(7):
        start = time.perf_counter()
        for _ in range(repeats):
            fn()
        samples.append((time.perf_counter() - start) / repeats)
    return {"lower": min(samples), "upper": max(samples), "batch_means": samples,
            "source": "perf_counter: 7 batch means, descriptive range not confidence bound"}


def run(output: Path, python: str):
    output.mkdir(parents=True, exist_ok=False)
    def save(name, data):
        with (output / name).open('x') as file:
            json.dump(data, file, indent=2, sort_keys=True, allow_nan=False)
            file.write('\n')
    files = [CASE / name for name in ('program.py', 'kernel.py', 'common.py', 'public_task.json', 'example_request.json')]
    files += [PRIOR / 'analysis.py', ROOT / 'qrefactorbench/resource_workflow.py',
              ROOT / 'qrefactorbench/_qdk_resource_worker.py', HERE / 'protocol.json', Path(__file__)]
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in files}
    save('input-manifest.json', hashes)
    request = json.loads((CASE / 'example_request.json').read_text())
    oracle, clauses, locks, gates, qasm = compile_instance(request)
    (output / 'application.qasm').write_text(qasm)
    semantic = check_semantics(request, oracle, clauses, locks, gates)
    save('semantics.json', semantic)
    timing = {'classical_full_review': measure(lambda: program.review(request)),
              'circuit_construction': measure(lambda: compile_instance(request), repeats=200)}
    save('host-timings.json', timing)
    profiles = [{'id': f'hypothetical-{gate_ns}ns', 'gate_time_ns': gate_ns,
                 'measurement_time_ns': gate_ns * 5, 'error_rate': 1e-4,
                 'source': 'explicit hypothetical scenario; not calibrated user hardware'} for gate_ns in (100, 1000)]
    resource_request = {'version': 'resource-workflow-v0.1', 'plan_id': 'lit005-one-iteration-prefix-repair',
        'application': {'format': 'openqasm3', 'source': qasm,
                        'coverage': 'one uniform preparation, one clause-derived oracle, one diffusion, data measurement'},
        'profiles': profiles, 'max_error': 0.01}
    interval = lambda x: {k: x[k] for k in ('lower', 'upper', 'source')}
    context = {'application_sha256': hashlib.sha256(qasm.encode()).hexdigest(),
        'comparison_id': 'lit005-source-example-exact-first',
        'evidence_source': 'semantics.json finite checks; host-timings.json; no calibrated deployment overhead',
        'same_task': True, 'classical_seconds': interval(timing['classical_full_review']),
        'overheads_seconds': {'preparation': interval(timing['circuit_construction']),
                             'classical_control': None, 'communication': None, 'readout_decode': None,
                             'validation_fallback': None, 'compilation_amortized': None},
        'quantum_executions': 1, 'max_failure_probability': 0,
        'algorithm_failure_bound': 0}
    save('resource-request.json', resource_request)
    save('controller-context.json', context)
    result = analyze_resources(resource_request, context, python=python, timeout=60)
    save('resource-analysis.json', result)
    statuses = [r['status'] for r in result['estimation_runs']]
    success = all(s == 'ok' for s in statuses) and bool(result['points'])
    # The inequality follows from unchanged mandatory predicate work, not from
    # QDK output or a fabricated complete timing number. Keep evidence separate.
    report = {'workflow_status': 'completed' if success else 'backend_incomplete',
        'proposal_source': 'current assistant session; no independent model run; negative control deliberately authored',
        'case': 'lit-005 v0.1.1', 'case_instances': 1, 'logical_qubits': oracle.width,
        'unitary_gates': len(gates), 'measurement_count': len(oracle.free),
        'backend_statuses': statuses, 'resource_points': len(result['points']),
        'decision': 'retain_classical_for_this_serial_prefix_repair_plan',
        'decision_evidence': 'Mandatory prefix checking retains the same-domain classical search work; quantum costs are additional and nonnegative. N-061 REPORT section 4 gives scoped proof.',
        'cost_model_status': 'complete list of terms; uncalibrated terms unknown, no numerical end-to-end advantage claim',
        'quality_model_limit': 'Current backend comparison propagates physical error conservatively; it does not model exact classical repair eliminating candidate-output errors. Do not relax contract to 1%.',
        'scope': 'Only this plan; no universal claim against all quantum algorithms or future hardware.',
        'environment': {'python': sys.version, 'platform': platform.platform(),
                        'qdk': importlib.metadata.version('qdk'), 'pyqir': importlib.metadata.version('pyqir')},
        'next_step': 'Compare alternative certificate/minimum-finding plans and a competitive classical solver; independently test LLM harness later.'}
    if any(digest(ROOT / p) != h for p, h in hashes.items()):
        raise RuntimeError('Input/adapter changed during run; outputs retained but not finalized')
    save('summary.json', report)
    save('output-manifest.json', {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()})
    print(json.dumps(report, indent=2))
    return 0 if success else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--qdk-python', default=sys.executable)
    args = parser.parse_args()
    raise SystemExit(run(args.output, args.qdk_python))
