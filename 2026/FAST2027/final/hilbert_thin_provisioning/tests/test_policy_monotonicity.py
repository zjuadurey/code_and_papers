from qiskit import QuantumCircuit
from qiskit.circuit import library as l
from htp.product_state_model import ProductStateModel
from htp.materialization_policy import POLICIES,materialization_cost


def test_dimension_growth_requires_event():
    m=ProductStateModel(4)
    operations=[(l.HGate(),[0]),(l.RZGate(.2),[0]),(l.CXGate(),[0,1]),
                (l.SwapGate(),[1,3]),(l.HGate(),[2]),(l.CZGate(),[2,3])]
    for op,ids in operations:
        before=m.q_physical;e=m.step(op,ids)
        assert 0<=m.q_physical<=m.q_logical<=m.n
        assert m.q_physical-before==e['materialization_batch_size']
        for policy in POLICIES:
            assert all(v>=0 for v in materialization_cost(policy,before,e['materialization_batch_size']).values())
