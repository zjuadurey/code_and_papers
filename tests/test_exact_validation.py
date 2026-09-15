import pytest
from qiskit import QuantumCircuit, transpile
from htp.validation import random_validation_circuit, validate_prefixes
from htp.analyzer import analyze

@pytest.mark.parametrize('seed',range(20))
def test_random_exact(seed):
    assert validate_prefixes(random_validation_circuit(seed))['false_known_violations']==0

def test_validation_rejects_large():
    with pytest.raises(ValueError): validate_prefixes(QuantumCircuit(9))

def test_lowering_can_destroy_reversible_proof():
    c=QuantumCircuit(3); c.x(0); c.x(1); c.ccx(0,1,2)
    lowered=transpile(c,basis_gates=['h','t','tdg','cx','x'],optimization_level=0)
    assert analyze(c)['summary']['q_final']==0
    assert analyze(lowered)['summary']['q_final']>0
    validate_prefixes(lowered)
