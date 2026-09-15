from qiskit import QuantumCircuit
from qiskit.circuit.library import SwapGate
from htp.abstract_state import K0,K1,Q
from htp.gate_semantics import transfer
from htp.analyzer import analyze

def test_swap():
    s=[Q,K1]; transfer(s,SwapGate(),[0,1]); assert s==[K1,Q]
    s=[K0,K1]; transfer(s,SwapGate(),[0,1]); assert s==[K1,K0]

def test_transport_not_new_dimension():
    c=QuantumCircuit(3); c.h(0); c.swap(0,1); c.swap(1,2)
    r=analyze(c)
    assert r['summary']['q_peak']==1 and r['summary']['never_quantum_count']==0
    assert len(r['events'])==1
