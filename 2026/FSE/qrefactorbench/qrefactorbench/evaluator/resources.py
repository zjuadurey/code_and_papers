"""Local Qiskit circuit inspection, separate from semantics and advantage claims."""

from typing import Any

from . import Check, strict_conjunction


def extract_resources(circuit: Any, *, shots: int | None = None,
                      representation: str = "as_supplied") -> dict[str, Any]:
    """Count the supplied static circuit, not a silently transpiled decomposition.

    operation_count includes directives; gate_count uses Qiskit's Gate type.
    Depth uses Qiskit's default filter. Dynamic control flow has no well-defined
    static cost here, so counts/depth are null rather than misleading estimates.
    """
    from qiskit import QuantumCircuit
    from qiskit.circuit import ControlFlowOp, Gate

    if not isinstance(circuit, QuantumCircuit):
        raise TypeError("Expected qiskit.QuantumCircuit")
    if shots is not None and (type(shots) is not int or shots <= 0):
        raise ValueError("shots must be a positive integer or None")
    dynamic = any(isinstance(instruction.operation, ControlFlowOp) for instruction in circuit.data)
    operations = [instruction.operation for instruction in circuit.data]
    counts = dict(sorted(circuit.count_ops().items()))
    return {
        "representation": representation, "num_qubits": circuit.num_qubits,
        "depth": None if dynamic else circuit.depth(),
        "operation_count": None if dynamic else sum(counts.values()),
        "gate_count": None if dynamic else sum(isinstance(op, Gate) for op in operations),
        "two_qubit_gate_count": None if dynamic else sum(isinstance(op, Gate) and op.num_qubits == 2 for op in operations),
        "measurement_count": None if dynamic else counts.get("measure", 0),
        "shots": shots, "top_level_operations": counts,
        "limitations": ["Counts refer to the supplied representation, not physical hardware cost."]
        + (["Dynamic control flow requires an explicit resource model."] if dynamic else []),
    }


def check_resource_limits(metrics: dict[str, Any] | None,
                          expectations: dict[str, Any] | None) -> Check:
    """Only explicit upper bounds are evaluated; overhead assumptions need review."""
    if metrics is None or expectations is None or not expectations.get("limits"):
        return Check(None, "No measured resources or no annotated numeric limits")
    results: list[bool | None] = []
    missing: list[str] = []
    failed: list[str] = []
    for name, limit in expectations["limits"].items():
        value = metrics.get(name)
        if value is None:
            missing.append(name)
            results.append(None)
        else:
            passed = value <= limit
            results.append(passed)
            if not passed:
                failed.append(name)
    return Check(strict_conjunction(results), f"Exceeded: {failed}; unmeasured: {missing}; checks cover numeric limits only")

