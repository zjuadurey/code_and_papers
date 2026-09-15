"""Final cross-file consistency and provenance audit; no quantum simulation."""
import _common
import datetime
import gzip
import json
import math
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from htp.loaders import sha256

run=json.loads(Path('results/manifests/latest_run.json').read_text())
verification=json.loads(Path('results/verification.json').read_text())
assert verification['status']=='PASS' and verification['false_known_violations']==0
for path,h in verification['validated_code_sha256'].items():
    assert sha256(path)==h
    assert run['code_sha256'][path]==h
for name in ['circuit_summary','q_trace','qubit_activation','materialization_events','parse_failures','unknown_gates','qdao_oracle','analysis_failures','layer_trace']:
    p=f'results/{name}.csv'; assert sha256(p)==run['outputs'][p],p
s=pd.read_csv('results/circuit_summary.csv')
t=pd.read_csv('results/q_trace.csv')
a=pd.read_csv('results/qubit_activation.csv')
e=pd.read_csv('results/materialization_events.csv')
assert len(s)==2*run['semantic_lowered_pairs']
assert len(t)==int((s.gates+1).sum())
assert len(a)==int(s.n.sum())
assert len(e)==int(s.num_materialization_events.sum())
assert (t.known_zero+t.known_one+t.q_live==t.n).all()
assert (t.state_reduction_log2==t.n-t.q_live).all()
assert (t.gate_index>=0).all()
for r in s.itertuples():
    with gzip.open(Path(run['raw_directory'])/f'{r.workload_id}_{r.representation}.json.gz','rt') as f:
        payload=json.load(f)
    trace=payload['trace']; qs=np.array([x['q_live'] for x in trace],dtype=int)
    assert len(trace)==r.gates+1 and qs[0]==0
    assert np.all(np.diff(qs)>=0) and qs[-1]==r.q_final
    assert sum(x['delta_q'] for x in payload['events'])==r.q_final
    # Independent direct finite-n reference, rather than invoking metrics.py.
    reference=r.gates/np.exp2(qs[1:].astype(float)-r.n).sum()
    assert math.isclose(reference,r.ideal_gate_reduction,rel_tol=1e-11)
    for event in payload['events']:
        k=event['gate_index']
        assert event['old_q']==qs[k-1] and event['new_q']==qs[k]
    assert sha256(r.input_path)==r.source_sha256
repos=pd.read_csv('results/manifests/external_repositories.csv')
for r in repos.itertuples():
    dirty=subprocess.check_output(['git','-C',r.local_path,'status','--porcelain'],text=True).strip()
    commit=subprocess.check_output(['git','-C',r.local_path,'rev-parse','HEAD'],text=True).strip()
    assert not dirty and commit==r.git_commit
for name in ['figure1_q_traces','figure2_activation_cdf','figure3_reduction_by_family','figure4_semantic_vs_lowered','figure5_full_materialization','figure6_qdao_oracle']:
    for ext in ['png','pdf']:
        assert (Path('results/figures')/f'{name}.{ext}').stat().st_size>1000
report=Path('FINAL_REPORT.md').read_text()
assert report.startswith('# STATIC CHARACTERIZATION: '+json.loads(Path('results/decision.json').read_text())['classification'])
audit=dict(status='PASS',timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),run_id=run['run_id'],
           summary_rows=len(s),trace_rows=len(t),activation_rows=len(a),materialization_events=len(e),external_repos_clean=True,
           hashes={str(p):sha256(p) for base in ['src','scripts','configs','notes'] for p in sorted(Path(base).rglob('*')) if p.is_file() and '__pycache__' not in str(p)})
for p in [Path('FINAL_REPORT.md'),Path('README.md'),Path('requirements.lock.txt'),Path('results/verification.json')]:
    audit['hashes'][str(p)]=sha256(p)
Path('results/manifests/artifact_audit.json').write_text(json.dumps(audit,indent=2))
print(json.dumps({k:v for k,v in audit.items() if k!='hashes'},indent=2))
