"""Bounded CNF search demonstration with an exact classical fallback.

The oracle is synthesized from clauses, not an enumerated truth table. This is
an AI-assisted implementation for inspection, not model-generated experiment output.
"""

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_original(case_id: str) -> ModuleType:
    """Load an explicitly selected, trusted local pilot source without editing it."""
    if case_id not in {"pilot-001", "pilot-002"}:
        raise ValueError("Only the two demonstration sources are supported")
    spec = importlib.util.spec_from_file_location(
        case_id, ROOT / "cases" / "pilot" / case_id / "program.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ORIGINAL = load_original("pilot-001")


def normalize_clauses(clauses: list[list[int]]) -> list[list[int]]:
    """Deduplicate literals and remove tautologies; retain empty clauses."""
    result = []
    for clause in clauses:
        literals = sorted(set(clause), key=lambda x: (abs(x), x))
        if not any(-literal in literals for literal in literals):
            result.append(literals)
    return result


def build_phase_oracle(n: int, clauses: list[list[int]]) -> Any:
    """Apply (-1)^satisfies to data states and return clause ancillas to zero.

Precondition: n >= 1; nonempty, normalized, non-tautological clauses with
distinct, valid literals. Each clause has one workspace qubit.
"""
    from qiskit import QuantumCircuit

    compute = QuantumCircuit(n + len(clauses))
    for index, clause in enumerate(clauses):
        target = n + index
        compute.x(target)
        positive = [literal - 1 for literal in clause if literal > 0]
        for qubit in positive:
            compute.x(qubit)
        compute.mcx([abs(literal) - 1 for literal in clause], target)
        for qubit in positive:
            compute.x(qubit)
    circuit = compute.copy()
    last = circuit.num_qubits - 1
    if len(clauses) == 1:
        circuit.z(last)
    else:
        circuit.h(last)
        circuit.mcx(list(range(n, last)), last)
        circuit.h(last)
    circuit.compose(compute.inverse(), inplace=True)
    return circuit


def build_search_circuit(n: int, clauses: list[list[int]]) -> Any:
    """One Grover iteration: a fixed demo budget, not an optimal search schedule."""
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(n + len(clauses))
    circuit.h(range(n))
    circuit.compose(build_phase_oracle(n, clauses), inplace=True)
    circuit.h(range(n))
    circuit.x(range(n))
    if n == 1:
        circuit.z(0)
    else:
        circuit.h(n - 1)
        circuit.mcx(list(range(n - 1)), n - 1)
        circuit.h(n - 1)
    circuit.x(range(n))
    circuit.h(range(n))
    return circuit


def run_hybrid(n: int, clauses: list[list[int]], *, seed: int = 7,
               shots: int = 16) -> dict[str, Any]:
    """Return exact Boolean behavior plus honest demonstration instrumentation.

Only plain, in-domain inputs of <= 6 data / <= 14 total qubits enter simulation.
Other inputs delegate to the original implementation, retaining its behavior.
No simulator runtime is interpreted as quantum performance.
"""
    if type(shots) is not int or shots <= 0:
        raise ValueError("shots must be a positive integer")
    trace: dict[str, Any] = {
        "seed": seed, "shots_requested": shots, "shots_executed": 0,
        "quantum_executed": False, "classical_fallback": False,
        "witness": None, "sampled_candidates": [], "resources": None,
    }

    def fallback(reason: str) -> dict[str, Any]:
        trace.update(reason=reason, classical_fallback=True,
                     output=ORIGINAL.has_assignment(n, clauses))
        return trace

    valid = (type(n) is int and 0 <= n <= 6 and type(clauses) is list
             and all(type(c) is list and all(type(x) is int and 0 < abs(x) <= n
                                            for x in c) for c in clauses))
    if not valid or n == 0:
        return fallback("Outside bounded simulation domain; original code executes")
    normalized = normalize_clauses(clauses)
    if not normalized or any(not clause for clause in normalized):
        return fallback("Empty/tautological formula or empty clause; original code executes")
    if n + len(normalized) > 14:
        return fallback("Demo statevector memory cap; original code executes")

    from qiskit import transpile
    from qiskit.quantum_info import Statevector
    from qrefactorbench.evaluator.resources import extract_resources

    circuit = build_search_circuit(n, normalized)
    state = Statevector.from_instruction(circuit)
    state.seed(seed)
    samples = [int(bits, 2) for bits in state.sample_memory(shots, qargs=list(range(n)))]
    # Measurements are sampled by Statevector; the circuit resource record
    # explicitly includes the equivalent terminal measurements.
    measured = circuit.copy()
    measured.measure_all()
    decomposed = transpile(measured, basis_gates=["u", "cx"], optimization_level=0)
    trace.update(
        quantum_executed=True, shots_executed=shots, sampled_candidates=samples,
        resources=extract_resources(decomposed, shots=shots,
                                    representation="u/cx, opt=0, all-qubit terminal measurement"),
    )
    for candidate in samples:
        if ORIGINAL.satisfies(candidate, clauses):
            trace.update(output=True, witness=candidate,
                         reason="Measured witness verified by original classical predicate")
            return trace
    return fallback("No verified sampled witness; exhaustive original code certifies result")


def has_assignment(n: int, clauses: list[list[int]]) -> bool:
    """Preserve the original public interface; instrumentation is separate."""
    return run_hybrid(n, clauses)["output"]
