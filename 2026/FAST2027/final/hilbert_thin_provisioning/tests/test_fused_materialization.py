import numpy as np
import pytest
from qiskit.quantum_info import Operator, random_statevector, random_unitary
from qiskit.circuit.library import CXGate,CZGate
from htp.fused_materialization import eager_expand_then_gate,fused_materialize_and_gate,fused_cx_product_control,naive_cx_product_control


@pytest.mark.parametrize('seed',range(12))
def test_fused_dense_equivalence(seed):
    state=random_statevector(16,seed=seed).data
    factor=random_statevector(2,seed=seed+30).data
    for gate,ids in [(Operator(CXGate()).data,[4,1]),(Operator(CXGate()).data,[1,4]),
                     (Operator(CZGate()).data,[4,1]),(random_unitary(4,seed=seed).data,[4,1])]:
        a=eager_expand_then_gate(state,[factor],gate,ids)
        b=fused_materialize_and_gate(state,[factor],gate,ids)
        assert np.allclose(a,b,atol=1e-13,rtol=0)


def test_batch_fused():
    b=random_statevector(8,seed=10).data
    factors=[random_statevector(2,seed=i).data for i in [11,12]]
    gate=Operator(CZGate()).data
    assert np.allclose(eager_expand_then_gate(b,factors,gate,[3,4]),fused_materialize_and_gate(b,factors,gate,[3,4]),atol=1e-13)


def test_microkernels_match_reference():
    b=random_statevector(32,seed=32).data;p=random_statevector(2,seed=8).data
    expected=eager_expand_then_gate(b,[p],Operator(CXGate()).data,[5,2])
    assert np.allclose(fused_cx_product_control(b,p,2),expected)
    assert np.allclose(naive_cx_product_control(b,p,2),expected)


def test_large_correctness_kernel_rejected():
    with pytest.raises(ValueError): fused_materialize_and_gate(np.ones(8192),[],np.eye(4),[0,1])
