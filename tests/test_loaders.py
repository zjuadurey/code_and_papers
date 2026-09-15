import pytest
from qiskit import QuantumCircuit, qasm2, qasm3, qpy
from htp.loaders import load_circuits, unitary_prefix, semantic_circuit, UnsupportedDynamic, lower
from htp.analyzer import analyze

@pytest.mark.parametrize('suffix',['.qasm','.qasm2','.qasm3','.qpy'])
def test_load(tmp_path,suffix):
    c=QuantumCircuit(3); c.x(0); c.ccx(0,1,2)
    p=tmp_path/('c'+suffix)
    if suffix=='.qpy':
        with p.open('wb') as f: qpy.dump([c,c],f)
    else: p.write_text(qasm3.dumps(c) if suffix=='.qasm3' else qasm2.dumps(c))
    loaded=load_circuits(p); assert len(loaded)==(2 if suffix=='.qpy' else 1)
    assert analyze(semantic_circuit(loaded[0]))['summary']['q_final']==0

def test_readout_and_dynamics():
    c=QuantumCircuit(2,2); c.h(0); c.measure([0,1],[0,1])
    clean,removed=unitary_prefix(c); assert removed==2 and len(clean.data)==1
    c.x(0)
    with pytest.raises(UnsupportedDynamic): unitary_prefix(c)

def test_custom_wrapper_and_lowering():
    b=QuantumCircuit(3); b.ccx(0,1,2)
    c=QuantumCircuit(3); c.append(b.to_gate(),range(3))
    assert semantic_circuit(c).data[0].operation.name=='ccx'
    assert len(lower(c).data)>0

def test_custom_gate_named_z(tmp_path):
    p=tmp_path/'spoof.qasm'
    p.write_text('OPENQASM 2.0; gate z a { U(pi/2,0,pi) a; } qreg q[1]; z q[0];')
    c=semantic_circuit(load_circuits(p)[0]); assert analyze(c)['summary']['q_final']==1

def test_legacy_undeclared_mcx(tmp_path):
    p=tmp_path/'legacy.qasm'
    p.write_text('OPENQASM 2.0; include "qelib1.inc"; qreg q[5]; mcx_gray q[0],q[1],q[2],q[3],q[4];')
    assert analyze(semantic_circuit(load_circuits(p)[0]))['summary']['q_final']==0

def test_legacy_c3sx(tmp_path):
    p=tmp_path/'legacy.qasm'
    p.write_text('OPENQASM 2.0; include "qelib1.inc"; qreg q[4]; c3sx q[0],q[1],q[2],q[3];')
    assert load_circuits(p)[0].data[0].operation.num_qubits==4

def test_static_lowering_exceeds_physical_ram_width():
    c=QuantumCircuit(64); c.h(0); c.ccx(0,1,63)
    result=lower(c)
    assert result.num_qubits==64 and result.count_ops()['ccx']==1

def test_arithmetic_portable_qpy(tmp_path):
    from qiskit.circuit.library import IntegerComparator
    c=semantic_circuit(IntegerComparator(3,5))
    p=tmp_path/'comparator.qpy'
    with p.open('wb') as f: qpy.dump(c,f)
    restored=load_circuits(p)[0]
    assert analyze(restored)['summary']['q_final']==analyze(c)['summary']['q_final']
