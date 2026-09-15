import pytest
from qiskit.circuit.library import CXGate
from htp.abstract_state import K0,K1,Q
from htp.gate_semantics import transfer

@pytest.mark.parametrize('before,after', [([K0,K0],[K0,K0]),([K0,K1],[K0,K1]),([K0,Q],[K0,Q]),([K1,K0],[K1,K1]),([K1,K1],[K1,K0]),([K1,Q],[K1,Q]),([Q,K0],[Q,Q]),([Q,K1],[Q,Q]),([Q,Q],[Q,Q])])
def test_cx(before,after):
    transfer(before,CXGate(),[0,1]); assert before==after
