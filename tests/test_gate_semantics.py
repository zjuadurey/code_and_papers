import numpy as np
import pytest
from qiskit.circuit import Gate, Parameter
from qiskit.circuit import library as l
from htp.abstract_state import K0, K1, Q
from htp.gate_semantics import transfer


@pytest.mark.parametrize('gate', [l.XGate(), l.YGate()])
@pytest.mark.parametrize('before,after', [(K0,K1),(K1,K0),(Q,Q)])
def test_flip(gate,before,after):
    s=[before]; transfer(s,gate,[0]); assert s==[after]


@pytest.mark.parametrize('gate', [l.ZGate(),l.SGate(),l.SdgGate(),l.TGate(),l.TdgGate(),l.RZGate(.43),l.PhaseGate(.2)])
@pytest.mark.parametrize('value', [K0,K1,Q])
def test_diagonal(gate,value):
    s=[value]; transfer(s,gate,[0]); assert s==[value]


@pytest.mark.parametrize('gate', [l.HGate(),l.SXGate(),l.SXdgGate()])
@pytest.mark.parametrize('value', [K0,K1,Q])
def test_mixing(gate,value):
    s=[value]; transfer(s,gate,[0]); assert s==[Q]


@pytest.mark.parametrize('gate_type', [l.RXGate,l.RYGate])
@pytest.mark.parametrize('theta,expected', [(0,K0),(2*np.pi,K0),(np.pi,K1),(-np.pi,K1),(np.pi/2,Q),(Parameter('a'),Q)])
def test_rotation(gate_type,theta,expected):
    from htp.abstract_state import initial
    s=initial(1); transfer(s,gate_type(theta),[0]); assert s==[expected]
    s=initial(1);s[0]=Q; transfer(s,gate_type(theta),[0]); assert s==[Q]


def test_unknown_and_name_spoofing():
    for name, arity in [('mystery',1),('x',2),('h',1),('cz',2)]:
        s=[K0]*arity
        _,unknown=transfer(s,Gate(name,arity,[]),list(range(arity)))
        assert unknown and s==[Q]*arity


def test_matrix_proofs():
    from htp.abstract_state import initial
    s=initial(2);s[:]=[Q,K1]; transfer(s,l.UnitaryGate(np.diag([1,1j,-1,-1j])),[0,1]); assert s==[Q,K1]
    s=initial(1); transfer(s,l.UGate(np.pi,.4,.8),[0]); assert s==[K1]


def test_near_special_angles_cannot_accumulate_false_known():
    from qiskit import QuantumCircuit
    from htp.validation import validate_prefixes
    from htp.analyzer import analyze
    c=QuantumCircuit(1)
    for _ in range(20): c.rx(9e-11,0)
    assert analyze(c)['summary']['q_final']==1
    validate_prefixes(c)


def test_nearly_diagonal_matrices_cannot_accumulate_false_known():
    from qiskit import QuantumCircuit
    from htp.validation import validate_prefixes
    from htp.analyzer import analyze
    c=QuantumCircuit(1)
    theta=1.8e-14
    mat=np.array([[np.cos(theta/2),-1j*np.sin(theta/2)],[-1j*np.sin(theta/2),np.cos(theta/2)]])
    gate=l.UnitaryGate(mat)
    for _ in range(6000): c.append(gate,[0])
    assert analyze(c)['summary']['q_final']==1
    validate_prefixes(c)


def test_huge_angle_reduction_is_not_reliable():
    from qiskit import QuantumCircuit
    from htp.analyzer import analyze
    from htp.validation import validate_prefixes
    c=QuantumCircuit(1);c.rx(2*np.pi*2**50,0)
    assert analyze(c)['summary']['q_final']==1
    validate_prefixes(c)
