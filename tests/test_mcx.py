import pytest
from qiskit.circuit.library import MCXGate, CCXGate
from htp.abstract_state import K0,K1,Q
from htp.gate_semantics import transfer

@pytest.mark.parametrize('gate,before,after',[(CCXGate(),[K0,Q,K1],[K0,Q,K1]),(CCXGate(),[K1,K1,K0],[K1,K1,K1]),(CCXGate(),[K1,K1,K1],[K1,K1,K0]),(MCXGate(3),[K1,Q,K0,K1],[K1,Q,K0,K1]),(MCXGate(3),[K1,Q,K1,K0],[Q,Q,Q,Q]),(MCXGate(2,ctrl_state=0),[K0,K0,K0],[K0,K0,K1]),(MCXGate(2,ctrl_state=0),[K1,Q,K0],[K1,Q,K0])])
def test_mcx(gate,before,after):
    transfer(before,gate,list(range(len(before)))); assert before==after

def test_multitarget_is_not_single_target_x():
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import MCMTGate,XGate
    from htp.validation import validate_prefixes
    from htp.loaders import semantic_circuit,lower
    from htp.gate_semantics import has_rule
    gate=MCMTGate(XGate(),2,2)
    assert not has_rule(gate)
    c=QuantumCircuit(4);c.h(0);c.x(1);c.append(gate,range(4))
    validate_prefixes(c)
    validate_prefixes(semantic_circuit(c))
    validate_prefixes(lower(c))
