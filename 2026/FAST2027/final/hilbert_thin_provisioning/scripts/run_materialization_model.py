import _materialization_common as common
import csv
import datetime
import gzip
import json
import math
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from htp.analyzer import scheduled_operations
from htp.abstract_state import Q
from htp.product_state_model import ProductStateModel
from htp.materialization_policy import POLICIES,materialization_cost,ImplicitZeroExpansion
from htp.qdao_trace_model import partition_trace
from htp.traffic_model import compose_traffic,rounded_bytes
from htp.workload_discovery import write_csv
from htp.loaders import sha256

out,config=common.OUT,common.CONFIG
frozen=common.check_frozen()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
raw=out/'raw'/stamp; raw.mkdir(parents=True,exist_ok=False)
previous=json.loads(Path('results/manifests/latest_run.json').read_text())
summary=pd.read_csv('results/circuit_summary.csv')
# All previously accepted inputs; external primary first, no discovery/new seeds.
summary['primary_eligible']=(~summary.source.isin(['generated','synthetic_control']))&summary.n.between(20,40)&(summary.representation=='lowered')
summary=summary.sort_values(['primary_eligible','source','workload_id','representation'],ascending=[False,True,True,True])
results,events,lifetimes,sensitivity,exclusions=[],[],[],[],[]
trace_file=(out/'gate_event_trace.csv').open('w',newline='')
trace_writer=None

for position,row in enumerate(summary.to_dict('records'),1):
    circuit=common.read_view(row)
    operations=scheduled_operations(circuit)
    assert len(operations)==row['gates'] and circuit.num_qubits==row['n']
    key={k:row[k] for k in ['workload_id','representation','source','family','n','primary_eligible']}
    model=ProductStateModel(row['n'],config['proof_tolerance'],config['numerical_budget'])
    with gzip.open(Path(previous['raw_directory'])/f"{row['workload_id']}_{row['representation']}.json.gz",'rt') as f:
        old_trace=json.load(f)['trace']
    qs={p:[row['n'] if p=='EAGER_FULL' else 0] for p in POLICIES}
    policy_events={p:[] for p in POLICIES}
    first_quantum=[None]*row['n']; first_physical=[None]*row['n']; triggers=['']*row['n']
    product_peak=0
    def trace_record(index,name,ids=()):
        return dict(**key,gate_index=index,gate_name=name,normalized_gate_position=index/len(operations),
                    qubits=json.dumps(list(ids)),
                    q_logical=model.q_logical,q_physical_eager=row['n'],q_physical_basis_rewrite=model.q_logical,
                    q_physical_basis_thin=model.q_logical,q_physical_product_fused=model.q_physical,
                    virtual_basis_count=sum(c.label in {'K0','K1'} for c in model.cells),
                    virtual_product_count=sum(c.label=='P' for c in model.cells),
                    physical_backing_bytes=config['amplitude_bytes']<<model.q_physical)
    trace=[trace_record(0,'INITIAL')]
    for gate_index,(op,ids,depth) in enumerate(operations,1):
        old_basis=list(model.basis)
        old_q=model.q_logical
        e=model.step(op,ids)
        assert model.q_logical==old_trace[gate_index]['q_live'],(row['workload_id'],gate_index)
        for i in range(row['n']):
            if model.basis[i]==Q and first_quantum[i] is None:
                first_quantum[i]=gate_index
            if model.cells[i].label=='M' and first_physical[i] is None:
                first_physical[i]=gate_index;triggers[i]=e['trigger_reason']
        product_peak=max(product_peak,sum(c.label=='P' for c in model.cells))
        for policy in POLICIES:
            q=(row['n'] if policy=='EAGER_FULL' else model.q_physical if policy=='PRODUCT_FUSED' else model.q_logical)
            old=qs[policy][-1];qs[policy].append(q)
            if q>old and policy!='EAGER_FULL':
                added=e['qubits'] if policy=='PRODUCT_FUSED' else [i for i in ids if old_basis[i]!=Q and model.basis[i]==Q]
                event=dict(gate_index=gate_index,gate_name=op.name,qubits=json.dumps(added),old_q=old,new_q=q,
                           materialization_batch_size=q-old,trigger_reason=e['trigger_reason'] if policy=='PRODUCT_FUSED' else 'basis_quantumization',
                           old_backing_bytes=config['amplitude_bytes']<<old,new_backing_bytes=config['amplitude_bytes']<<q,
                           **materialization_cost(policy,old,q-old,config['amplitude_bytes']))
                if policy=='BASIS_THIN':
                    descriptor=ImplicitZeroExpansion(event['old_backing_bytes'],tuple(int(old_basis[i]) for i in added))
                    assert descriptor.physical_bytes_at_insertion==event['old_backing_bytes']
                    event['active_branch']=descriptor.active_branch
                policy_events[policy].append(event)
                events.append(dict(**key,policy=policy,**event))
        trace.append(trace_record(gate_index,op.name,ids))
    if trace_writer is None:
        trace_writer=csv.DictWriter(trace_file,fieldnames=list(trace[0]),lineterminator='\n');trace_writer.writeheader()
    trace_writer.writerows(trace);trace_file.flush()
    windows=[];completed=[]
    for i in range(row['n']):
        quantum,physical=first_quantum[i],first_physical[i]
        if physical is not None: assert quantum is not None and physical>=quantum
        window=physical-quantum if quantum is not None and physical is not None else None
        lower_bound=(physical if physical is not None else len(operations))-quantum if quantum is not None else None
        if lower_bound is not None: windows.append(lower_bound/len(operations))
        if window is not None: completed.append(window/len(operations))
        lifetimes.append(dict(**key,qubit=i,first_quantum_gate=quantum,first_physical_gate=physical,
            quantum_fraction=quantum/len(operations) if quantum is not None else None,
            physical_fraction=physical/len(operations) if physical is not None else None,
            virtual_product_window_gates=window,virtual_product_window_fraction=window/len(operations) if window is not None else None,
            observed_window_lower_bound_gates=lower_bound,observed_window_lower_bound_fraction=lower_bound/len(operations) if lower_bound is not None else None,
            never_quantumized=quantum is None,never_physicalized=physical is None,physicalization_trigger=triggers[i]))
    with gzip.open(raw/f"{row['workload_id']}_{row['representation']}.json.gz",'wt') as f:
        json.dump(dict(key=key,qs=qs,events=policy_events,trace=trace,numerical_proof_error=model.error),f)
    for m in config['qdao_m']:
        try:
            groups,partition_mode=partition_trace([ids for _,ids,_ in operations],row['n'],m,config['fixed_t'])
        except ValueError as err:
            exclusions.append(dict(**key,m=m,error_type=type(err).__name__,error_message=str(err)))
            groups=None;partition_mode='invalid_single_gate_capacity'
        eager=compose_traffic(qs['EAGER_FULL'],[],groups,'EAGER_FULL')['predicted_total_bytes'] if groups else None
        for policy in POLICIES:
            pe=policy_events[policy]
            record=dict(**key,policy=policy,m=m,fixed_t=config['fixed_t'],partition_mode=partition_mode,
                        oracle_valid=bool(groups),primary=bool(row['primary_eligible'] and m==config['primary_m'] and groups),
                        gates=len(operations),q_peak=max(qs[policy]),peak_bytes=config['amplitude_bytes']<<max(qs[policy]),
                        gate_volume_bytes=sum(config['amplitude_bytes']<<q for q in qs[policy][1:]),
                        materialization_events=len(pe),median_batch_size=float(np.median([e['materialization_batch_size'] for e in pe])) if pe else 0,
                        max_batch_size=max((e['materialization_batch_size'] for e in pe),default=0),
                        full_state_rewrites_avoided=len(policy_events['BASIS_REWRITE']) if policy in {'BASIS_THIN','PRODUCT_FUSED'} else 0,
                        median_physicalization_delay=float(np.median(completed)) if completed and policy=='PRODUCT_FUSED' else 0,
                        p90_physicalization_delay=float(np.quantile(completed,.9)) if completed and policy=='PRODUCT_FUSED' else 0,
                        max_physicalization_delay=max(completed) if completed and policy=='PRODUCT_FUSED' else 0,
                        median_observed_virtual_window=float(np.median(windows)) if windows and policy=='PRODUCT_FUSED' else 0,
                        never_physicalized_count=sum(c.label!='M' for c in model.cells) if policy=='PRODUCT_FUSED' else row['n']-max(qs[policy]),
                        metadata_peak_bytes=2*config['amplitude_bytes']*product_peak if policy=='PRODUCT_FUSED' else 0,
                        persistent_backing_only=True)
            if groups:
                traffic=compose_traffic(qs[policy],pe,groups,policy,config['amplitude_bytes'])
                record.update(traffic,reduction_vs_eager=eager/traffic['predicted_total_bytes'],
                              reduction_boundary_fused=eager/traffic['predicted_total_boundary_fused'],
                              reduction_resident_lower_bound=eager/traffic['predicted_total_resident_lower_bound'])
            else:
                record.update(materialization_read_bytes=sum(e['read_bytes'] for e in pe),materialization_write_bytes=sum(e['write_bytes'] for e in pe))
            results.append(record)
            if m==config['primary_m'] and groups and row['primary_eligible']:
                for amplitude in config['amplitude_byte_sensitivity']:
                    for chunk in [1]+config['chunk_bytes']:
                        traffic=compose_traffic(qs[policy],pe,groups,policy,amplitude,chunk)
                        eg=compose_traffic(qs['EAGER_FULL'],[],groups,'EAGER_FULL',amplitude,chunk)
                        sensitivity.append(dict(**key,policy=policy,m=m,amplitude_bytes=amplitude,chunk_bytes=chunk,
                                                predicted_total_bytes=traffic['predicted_total_bytes'],
                                                reduction_vs_eager=eg['predicted_total_bytes']/traffic['predicted_total_bytes']))
    if position%20==0: print(f'{position}/{len(summary)} views processed',flush=True)
trace_file.close()
write_csv(out/'workload_policy_results.csv',results)
write_csv(out/'physicalization_events.csv',events)
write_csv(out/'qubit_lifetimes.csv',lifetimes)
write_csv(out/'sensitivity.csv',sensitivity)
write_csv(out/'oracle_exclusions.csv',exclusions,['workload_id','representation','source','family','n','primary_eligible','m','error_type','error_message'])
batch=[]
for q in [8,16,24]:
    for k in range(1,9):
        cost=materialization_cost('PRODUCT_FUSED',q,k)
        batch.append(dict(old_q=q,batch_size=k,**cost,fusion_reduction=cost['standalone_expand_then_gate_bytes']/cost['standalone_fused_bytes']))
write_csv(out/'batch_sensitivity.csv',batch)
manifest=dict(run_id=stamp,raw_directory=str(raw),code_sha256=common.code_hashes(),input_summary_sha256=sha256('results/circuit_summary.csv'),
              external_repositories_sha256=sha256('results/manifests/external_repositories.csv'),primary_eligible=int(summary.primary_eligible.sum()),
              real_circuits=int(summary[~summary.source.isin(['generated','synthetic_control'])].workload_id.nunique()),views=len(summary),
              output_sha256={str(out/name):sha256(out/name) for name in [
                  'workload_policy_results.csv','physicalization_events.csv','qubit_lifetimes.csv',
                  'gate_event_trace.csv','sensitivity.csv','oracle_exclusions.csv','batch_sensitivity.csv']})
(out/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
(raw/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
with (out/'reproducibility.txt').open('w') as f:
    f.write('trace-driven static model — NOT measured SSD traffic\n'+json.dumps(manifest,indent=2)+'\n')
    for command in [['git','rev-parse','HEAD'],['git','rev-parse','HEAD^'],['git','status','--short'],['conda','info'],[sys.executable,'--version'],[sys.executable,'-m','pip','freeze']]:
        f.write('$ '+' '.join(command)+'\n'+subprocess.check_output(command,text=True)+'\n')
    f.write(Path('results/manifests/external_repositories.csv').read_text())
    f.write('\nCONFIG\n'+Path('configs/materialization_model.yaml').read_text())
common.check_frozen()
print('Model complete:',manifest['real_circuits'],'real circuits;',manifest['primary_eligible'],'primary candidates')
