"""Portable integration smoke checks, runnable without pytest or installation.

Usage: python tests/test_packaging_integration.py
Requires all runtime extras; intended for an existing Qiskit/YAML environment.
"""

import json
import tempfile
from pathlib import Path


def main() -> None:
    import yaml
    from qiskit import QuantumCircuit

    from qrefactorbench.cli import evaluate
    from qrefactorbench.evaluator.resources import extract_resources
    from qrefactorbench.loader import load_document
    from qrefactorbench.schema import documents
    from qrefactorbench.validator import validate_dataset

    root = Path(__file__).resolve().parents[1]
    report = validate_dataset(root / "cases")
    assert report.valid and len(report.cases) == 14
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "case.yaml"
        _, case = report.cases[0]
        path.write_text(yaml.safe_dump(case), encoding="utf-8")
        assert load_document(path) == case
    result = evaluate(report, root / "examples/draft_predictions.json", True,
                      {c["case_id"] for _, c in report.cases if c["case_id"].startswith("toy-")})
    assert result["aggregate"]["end_to_end_quantumization_success"]["passed"] == 0
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    assert extract_resources(circuit)["two_qubit_gate_count"] == 1
    assert set(documents()) == {"case", "prediction", "migration_plan", "phase1_prediction"}
    print(json.dumps({"integration": "passed", "case_count": 14, "yaml_roundtrip": True,
                      "qiskit_real_circuit": True, "schema_count": 4}, sort_keys=True))


if __name__ == "__main__":
    main()
