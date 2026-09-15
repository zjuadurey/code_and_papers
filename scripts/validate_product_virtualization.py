import _materialization_common as common
import datetime
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import pandas as pd
from qiskit import QuantumCircuit
from qiskit.circuit import library as lib
from qiskit.quantum_info import Statevector,Operator,random_statevector,random_unitary
from htp.product_state_model import ProductStateModel
from htp.analyzer import scheduled_operations
from htp.loaders import lower
from htp.validation import random_validation_circuit
from htp.fused_materialization import eager_expand_then_gate,fused_materialize_and_gate,fused_cx_product_control,naive_cx_product_control

out,config=common.OUT,common.CONFIG
common.check_frozen()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
raw=out/'raw'/f'validation_{stamp}';raw.mkdir()
report=dict(status='RUNNING',false_virtual=0,false_virtual_violations=0,product_validation_cases=0,
            prefixes=0,virtual_claims=0,P_claims=0,max_impurity=0.,max_vector_projector_error=0.,
            fused_correctness_cases=0,max_fused_infidelity=0.,max_fused_amplitude_error=0.,seed=config['seed'],
            exact_max_qubits=8,fused_max_qubits=12,tolerance=config['proof_tolerance'])
cases=[];fused=[]
(out/'verification.json').write_text(json.dumps(report,indent=2))

def verify(circuit,label):
    n=circuit.num_qubits
    if n>8: raise ValueError('Exact validation limit is 8 qubits')
    model=ProductStateModel(n)
    state=Statevector.from_int(0,1<<n)
    checks=0
    for k,(op,ids,_) in enumerate(scheduled_operations(circuit),1):
        model.step(op,ids)
        state=state.evolve(op,qargs=ids)
        for i,cell in enumerate(model.cells):
            if cell.label=='M': continue
            matrix=np.moveaxis(state.data.reshape([2]*n),n-1-i,0).reshape(2,-1)
            rho=matrix@matrix.conj().T
            impurity=abs(1-float(np.trace(rho@rho).real))
            error=0. if cell.vector is None else float(np.max(np.abs(rho-np.outer(cell.vector,cell.vector.conj()))))
            if impurity>config['proof_tolerance'] or error>config['proof_tolerance']:
                report['false_virtual']+=1;report['false_virtual_violations']+=1
                raise AssertionError(f'FALSE_VIRTUAL case={label}, gate={k}:{op.name}, qubit={i}, label={cell.label}, impurity={impurity}, projector_error={error}')
            report['max_impurity']=max(report['max_impurity'],impurity)
            report['max_vector_projector_error']=max(report['max_vector_projector_error'],error)
            report['virtual_claims']+=1;report['P_claims']+=int(cell.label=='P');checks+=1
        report['prefixes']+=1
    report['product_validation_cases']+=1
    cases.append(dict(case=label,n=n,gates=len(scheduled_operations(circuit)),virtual_checks=checks,q_physical_final=model.q_physical))

try:
    xml=raw/'pytest.xml'
    subprocess.run([sys.executable,'-m','pytest','-q',f'--junitxml={xml}'],check=True)
    root=ET.parse(xml).getroot()
    report['tests_passed']=sum(int(s.get('tests',0))-int(s.get('failures',0))-int(s.get('errors',0))-int(s.get('skipped',0)) for s in root.iter('testsuite'))
    report['test_failures']=sum(int(s.get('failures',0))+int(s.get('errors',0)) for s in root.iter('testsuite'))
    rng=np.random.default_rng(config['seed'])
    for index in range(config['exact_random_circuits']):
        n=int(rng.integers(2,9))
        c=QuantumCircuit(n)
        # Long product-only prefixes are deliberately retained, not immediately
        # saturated by entanglers, to exercise many P-state assertions.
        for _ in range(16):
            bit=int(rng.integers(n))
            gate=[lib.HGate(),lib.RXGate(.37),lib.RYGate(.29),lib.RZGate(.73),lib.XGate()][int(rng.integers(5))]
            c.append(gate,[bit])
        for _ in range(28):
            arity=min(n,int(rng.choice([1,1,2,2,2,3])))
            ids=list(map(int,rng.choice(n,arity,replace=False)))
            if arity==1:
                gate=lib.UGate(*rng.uniform(-np.pi,np.pi,3))
            elif arity==2:
                gate=[lib.CXGate(),lib.CZGate(),lib.SwapGate(),lib.CPhaseGate(.43),lib.CRYGate(.8),lib.UnitaryGate(random_unitary(4,seed=config['seed']+index))][int(rng.integers(6))]
            else:
                gate=[lib.CCXGate(),lib.CSwapGate(),lib.MCXGate(2,ctrl_state=0)][int(rng.integers(3))]
            c.append(gate,ids)
        verify(c,f'product_random_{index}_semantic')
        verify(lower(c),f'product_random_{index}_lowered')
        if index<100:
            verify(random_validation_circuit(config['seed']+index),f'basis_random_{index}')
        if (index+1)%100==0: print('Random product circuits',index+1,flush=True)
    old=pd.read_csv('results/circuit_summary.csv')
    for row in old[(old.n<=8)&(old.gates<=1000)].to_dict('records'):
        verify(common.read_view(row),row['workload_id']+'_'+row['representation'])
    # Explicit M/backing controls correlated with unaddressed wires.
    for gate in [lib.CXGate(),lib.CZGate(),lib.CRYGate(.4),lib.UnitaryGate(random_unitary(4,seed=9))]:
        c=QuantumCircuit(3);c.h(0);c.cx(0,1);c.h(2);c.append(gate,[0,2]);verify(c,'entangled_rest_'+gate.name)
    for index in range(config['fused_cases']):
        q=int(rng.integers(1,9));k=2 if index%5==4 else 1
        backing=random_statevector(1<<q,seed=config['seed']+index).data
        factors=[random_statevector(2,seed=config['seed']+2000+index*2+j).data for j in range(k)]
        case=index%4
        if k==2:
            ids=[q,q+1]
        else:
            target=int(rng.integers(q));ids=[q,target] if case!=1 else [target,q]
        matrix=Operator(lib.CXGate() if case<2 else lib.CZGate()).data if case<3 else random_unitary(4,seed=index).data
        eager=eager_expand_then_gate(backing,factors,matrix,ids)
        result=fused_materialize_and_gate(backing,factors,matrix,ids)
        fidelity=float(abs(np.vdot(eager,result))**2/(np.vdot(eager,eager).real*np.vdot(result,result).real))
        infidelity=max(0.,1-fidelity);error=float(np.max(np.abs(eager-result)))
        assert infidelity<1e-12 and error<1e-12,(index,infidelity,error)
        if k==1 and case==0:
            assert np.allclose(fused_cx_product_control(backing,factors[0],ids[1]),eager,atol=1e-13,rtol=0)
            assert np.allclose(naive_cx_product_control(backing,factors[0],ids[1]),eager,atol=1e-13,rtol=0)
        report['fused_correctness_cases']+=1
        report['max_fused_infidelity']=max(report['max_fused_infidelity'],infidelity)
        report['max_fused_amplitude_error']=max(report['max_fused_amplitude_error'],error)
        fused.append(dict(case=index,kind=['CX_product_control','CX_materialized_control','CZ','general_2q'][case],old_q=q,batch_size=k,infidelity=infidelity,max_amplitude_error=error))
    common.check_frozen()
    report['status']='PASS'
except Exception as error:
    report.update(status='FAIL',error=str(error))
    raise
finally:
    report['code_sha256']=common.code_hashes()
    (out/'verification.json').write_text(json.dumps(report,indent=2))
    (raw/'verification.json').write_text(json.dumps(report,indent=2))
    pd.DataFrame(cases).to_csv(out/'exact_validation_cases.csv',index=False)
    pd.DataFrame(fused).to_csv(out/'fused_validation_cases.csv',index=False)
print(json.dumps({k:v for k,v in report.items() if k!='code_sha256'},indent=2))
