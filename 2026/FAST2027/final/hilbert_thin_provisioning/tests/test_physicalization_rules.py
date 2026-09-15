import pytest
from qiskit.circuit import library as l
from htp.product_state_model import ProductStateModel


@pytest.mark.parametrize('bit',[0,1])
def test_basis_control(bit):
    m=ProductStateModel(2)
    if bit: m.step(l.XGate(),[0])
    m.step(l.HGate(),[1]); m.step(l.CXGate(),[0,1])
    assert m.q_physical==0


def test_cx_bell_batch():
    m=ProductStateModel(2); m.step(l.HGate(),[0])
    e=m.step(l.CXGate(),[0,1])
    assert e['materialization_batch_size']==2 and m.q_physical==2


def test_cx_eigenstate_is_product():
    m=ProductStateModel(2); m.step(l.HGate(),[0]); m.step(l.HGate(),[1])
    m.step(l.CXGate(),[0,1]); assert m.q_physical==0


def test_cz_product_pair_and_known_shortcut():
    m=ProductStateModel(2); m.step(l.HGate(),[0]); m.step(l.CZGate(),[0,1])
    assert m.q_physical==0
    m.step(l.HGate(),[1]); m.step(l.CZGate(),[0,1]); assert m.q_physical==2


def test_materialized_control_plus_target():
    m=ProductStateModel(3); m.step(l.HGate(),[0]); m.step(l.CXGate(),[0,1])
    m.step(l.HGate(),[2]); m.step(l.CXGate(),[0,2])
    assert m.q_physical==2  # |+> is an X eigenvector for any entangled control.


def test_materialized_target_with_product_control():
    m=ProductStateModel(3); m.step(l.HGate(),[0]); m.step(l.CXGate(),[0,1])
    m.step(l.HGate(),[2]); e=m.step(l.CXGate(),[2,0])
    assert e['materialization_batch_size']==1 and m.q_physical==3


def test_large_mcx_known_zero():
    m=ProductStateModel(7); m.step(l.HGate(),[0]); m.step(l.MCXGate(6),list(range(7)))
    assert m.q_physical==0


def test_multi_target_arity():
    m=ProductStateModel(4);m.step(l.HGate(),[0]);m.step(l.XGate(),[1])
    m.step(l.MCMTGate(l.XGate(),2,2),list(range(4)))
    assert m.cells[2].label=='M' and m.cells[3].label=='M'
