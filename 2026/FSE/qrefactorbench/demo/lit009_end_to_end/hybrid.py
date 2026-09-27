"""Bounded executable lit-009 demo, with explicit classical certification cost.

No maximum is hard-coded into the quantum circuit. A classical truth-table
compiler still scans all data against a threshold; this is not a fast QRAM model.
Historical model plans are not replaced or credited with this engineering work.
"""
from __future__ import annotations

import ast
import json
import math
from pathlib import Path
from time import perf_counter
from types import FunctionType, ModuleType
from typing import Any, Callable

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-009"
PROTOCOL = json.loads((HERE / "protocol.json").read_text())


def load_sources() -> tuple[ModuleType, ModuleType]:
    """Load the three trusted files into isolated namespaces; no sys.modules patch."""
    common = ModuleType("lit009_common")
    kernel = ModuleType("lit009_kernel")
    program = ModuleType("lit009_program")
    for module, filename in ((common, "common.py"), (kernel, "kernel.py")):
        path = SOURCE / filename
        module.__file__ = str(path)
        exec(compile(path.read_text(), str(path), "exec"), module.__dict__)
    tree = ast.parse((SOURCE / "program.py").read_text())
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and node.module in {"common", "kernel"})]
    for name in ("fields", "finite", "names", "vector"):
        program.__dict__[name] = getattr(common, name)
    program.__dict__.update(solve=kernel.solve, residual=kernel.residual)
    exec(compile(tree, str(SOURCE / "program.py"), "exec"), program.__dict__)
    return kernel, program


KERNEL, ORIGINAL = load_sources()


def replace_solver(solver: Callable) -> Callable:
    namespace = dict(ORIGINAL.review.__globals__, solve=solver)
    return FunctionType(ORIGINAL.review.__code__, namespace, "review")


def phase_flip(circuit: QuantumCircuit, index: int) -> None:
    """Flip exactly one little-endian computational basis state's phase."""
    width = circuit.num_qubits
    zeros = [bit for bit in range(width) if not ((index >> bit) & 1)]
    for bit in zeros:
        circuit.x(bit)
    if width == 1:
        circuit.z(0)
    else:
        circuit.h(width - 1)
        circuit.mcx(list(range(width - 1)), width - 1)
        circuit.h(width - 1)
    for bit in zeros:
        circuit.x(bit)


def threshold_oracle(values: list[float], threshold: int) -> QuantumCircuit:
    """Classically synthesize predicate; no argmax and no favorable free lookup."""
    width = max(1, (len(values) - 1).bit_length())
    circuit = QuantumCircuit(width, name="threshold_oracle")
    for i, value in enumerate(values):
        if value > values[threshold] or (value == values[threshold] and i < threshold):
            phase_flip(circuit, i)
    return circuit


def search_circuit(values: list[float]) -> tuple[QuantumCircuit, QuantumCircuit]:
    oracle = threshold_oracle(values, len(values) - 1)
    circuit = QuantumCircuit(oracle.num_qubits)
    circuit.h(range(circuit.num_qubits))
    circuit.compose(oracle, inplace=True)
    circuit.h(range(circuit.num_qubits))
    phase_flip(circuit, 0)
    circuit.h(range(circuit.num_qubits))
    # This is one fixed Grover iteration, NOT a maximum-finding success guarantee.
    return oracle, circuit


class PivotSelector:
    def __init__(self, seed: int = 7, sampler: Callable | None = None):
        self.seed = seed
        self.sampler = sampler
        self.events: list[dict[str, Any]] = []

    def __call__(self, rows: list[list[float]], col: int, n: int) -> int:
        started = perf_counter()
        values = [abs(rows[i][col]) for i in range(col, n)]
        event: dict[str, Any] = {"col": col, "active_rows": len(values),
                                 "quantum_executed": False}
        self.events.append(event)
        reason = ("single_element" if len(values) == 1 else
                  "nonfinite" if not all(math.isfinite(v) for v in values) else
                  "size_limit" if len(values) > PROTOCOL["max_active_rows"] else None)
        if reason:
            result = max(range(col, n), key=lambda i: abs(rows[i][col]))
            event.update(route=reason, result=result, total_seconds=perf_counter()-started)
            return result
        build_start = perf_counter()
        try:
            oracle, circuit = search_circuit(values)
            built = perf_counter()
            compiled = transpile(circuit, basis_gates=PROTOCOL["basis_gates"],
                                 optimization_level=0, seed_transpiler=0)
        except Exception as exc:
            result = max(range(col, n), key=lambda i: abs(rows[i][col]))
            event.update(route="construction_error", result=result,
                         backend_error=f"{type(exc).__name__}: {exc}",
                         total_seconds=perf_counter()-started)
            return result
        compiled_at = perf_counter()
        error = None
        try:
            if self.sampler is None:
                state = Statevector.from_instruction(compiled)
                state.seed(self.seed + len(self.events))
                samples = [int(s, 2) for s in state.sample_memory(PROTOCOL["shots_per_pivot"])]
            else:
                samples = self.sampler(compiled, len(values))
            event["quantum_executed"] = self.sampler is None
            candidate = len(values) - 1
            for i in samples:
                if type(i) is not int or not 0 <= i < len(values):
                    continue
                if values[i] > values[candidate] or (values[i] == values[candidate] and i < candidate):
                    candidate = i
        except Exception as exc:
            # Bounded backend failure; original algorithm remains the fallback.
            samples, candidate = [], len(values) - 1
            error = f"{type(exc).__name__}: {exc}"
        sampled_at = perf_counter()
        exact = max(range(len(values)), key=values.__getitem__)
        result = col + exact
        certified_at = perf_counter()
        event.update(
            route="backend_error" if error else "certified" if candidate == exact else "fallback",
            samples=samples, candidate=col+candidate, result=result, backend_error=error,
            injected_sampler=self.sampler is not None,
            oracle_comparisons=len(values), certification_candidates=len(values),
            shots=PROTOCOL["shots_per_pivot"], oracle_calls_per_shot=1,
            qubits=compiled.num_qubits, depth=compiled.depth(),
            operations=dict(compiled.count_ops()), oracle_operations=dict(oracle.count_ops()),
            build_seconds=built-build_start, compile_seconds=compiled_at-built,
            simulation_and_decode_seconds=sampled_at-compiled_at,
            certification_seconds=certified_at-sampled_at,
            total_seconds=certified_at-started)
        return result


def make_review(selector: PivotSelector) -> Callable:
    """Replace only the pivot expression, keeping all surrounding statements."""
    tree = ast.parse((SOURCE / "kernel.py").read_text())
    matches = 0
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "pivot"):
            expected = "max(range(col, n), key=lambda i: abs(rows[i][col]))"
            if ast.dump(node.value) != ast.dump(ast.parse(expected, mode="eval").body):
                raise RuntimeError("Original pivot expression changed")
            node.value = ast.copy_location(ast.parse("_choose(rows, col, n)", mode="eval").body, node.value)
            matches += 1
    if matches != 1:
        raise RuntimeError("Expected one pivot assignment")
    namespace = dict(KERNEL.__dict__, _choose=selector)
    exec(compile(ast.fix_missing_locations(tree), str(SOURCE / "kernel.py"), "exec"), namespace)
    return replace_solver(namespace["solve"])


def main() -> None:
    import sys
    selector = PivotSelector()
    report = make_review(selector)(json.load(sys.stdin))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
