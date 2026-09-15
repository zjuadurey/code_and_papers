import itertools
import pytest
from qiskit.circuit import library as l
from htp.abstract_state import K0,K1,Q
from htp.gate_semantics import transfer

@pytest.mark.parametrize('before',list(itertools.product([K0,K1,Q],repeat=2)))
@pytest.mark.parametrize('gate',[l.CZGate(),l.CPhaseGate(.3),l.CRZGate(.2),l.RZZGate(.8)])
def test_diagonal_controls(before,gate):
    s=list(before); transfer(s,gate,[0,1]); assert s==list(before)
