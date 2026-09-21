"""Run context-001 with a sampled QAOA solver instead of exact enumeration.

This bounded prototype may fail the original exact/tie contract. It never repairs
the answer using the original solver; verification is external in run_comparison.
"""

import json
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

from demo.context001_qiskit.maintenance import compare_assignments, evaluate_windows, prepare_request
from qrefactorbench.evaluator.resources import extract_resources

PROTOCOL = json.loads(Path(__file__).with_name("protocol.json").read_text())


def cost_layer(matrix: list[list[int]], gamma: float) -> QuantumCircuit:
    """Implement exp(-i gamma H/W) up to global phase using RZZ rotations."""
    n = len(matrix)
    total = sum(matrix[i][j] for i in range(n) for j in range(i + 1, n))
    circuit = QuantumCircuit(n)
    if total:
        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j]:
                    circuit.rzz(gamma * matrix[i][j] / total, i, j)
    return circuit


def circuit_for(matrix: list[list[int]], angles: np.ndarray) -> QuantumCircuit:
    n = len(matrix)
    circuit = QuantumCircuit(n)
    circuit.h(range(n))
    circuit.compose(cost_layer(matrix, float(angles[0])), inplace=True)
    circuit.rx(2 * float(angles[1]), range(n))
    return circuit


def cost_operator(matrix: list[list[int]]) -> SparsePauliOp:
    n = len(matrix)
    total = sum(matrix[i][j] for i in range(n) for j in range(i + 1, n))
    terms = [("I" * n, 0.5 if total else 0.0)]
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j]:
                label = ["I"] * n
                label[n - 1 - i] = label[n - 1 - j] = "Z"
                terms.append(("".join(label), matrix[i][j] / (2 * total)))
    return SparsePauliOp.from_list(terms)


def select_sample(matrix: list[list[int]], counts: dict[str, int]) -> tuple[int, list[list[int]]]:
    """Qiskit counts print q_(n-1)..q_0; bit i maps to equipment input i."""
    n = len(matrix)
    if not counts or any(len(key) != n or set(key) - {"0", "1"} or value <= 0
                         for key, value in counts.items()):
        raise ValueError("Expected nonempty positive counts on all data qubits")
    masks = [int(key, 2) for key in counts]

    def cost(mask: int) -> int:
        return sum(matrix[i][j] for i in range(n) for j in range(i + 1, n)
                   if ((mask >> i) & 1) == ((mask >> j) & 1))

    mask = min(masks, key=lambda candidate: (cost(candidate), candidate))
    return mask, [[i for i in range(n) if ((mask >> i) & 1) == value] for value in (1, 0)]


def solve(matrix: list[list[int]]) -> tuple[list[list[int]], dict[str, Any]]:
    n = len(matrix)
    if n > PROTOCOL["max_qubits"]:
        raise ValueError("equipment must be a list of at most 16 names")
    total = sum(matrix[i][j] for i in range(n) for j in range(i + 1, n))
    if total > PROTOCOL["max_total_weight"]:
        raise NotImplementedError("Weight precision exceeds this floating-point prototype's declared domain")
    if not n:
        return [[], []], {"quantum_executed": False, "reason": "empty input", "counts": {},
                         "exact_fallback_used": False, "optimizer_evaluations": 0}
    operator = cost_operator(matrix)
    evaluations = []

    def objective(angles: np.ndarray) -> float:
        state = Statevector.from_instruction(circuit_for(matrix, angles))
        value = float(state.expectation_value(operator).real)
        evaluations.append({"angles": [float(a) for a in angles], "normalized_expectation": value})
        return value

    result = minimize(objective, PROTOCOL["initial_gamma_beta"], method=PROTOCOL["optimizer"],
                      options={"maxiter": PROTOCOL["maxiter"], "tol": PROTOCOL["optimizer_tolerance"]})
    circuit = circuit_for(matrix, result.x)
    state = Statevector.from_instruction(circuit)
    state.seed(PROTOCOL["seed"])
    counts = {str(key): int(value) for key, value in state.sample_counts(shots=PROTOCOL["shots"]).items()}
    mask, windows = select_sample(matrix, counts)
    measured = circuit.copy()
    measured.measure_all()
    return windows, {
        "quantum_executed": True, "simulation": "ideal statevector; final measurement sampled",
        "optimizer_objective": "exact simulator expectation, not shot-estimated or an optimum-reference lookup",
        "optimizer_success": bool(result.success), "optimizer_message": str(result.message),
        "optimizer_evaluations": int(result.nfev), "optimizer_trace": evaluations,
        "angles": [float(a) for a in result.x], "normalized_expectation": float(result.fun),
        "counts": counts, "selected_mask": mask, "shots": PROTOCOL["shots"], "seed": PROTOCOL["seed"],
        "probabilities_by_integer_mask": [float(value) for value in state.probabilities()],
        "circuit_text": str(measured.draw(output="text")),
        "resources": extract_resources(measured, shots=PROTOCOL["shots"],
                                       representation="logical h/rzz/rx plus equivalent terminal measurements"),
        "resources_scope": "final circuit only; optimizer statevector calls reported separately; no hardware transpilation",
        "exact_fallback_used": False,
    }


def review_schedule_with_trace(request: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    names, matrix, current_windows = prepare_request(request)
    current = evaluate_windows(names, matrix, current_windows)
    windows, trace = solve(matrix)
    proposed = evaluate_windows(names, matrix, windows)
    report = {"equipment_count": len(names), "requirement_count": len(request["requirements"]),
              "current": current, "proposed": proposed,
              "changes": compare_assignments(names, current, proposed)}
    return report, trace


def review_schedule(request: Any) -> dict[str, Any]:
    """Same output interface as the source; exact/tie preservation is not guaranteed."""
    return review_schedule_with_trace(request)[0]


if __name__ == "__main__":
    import sys
    print(json.dumps(review_schedule(json.load(sys.stdin)), indent=2))
