import json
import pytest
from run import CASE, compile_instance, simulate, check_semantics


def test_full_grover_circuit_including_diffusion():
    request = json.loads((CASE / 'example_request.json').read_text())
    oracle, clauses, locks, gates, _ = compile_instance(request)
    result = simulate(gates)
    # Bit i is feature i: 2 = 010, 6 = 011 in feature order.
    assert result == pytest.approx({2: 0.5, 6: 0.5})
    verified = check_semantics(request, oracle, clauses, locks, gates)
    assert verified['arbitrary_witness_negative_control_rejected']
    assert verified['samples_checked'] == 9


def test_sample_circuit_has_explicit_measurements_and_no_answer_table():
    request = json.loads((CASE / 'example_request.json').read_text())
    _, _, _, _, qasm = compile_instance(request)
    assert qasm.count('measure') == 3
    assert 'ccx' in qasm and 'qubit[14]' in qasm


def test_constant_formula_not_sent_to_quantum_estimator():
    request = json.loads((CASE / 'example_request.json').read_text())
    request['rules'] = []
    with pytest.raises(ValueError, match='nonconstant'):
        compile_instance(request)
