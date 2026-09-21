"""Local small-circuit validation fixtures, not a scientific model/solver run."""
import ast
from collections import Counter
from pathlib import Path
import pytest
from qiskit import QuantumCircuit,transpile
from qiskit.quantum_info import Statevector
from methods import distribution_report,process_overlap,structural_signature
from qrefactorbench.evaluator.resources import extract_resources

HERE=Path(__file__).resolve().parent


def test_same_pqid_count_signature_different_operation_operands():
    a,b=QuantumCircuit(2),QuantumCircuit(2)
    a.h(0);a.cx(0,1)
    b.h(0);b.cx(1,0)
    assert structural_signature(a)==structural_signature(b)
    assert process_overlap(a,b)<1
    assert distribution_report(Statevector.from_instruction(a).probabilities_dict(),Statevector.from_instruction(b).probabilities_dict())['total_variation']>0
    # Execute only four reviewed pure functions from the pinned evaluator; no worker main.
    names={'normalize_gate_counts','observed_gate_counts','metadata_gate_count','structural_result'}
    nodes=[n for n in ast.parse((HERE/'sources/pqid_worker.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert len(nodes)==4
    scope={'Counter':Counter};exec(compile(ast.Module(body=nodes,type_ignores=[]),'reviewed_pqid_functions','exec'),scope)
    assert scope['structural_result'](b,structural_signature(a))['checks']['all_match']


def test_equal_computational_basis_distribution_is_not_channel_equivalence():
    a,b=QuantumCircuit(1),QuantumCircuit(1);a.id(0);b.z(0)
    assert distribution_report(Statevector.from_instruction(a).probabilities_dict(),Statevector.from_instruction(b).probabilities_dict())['total_variation']==0
    assert process_overlap(a,b)==pytest.approx(0)
    c=QuantumCircuit(1);c.global_phase=0.37
    assert process_overlap(a,c)==pytest.approx(1)


def test_process_overlap_refuses_nonunitary_contract():
    a=QuantumCircuit(1);a.h(0);b=a.copy();b.measure_all()
    with pytest.raises(ValueError):process_overlap(a,b)
    b=QuantumCircuit(1);b.reset(0)
    with pytest.raises(ValueError):process_overlap(a,b)


def test_mqt_generator_multiple_representations():
    # One inspected pure function; strip only its registry decorator, preserve body.
    source=ast.parse((HERE/'sources/mqt_qaoa.py').read_text())
    fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='create_circuit')
    fn.decorator_list=[]
    import numpy as np
    from qiskit.circuit import ParameterVector
    scope={'np':np,'QuantumCircuit':QuantumCircuit,'ParameterVector':ParameterVector}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'reviewed_mqt_generator','exec'),scope)
    high=scope['create_circuit'](4,repetitions=1,seed=10)
    bound=high.assign_parameters({p:0.31 for p in high.parameters})
    low=transpile(bound,basis_gates=['rz','sx','x','cx'],optimization_level=0,seed_transpiler=10)
    assert process_overlap(bound,low)==pytest.approx(1)
    assert extract_resources(bound)['num_qubits']==extract_resources(low)['num_qubits']==4
    assert extract_resources(low)['representation']=='as_supplied'
    assert low.count_ops().get('rzz',0)==0


def test_quanplus_actual_kl_function_is_not_adopted_threshold():
    import numpy as np
    tree=ast.parse((HERE/'sources/quanplus_kl.py').read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef));scope={'np':np}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'reviewed_quanplus_kl','exec'),scope)
    value,upstream_accepts=scope['get_kl_div'](np.array([1.,0.]),np.array([0.5,0.5]))
    assert value==pytest.approx(__import__('math').log(2),abs=1e-9)
    assert not upstream_accepts
    # Our report exposes the opposite, explicitly named direction with no smoothing.
    ours=distribution_report({'0':0.5,'1':0.5},{'0':1})
    assert ours['kl_is_infinite'] and ours['acceptance'] is None
