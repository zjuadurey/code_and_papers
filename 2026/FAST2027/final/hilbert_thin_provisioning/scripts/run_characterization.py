import _common
import csv
import datetime
import gzip
import hashlib
import io
import json
import signal
import time
from pathlib import Path
import pandas as pd
import yaml
from qiskit import qpy
from htp.analyzer import analyze
from htp.loaders import load_circuits, unitary_prefix, semantic_circuit, lower, sha256, UnsupportedDynamic
from htp.qdao_model import traffic_oracle
from htp.workload_generators import generate
from htp.workload_discovery import write_csv

config = yaml.safe_load(Path('configs/analysis.yaml').read_text())
wc = yaml.safe_load(Path('configs/workloads.yaml').read_text())
run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
raw = Path('results/raw')/run_id
raw.mkdir(parents=True, exist_ok=False)
(raw/'generated_inputs').mkdir()
for p in [Path('configs/analysis.yaml'), Path('configs/workloads.yaml'), Path('results/manifests/selected_workloads.csv')]:
    (raw/p.name).write_bytes(p.read_bytes())

class Stream:
    def __init__(self,name,fields):
        self.f=Path('results',name+'.csv').open('w',newline='')
        self.w=csv.DictWriter(self.f,fieldnames=fields); self.w.writeheader()
    def write(self,rows):
        self.w.writerows(rows); self.f.flush()
    def close(self): self.f.close()

dummy=__import__('qiskit').QuantumCircuit(1); dummy.h(0)
example=analyze(dummy)
keys=['workload_id','representation']
streams={
    'trace':Stream('q_trace',keys+list(example['trace'][0])),
    'activations':Stream('qubit_activation',keys+list(example['activations'][0])),
    'events':Stream('materialization_events',keys+list(example['events'][0])),
    'layers':Stream('layer_trace',keys+list(example['layers'][0]))}
summaries, unknowns, oracles, failures, generated_manifest, exclusions = [], [], [], [], [], []
seen = {}

def timeout(signum,frame):
    raise TimeoutError('Per-workload static processing exceeded 120 seconds')
signal.signal(signal.SIGALRM,timeout)

def process(circuit,meta):
    start=time.monotonic()
    signal.alarm(120)
    try:
        clean, removed=unitary_prefix(circuit)
        semantic=semantic_circuit(clean,config['max_analysis_gates'])
        # Structural duplicate key ignores filenames/register names but preserves gates and parameters.
        structure=[(op.base_class.__module__,op.name,[str(p) for p in op.params],ids) for op,ids,_ in __import__('htp.analyzer',fromlist=['scheduled_operations']).scheduled_operations(semantic)]
        digest=hashlib.sha256(json.dumps([clean.num_qubits,structure],sort_keys=True).encode()).hexdigest()
        meta['circuit_structure_sha256']=digest
        if meta['source'] not in {'generated','synthetic_control'} and digest in seen:
            exclusions.append(dict(**meta,reason='duplicate_normalized_structure',duplicate_of=seen[digest]))
            return
        lowered=lower(clean)
        if len(lowered.data)>config['max_analysis_gates']:
            raise ValueError('LoweredGateLimit')
        views=[('semantic',semantic),('lowered',lowered)]
        results=[(name,analyze(c,config['angle_tol'])) for name,c in views]
        if any(r['summary']['gates']==0 for _,r in results):
            raise ValueError('Empty unitary prefix')
        for name,result in results:
            key=dict(workload_id=meta['workload_id'],representation=name)
            summary=dict(**(meta | key | result['summary']), original_gate_count=len(circuit.data),
                         semantic_gate_count=results[0][1]['summary']['gates'], lowered_gate_count=results[1][1]['summary']['gates'],
                         removed_terminal_instructions=removed, analysis_seconds=time.monotonic()-start)
            summaries.append(summary)
            for field,stream in streams.items():
                stream.write([dict(**key,**r) for r in result[field]])
            for gate,count in result['unknown'].items():
                unknowns.append(dict(**key,unknown_gate_name=gate,count=count,example_workloads=meta['workload_id']))
            for m in config['qdao_m']:
                if config['qdao_fixed_t'] < m < clean.num_qubits:
                    try:
                        oracles.append(dict(**key,source=meta['source'],family=meta['family'],n=clean.num_qubits,
                                            **traffic_oracle(result,m,config['qdao_fixed_t']),oracle_ok=True,error=''))
                    except ValueError as e:
                        oracles.append(dict(**key,source=meta['source'],family=meta['family'],n=clean.num_qubits,m=m,
                                            oracle_ok=False,error=str(e)))
            payload={k:v for k,v in result.items() if k!='operations'}
            payload['summary']=summary
            with gzip.open(raw/f"{meta['workload_id']}_{name}.json.gz",'wt') as f:
                json.dump(payload,f,allow_nan=False)
        if meta['source'] not in {'generated','synthetic_control'}:
            seen[digest]=meta['workload_id']
    except AssertionError:
        raise
    except Exception as e:
        failures.append(dict(**meta,error_type=type(e).__name__,error_message=str(e)[:1500],
                             unsupported_dynamic=isinstance(e,UnsupportedDynamic)))
        print(f"Excluded {meta['workload_id']}: {type(e).__name__}: {str(e)[:180]}",flush=True)
    finally:
        signal.alarm(0)

selected=pd.read_csv('results/manifests/selected_workloads.csv').to_dict('records')
for index,row in enumerate(selected):
    wid=f"{row['source']}_{row['sha256'][:16]}_{row['circuit_index']}"
    meta=dict(workload_id=wid,source=row['source'],source_path=row['path'],source_sha256=row['sha256'],
              family=row['family_if_inferable'],synthetic_control=False,generator='',input_path=row['absolute_path'],
              circuit_index=row['circuit_index'])
    assert sha256(row['absolute_path'])==row['sha256'], 'Input changed since discovery'
    process(load_circuits(row['absolute_path'])[row['circuit_index']],meta)
    if (index+1)%20==0:
        print(f'External {index+1}/{len(selected)}; pairs={len(summaries)//2}, exclusions={len(exclusions)}, failures={len(failures)}',flush=True)
for name,family,circuit,generator,synthetic in generate(wc['generated_sizes'],wc['seed']):
    # Qiskit 2.5.2 QPY cannot reload some library OrGate wrappers. Serialize
    # the actual transparent semantic expansion, and analyze that same input.
    circuit=semantic_circuit(circuit,config['max_analysis_gates'])
    path=raw/'generated_inputs'/f'{name}.qpy'
    with path.open('wb') as f: qpy.dump(circuit,f)
    loaded=load_circuits(path)[0]
    assert loaded.num_qubits==circuit.num_qubits and len(loaded.data)==len(circuit.data)
    digest=sha256(path)
    meta=dict(workload_id=name,source='synthetic_control' if synthetic else 'generated',source_path=str(path),
              source_sha256=digest,family=family,synthetic_control=synthetic,generator=generator,input_path=str(path.resolve()),circuit_index=0)
    generated_manifest.append(meta)
    process(loaded,meta)
    print(f'Generated {name}; pairs={len(summaries)//2}',flush=True)
for stream in streams.values(): stream.close()
write_csv('results/circuit_summary.csv',summaries)
write_csv('results/unknown_gates.csv',unknowns,keys+['unknown_gate_name','count','example_workloads'])
write_csv('results/qdao_oracle.csv',oracles)
write_csv('results/analysis_failures.csv',failures)
write_csv('results/manifests/duplicate_exclusions.csv',exclusions)
write_csv('results/manifests/generated.csv',generated_manifest)
manifest=dict(run_id=run_id,raw_directory=str(raw),semantic_lowered_pairs=len(summaries)//2,
              analysis_failures=len(failures),structural_duplicates=len(exclusions),code_sha256={str(p):sha256(p) for base in ['src','scripts','configs'] for p in sorted(Path(base).rglob('*')) if p.is_file() and '__pycache__' not in str(p)},
              outputs={str(p):sha256(p) for p in sorted(Path('results').glob('*.csv'))})
Path('results/manifests/latest_run.json').write_text(json.dumps(manifest,indent=2))
(raw/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Characterization complete:',manifest['semantic_lowered_pairs'],'pairs;',len(failures),'explicit failures')
