"""Save actual local method-fixture results; no model, optimizer or QPU execution."""
import argparse
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
import importlib.metadata

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector

from methods import (backward_error,distribution_report,objective_report,pass_at_k,
                     process_overlap,structural_signature,symmetry_defect)
from qrefactorbench.evaluator.resources import extract_resources

HERE=Path(__file__).resolve().parent


def extracted(filename: str, names: set[str], scope: dict) -> dict:
    """Load only named, inspected top-level functions with snapshot identity checked."""
    path=HERE/'sources'/filename
    row=next(r for r in json.loads((HERE/'sources/manifest.json').read_text()) if r['file']==filename)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('changed source snapshot')
    nodes=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names]
    if {n.name for n in nodes}!=names:raise ValueError('missing source function')
    for n in nodes:n.decorator_list=[]  # MQT registry only; record adaptation in output.
    exec(compile(ast.Module(body=nodes,type_ignores=[]),f'inspected_{filename}','exec'),scope)
    return scope


def run() -> dict:
    a,b=QuantumCircuit(2),QuantumCircuit(2);a.h(0);a.cx(0,1);b.h(0);b.cx(1,0)
    pqid=extracted('pqid_worker.py',{'normalize_gate_counts','observed_gate_counts','metadata_gate_count','structural_result'},{'Counter':Counter})
    identity,phase=QuantumCircuit(1),QuantumCircuit(1);identity.id(0);phase.z(0)
    plus=extracted('quanplus_kl.py',{'get_kl_div'},{'np':np})
    kl,upstream_pass=plus['get_kl_div'](np.array([1.,0.]),np.array([0.5,0.5]))
    mqt=extracted('mqt_qaoa.py',{'create_circuit'},{'np':np,'QuantumCircuit':QuantumCircuit,'ParameterVector':ParameterVector})
    parameterized=mqt['create_circuit'](4,repetitions=1,seed=10)
    high=parameterized.assign_parameters({p:0.31 for p in parameterized.parameters})
    low=transpile(high,basis_gates=['rz','sx','x','cx'],optimization_level=0,seed_transpiler=10)
    return {
        'status':'ENGINEERING_FIXTURES_NOT_MODEL_SCORES','model_calls':0,'qpu_calls':0,'quantum_optimizer_runs':0,
        'environment':{n:importlib.metadata.version(n) for n in ['qiskit','numpy','scipy','pytest']},
        'pass_at_k':{'source':'QuanBench/HumanEval estimator','hand_fixture':{'n':4,'c':2,'k':2},'value':pass_at_k(4,2,2),'actual_model_sample_count':0},
        'quanplus':{'source_function_executed':True,'upstream_direction':'observed to expected; elementwise clip eps=1e-12, no renormalization',
                    'source_kl':float(kl),'source_threshold':0.05,'source_fixture_accepts':bool(upstream_pass),
                    'threshold_adopted':False,'our_explicit_direction':distribution_report({'0':0.5,'1':0.5},{'0':1})},
        'pqid':{'source_function_executed':True,'upstream_structural_checks':pqid['structural_result'](b,structural_signature(a))['checks'],
                'unitary_process_overlap':process_overlap(a,b),
                'distribution':distribution_report(Statevector.from_instruction(a).probabilities_dict(),Statevector.from_instruction(b).probabilities_dict()),
                'conclusion':'This constructed pair shares count metadata but not circuit semantics; not a model failure.'},
        'unitary_vs_distribution':{'process_overlap':process_overlap(identity,phase),
                                   'distribution':distribution_report(Statevector.from_instruction(identity).probabilities_dict(),Statevector.from_instruction(phase).probabilities_dict()),
                                   'scope':'Unitary-only diagnostic; measurement/nonunitary circuits are rejected, never silently stripped.'},
        'mqt':{'source_generator_executed':True,'adaptation':'Removed registry decorator only; body retained.',
               'configuration':{'num_qubits':4,'repetitions':1,'seed':10,'all_parameters':0.31,'optimization_level':0,'seed_transpiler':10,'basis':['rz','sx','x','cx']},
               'high_level':extract_resources(high,representation='logical_rzz_rx_h'),
               'basis_level':extract_resources(low,representation='basis_rz_sx_x_cx'),
               'process_overlap':process_overlap(high,low),'hardware_layout':None,'shots':None,'objective_optimized':False},
        'supermarq':{'objective_gap':objective_report({'00':1},{'11':1},{'00':2,'11':2}),
                     'distribution':distribution_report({'00':1},{'11':1}),
                     'note':'Equal expectation need not imply equal distributions. Upstream score denominator can be zero/signed; no ratio threshold imported.'},
        'hpl':{'good':backward_error([[4,1],[1,3]],[1,2],[1/11,7/11],sys.float_info.epsilon),
               'bad':backward_error([[4,1],[1,3]],[1,2],[0,0],sys.float_info.epsilon),'official_hpl_run':False},
        'hpcg':{'symmetric_raw_defect':symmetry_defect([[4,1],[1,3]],[1,0],[0,1]),
                'nonsymmetric_raw_defect':symmetry_defect([[4,2],[1,3]],[1,0],[0,1]),
                'upstream_scaled_threshold_adopted':False,'official_hpcg_run':False},
    }


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    path=parser.parse_args().output
    if path.exists():raise FileExistsError(path)
    result=run();path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(path)
