import _common
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from qiskit import transpile
from qiskit.quantum_info import Statevector
from htp.loaders import backend, load_circuits, unitary_prefix, semantic_circuit, lower, sha256
from htp.validation import validate_prefixes, random_validation_circuit

config=yaml.safe_load(Path('configs/analysis.yaml').read_text())
report=dict(status='RUNNING',false_known_violations=0,exact_validation_cases=0,random_cases=0,
            benchmark_cases=0,prefixes=0,known_claims=0,max_density_error=0.,aer_crosschecks=0,
            tolerance=config['exact_tol'],seed=config['exact_seed'],max_qubits=8)
out=Path('results/verification.json')
out.write_text(json.dumps(report,indent=2))
cases=[]
try:
    # This test result is tied to this validation, not inferred from an old console log.
    xml=Path('results/raw')/(json.loads(Path('results/manifests/latest_run.json').read_text())['run_id'])/'pytest.xml'
    subprocess.run([sys.executable,'-m','pytest','-q',f'--junitxml={xml}'],check=True)
    root=ET.parse(xml).getroot()
    suites=list(root.iter('testsuite'))
    report['tests_passed']=sum(int(s.get('tests','0'))-int(s.get('failures','0'))-int(s.get('errors','0'))-int(s.get('skipped','0')) for s in suites)
    report['test_failures']=sum(int(s.get('failures','0'))+int(s.get('errors','0')) for s in suites)

    def check(circuit,label,category):
        result=validate_prefixes(circuit,config['exact_tol'])
        report['exact_validation_cases']+=1
        report[category]+=1
        for key in ['prefixes','known_claims']:
            report[key]+=result[key]
        report['max_density_error']=max(report['max_density_error'],result['max_density_error'])
        cases.append(dict(case=label,n=circuit.num_qubits,**result))

    for i in range(config['exact_cases']):
        circuit=random_validation_circuit(config['exact_seed']+i)
        check(circuit,f'random_{i}_semantic','random_cases')
        lowered=lower(circuit)
        check(lowered,f'random_{i}_lowered','random_cases')
        if i<20:
            b=backend(); c=transpile(circuit,backend=b,optimization_level=0)
            c.save_statevector()
            actual=b.run(c).result().get_statevector()
            assert Statevector(actual).equiv(Statevector.from_instruction(circuit),atol=config['exact_tol'],rtol=0)
            report['aer_crosschecks']+=1
        if (i+1)%100==0: print('Random exact cases',i+1,flush=True)
    summary=pd.read_csv('results/circuit_summary.csv')
    small=summary[(summary.n<=8)&(summary.gates<=1000)&(summary.representation=='semantic')]
    for row in small.to_dict('records'):
        circuit=load_circuits(row['input_path'])[int(row['circuit_index'])]
        circuit,_=unitary_prefix(circuit)
        check(semantic_circuit(circuit),row['workload_id']+'_semantic','benchmark_cases')
        check(lower(circuit),row['workload_id']+'_lowered','benchmark_cases')
        # Also ensure the lowering preserves the workload state, independently
        # of the abstract labels (which are allowed to be conservative).
        assert Statevector.from_instruction(circuit).equiv(Statevector.from_instruction(lower(circuit)),atol=config['exact_tol'],rtol=0)
    report['status']='PASS'
except Exception as e:
    report['status']='FAIL'
    report['error']=str(e)
    if 'FALSE-KNOWN' in str(e): report['false_known_violations']+=1
    raise
finally:
    report['validated_code_sha256']={str(p):sha256(p) for p in sorted(Path('src/htp').glob('*.py'))}
    out.write_text(json.dumps(report,indent=2))
    pd.DataFrame(cases).to_csv('results/exact_validation_cases.csv',index=False)
print(json.dumps(report,indent=2))
