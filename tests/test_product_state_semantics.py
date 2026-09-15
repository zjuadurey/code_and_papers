import numpy as np
import pytest
from qiskit.circuit import Parameter, Gate
from qiskit.circuit import library as l
from htp.product_state_model import ProductStateModel


@pytest.mark.parametrize('gate', [l.HGate(), l.RXGate(.4), l.RYGate(.6), l.RZGate(.2), l.SGate(), l.TGate(), l.UGate(.3,.4,.5)])
def test_local_unitaries_never_physicalize(gate):
    m=ProductStateModel(1)
    m.step(gate,[0]); assert m.q_physical==0


def test_hh_canonicalization_and_symbolic():
    m=ProductStateModel(1)
    m.step(l.HGate(),[0]); assert m.cells[0].label=='P'
    m.step(l.HGate(),[0]); assert m.cells[0].label=='K0' and m.q_logical==1
    m.step(l.RXGate(Parameter('theta')),[0]); assert m.cells[0].label=='P'
    m.step(l.HGate(),[0]); assert m.q_physical==0 and m.cells[0].vector is None


def test_swap_moves_mapping_not_dimensions():
    m=ProductStateModel(3)
    m.step(l.HGate(),[0]); m.step(l.CXGate(),[0,1])
    slot=m.cells[0].physical_slot
    m.step(l.SwapGate(),[0,2])
    assert m.q_physical==2 and m.cells[0].label=='K0'
    assert m.cells[2].physical_slot==slot


def test_spoofed_name_not_basis_proof():
    m=ProductStateModel(2)
    m.step(Gate('cz',2,[]),[0,1])
    assert m.q_physical==2
