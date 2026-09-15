"""Read-only cross-artifact audit; writes its own record under the new results."""
import _materialization_common as common
import datetime
import gzip
import json
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from htp.loaders import sha256
from htp.materialization_policy import POLICIES

out=common.OUT
frozen=common.check_frozen()
manifest=json.loads((out/'run_manifest.json').read_text())
verification=json.loads((out/'verification.json').read_text())
assert verification['status']=='PASS' and verification['false_virtual']==0
assert verification['test_failures']==0 and verification['tests_passed']>=194
assert verification['fused_correctness_cases']>=1000
for path,digest in manifest['output_sha256'].items():
    assert sha256(path)==digest,('Model output changed after generation',path)
for record in [manifest,verification]:
    for path,digest in record['code_sha256'].items():
        if path.startswith('src/') or path in ['scripts/run_materialization_model.py',
                'scripts/validate_product_virtualization.py','scripts/_materialization_common.py',
                'configs/materialization_model.yaml']:
            assert sha256(path)==digest,('Stale core evidence',path)
s=pd.read_csv(out/'workload_policy_results.csv')
old=pd.read_csv('results/circuit_summary.csv')
real=old[~old.source.isin(['generated','synthetic_control'])]
assert real.workload_id.nunique()==251
assert len(real)==502
assert len(s)==len(old)*len(POLICIES)*len(common.CONFIG['qdao_m'])
assert s[s.primary_eligible].workload_id.nunique()==90
assert s[s.primary].workload_id.nunique()==86
assert set(s.policy)==set(POLICIES)
assert (s[s.policy=='EAGER_FULL'].q_peak==s[s.policy=='EAGER_FULL'].n).all()
valid=s[s.oracle_valid]
for column in ['peak_bytes','gate_volume_bytes','materialization_read_bytes','materialization_write_bytes']:
    assert (s[column].astype(float)>=0).all(),column
assert np.allclose(valid.predicted_total_bytes.astype(float),
    valid.predicted_qdao_bytes.astype(float)+valid.predicted_materialization_bytes.astype(float),rtol=1e-14)
assert (valid.predicted_total_boundary_fused.astype(float)<=valid.predicted_total_bytes.astype(float)).all()
assert (valid.predicted_total_resident_lower_bound.astype(float)<=valid.predicted_total_boundary_fused.astype(float)).all()

events=pd.read_csv(out/'physicalization_events.csv')
assert (events.new_q-events.old_q==events.materialization_batch_size).all()
assert (events.materialization_batch_size>0).all()
thin=events[events.policy=='BASIS_THIN']
assert (thin.insertion_read_bytes==0).all() and (thin.insertion_write_bytes==0).all()
assert all(int(r.implicit_zero_bytes)==int(r.new_backing_bytes)-int(r.old_backing_bytes) for r in thin.itertuples())
life=pd.read_csv(out/'qubit_lifetimes.csv')
assert life.first_physical_gate.isna().equals(life.never_physicalized)
assert life.first_quantum_gate.isna().equals(life.never_quantumized)
completed=life[~life.never_physicalized]
assert (completed.first_physical_gate>=completed.first_quantum_gate).all()
assert (completed.virtual_product_window_gates==completed.first_physical_gate-completed.first_quantum_gate).all()

total_rows=0
for chunk in pd.read_csv(out/'gate_event_trace.csv',chunksize=100000,dtype={'physical_backing_bytes':str}):
    assert (chunk.q_physical_eager==chunk.n).all()
    assert (chunk.q_physical_product_fused<=chunk.q_logical).all()
    assert (chunk.q_logical<=chunk.n).all()
    assert (chunk.q_physical_basis_thin==chunk.q_logical).all()
    assert (chunk.q_physical_basis_rewrite==chunk.q_logical).all()
    assert (chunk.virtual_basis_count+chunk.virtual_product_count+chunk.q_physical_product_fused==chunk.n).all()
    assert all(int(b)==16*(1<<int(q)) for b,q in zip(chunk.physical_backing_bytes,chunk.q_physical_product_fused))
    total_rows+=len(chunk)
assert total_rows==int((old.gates+1).sum())

# Independently derive capacity and growth totals from immutable per-view raw traces.
raw_dir=Path(manifest['raw_directory'])
audited_views=0
for row in old.to_dict('records'):
    with gzip.open(raw_dir/f"{row['workload_id']}_{row['representation']}.json.gz",'rt') as f:
        raw=json.load(f)
    for policy in POLICIES:
        qs=raw['qs'][policy]
        ev=raw['events'][policy]
        assert len(qs)==row['gates']+1
        assert all(b>=a for a,b in zip(qs,qs[1:]))
        deltas={j:b-a for j,(a,b) in enumerate(zip(qs,qs[1:]),1) if b>a}
        assert deltas=={e['gate_index']:e['materialization_batch_size'] for e in ev}
        result=s[(s.workload_id==row['workload_id'])&(s.representation==row['representation'])&(s.policy==policy)]
        assert (result.q_peak==max(qs)).all()
        assert (result.materialization_events==len(ev)).all()
        assert all(int(x)==sum(16*(1<<q) for q in qs[1:]) for x in result.gate_volume_bytes)
    assert raw['numerical_proof_error']<=common.CONFIG['numerical_budget']
    audited_views+=1
assert audited_views==718

external=[]
for row in pd.read_csv('results/manifests/external_repositories.csv').to_dict('records'):
    commit=subprocess.check_output(['git','-C',row['local_path'],'rev-parse','HEAD'],text=True).strip()
    status=subprocess.check_output(['git','-C',row['local_path'],'status','--porcelain'],text=True)
    assert commit==row['git_commit'] and not status,('External repository changed',row['name'])
    external.append(dict(name=row['name'],git_commit=commit,dirty=False))
for fmt in ['png','pdf']:
    assert len(list((out/'figures').glob('*.'+fmt)))>=7
for name in ['policy_summary.csv','workload_policy_results.csv','qubit_lifetimes.csv',
             'physicalization_events.csv','gate_event_trace.csv','sensitivity.csv','verification.json']:
    assert (out/name).stat().st_size>0
assert json.loads((out/'microbenchmark_status.json').read_text())['status'] in {'PASS','PARTIAL_RESOURCE_SKIP'}
assert Path('MATERIALIZATION_REPORT.md').read_text().startswith('# MECHANISM RESULT: ')
common.check_frozen()
record=dict(status='PASS',timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    current_git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    parent_git_commit=subprocess.check_output(['git','rev-parse','HEAD^'],text=True).strip(),
    previous_phase_commit=frozen['starting_commit'],frozen_prior_files=len(frozen['sha256']),
    prior_outputs_unchanged=True,views=audited_views,trace_rows=total_rows,real_circuits=251,
    primary_candidates=90,primary_common_valid=86,external_repositories=external,
    tests_passed=verification['tests_passed'],false_virtual=0,fused_correctness_cases=verification['fused_correctness_cases'],
    code_sha256=common.code_hashes(),
    artifact_sha256={str(p):sha256(p) for p in sorted(out.rglob('*')) if p.is_file() and
        'raw' not in p.relative_to(out).parts and p.name not in {'artifact_audit.json','audit.log'} and p.suffix!='.log'},
    report_sha256=sha256('MATERIALIZATION_REPORT.md'))
(out/'artifact_audit.json').write_text(json.dumps(record,indent=2))
(raw_dir/'artifact_audit.json').write_text(json.dumps(record,indent=2))
print(json.dumps({k:v for k,v in record.items() if k not in {'code_sha256','artifact_sha256','external_repositories'}},indent=2))
