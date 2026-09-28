"""Optional dependency tests can run independently in an existing Qiskit/YAML env."""

import pytest

from qrefactorbench.evaluator.resources import extract_resources
from qrefactorbench.loader import DataError, load_document


def test_real_qiskit_resources():
    qiskit = pytest.importorskip("qiskit")
    circuit = qiskit.QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.barrier()
    circuit.measure([0, 1], [0, 1])
    result = extract_resources(circuit, shots=128)
    assert result["num_qubits"] == 2
    assert result["depth"] == 3
    assert result["operation_count"] == 5  # barrier included
    assert result["gate_count"] == 2
    assert result["two_qubit_gate_count"] == 1  # two-qubit barrier excluded
    assert result["measurement_count"] == 2
    assert result["shots"] == 128
    assert extract_resources(qiskit.QuantumCircuit(0))["depth"] == 0
    with pytest.raises(ValueError):
        extract_resources(circuit, shots=True)


def test_dynamic_circuit_does_not_report_false_static_costs():
    qiskit = pytest.importorskip("qiskit")
    circuit = qiskit.QuantumCircuit(1, 1)
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.x(0)
    result = extract_resources(circuit)
    assert result["depth"] is None
    assert result["gate_count"] is None
    assert result["operation_count"] is None


@pytest.mark.parametrize("suffix,text", [(".json", '{"a": 1, "a": 2}'), (".json", '{"a": NaN}')])
def test_json_ambiguities_are_rejected(tmp_path, suffix, text):
    path = tmp_path / ("input" + suffix)
    path.write_text(text)
    with pytest.raises(DataError):
        load_document(path)


def test_yaml_round_trip_and_duplicate_rejection(tmp_path):
    pytest.importorskip("yaml")
    path = tmp_path / "input.yaml"
    path.write_text("case_id: example\nunknown: null\nboolean: false\n")
    assert load_document(path) == {"case_id": "example", "unknown": None, "boolean": False}
    for bad in ("a: 1\na: 2\n", "a: .nan\n", "date: 2026-09-18\n", "1: text\n", "a: &a [*a]\n"):
        path.write_text(bad)
        with pytest.raises(DataError):
            load_document(path)
