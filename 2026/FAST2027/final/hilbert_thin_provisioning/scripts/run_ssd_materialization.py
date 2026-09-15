"""Sequential, resumable storage experiment. Only owned temporary files are removed."""
import _ssd_common as common
import datetime,json,os,shutil,subprocess,sys,tempfile,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import psutil
from htp.storage.benchmark_config import disk_plan,product_vector,factor_args
from htp.storage.environment_probe import host_free
from htp.storage.result_schema import parse_native

out=common.OUT;cfg=common.config();environment=json.loads((out/'environment.json').read_text())
proof=json.loads((out/'correctness.json').read_text())
assert proof['status']=='PASS' and proof['incorrect_cases']==0 and proof['correctness_cases']>=2000
assert proof['binary_sha256']==common.digest(common.BINARY)
common.frozen_check()
primary_mode='direct' if environment['direct_io']['supported'] and 'direct' in cfg['io_modes'] else 'buffered'
directory=common.bench_dir();host_letter=(environment.get('host_volume') or {}).get('DriveLetter')
seed=cfg['random_seed'];rng=np.random.default_rng(seed)
planned=[]

def add_group(q,scenario,gate,state,chunk,mode,target,reps,study):
    policies=['NAIVE_BASIS','THIN_BASIS','FUSED_BASIS'] if scenario=='basis' else ['NAIVE_PRODUCT','PRODUCT_FUSED']
    for rep in range(reps):
        for policy in rng.permutation(policies):
            spec=dict(q_old=q,scenario=scenario,gate=gate,product_state=state,chunk_bytes=chunk*1024**2,
                      io_mode=mode,target=target,repetition=rep,study=study,policy=str(policy),
                      product_seed=seed+q*100+rep+['cx_product_control','cx_product_target','cz'].index(gate)*10000)
            spec['config_id']=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()[:20]
            spec['planned_order']=len(planned)
            planned.append(spec)

for q in cfg['q_values']:
    repetitions=cfg['repetitions_small'] if q<=28 else cfg['repetitions_large']
    # Random order of gate/state groups as well as the methods within each repetition.
    for chunk in cfg['chunk_mib']:
        groups=[(g,s) for g in cfg['gates'] for s in cfg['product_states']]
        rng.shuffle(groups)
        for gate,state in groups:add_group(q,'product',gate,state,chunk,primary_mode,cfg['target_bit'],repetitions,'main')
        add_group(q,'basis','cx_product_target','basis0',chunk,primary_mode,cfg['target_bit'],repetitions,'basis')
    if q in cfg['chunk_sensitivity_q']:
        for chunk in cfg['chunk_sensitivity_mib']:
            if chunk not in cfg['chunk_mib']:add_group(q,'product','cx_product_control','plus',chunk,primary_mode,cfg['target_bit'],cfg['sensitivity_repetitions'],'chunk')
    if primary_mode=='direct' and 'buffered' in cfg['io_modes'] and q in cfg['buffered_sensitivity_q']:
        add_group(q,'product','cx_product_control','plus',cfg['chunk_mib'][0],'buffered',cfg['target_bit'],cfg['sensitivity_repetitions'],'buffered')
    if q==cfg['high_target_q']:
        add_group(q,'product','cx_product_control','plus',16,primary_mode,cfg['high_target_bit'],cfg['sensitivity_repetitions'],'target')

pd.DataFrame(planned).to_csv(out/'benchmark_manifest.csv',index=False)
journal=out/'raw_runs.jsonl'
rows=[json.loads(line) for line in journal.read_text().splitlines() if line] if journal.exists() else []
for row in rows:assert row['binary_sha256']==proof['binary_sha256'],'Resume requires identical binary'
done={r['config_id'] for r in rows}
assert done <= {p['config_id'] for p in planned}, 'Existing results belong to a different configuration; use a separate result directory'
skips=[]
if (out/'skipped_cases.csv').exists():
    skips=pd.read_csv(out/'skipped_cases.csv').to_dict('records')
input_records=[]
if (out/'input_generation.csv').exists():input_records=pd.read_csv(out/'input_generation.csv').to_dict('records')

def save_skips():
    pd.DataFrame(skips,columns=['config_id','q_old','policy','study','io_mode','status','reason','required_bytes','budget_bytes','guest_free_bytes','host_free_bytes']).to_csv(out/'skipped_cases.csv',index=False,na_rep='NA')

def capacity(q,input_exists):
    guest=shutil.disk_usage(directory).free;host=host_free(host_letter)
    # Do not turn a transient host-audit failure into unlimited host capacity.
    if host_letter and host is None:raise RuntimeError('Cannot refresh VHDX host free-space audit')
    p=disk_plan(q,guest,host,input_exists,cfg['max_free_space_fraction'])
    return dict(**p,guest_free_bytes=guest,host_free_bytes=host)

def skip(spec,p,reason):
    skips.append({**{k:spec[k] for k in ['config_id','q_old','policy','study','io_mode']},
                  'status':'SKIPPED','reason':reason,**{k:p[k] for k in ['required_bytes','budget_bytes','guest_free_bytes','host_free_bytes']}})
    save_skips()

mask=(1<<64)-1
def component(index):
    z=(index+seed+0x9e3779b97f4a7c15)&mask;z=((z^(z>>30))*0xbf58476d1ce4e5b9)&mask
    z=((z^(z>>27))*0x94d049bb133111eb)&mask;z^=z>>31
    return (z>>11)*2.**-53-.5

def sample_output(path,q,gate,target,v):
    sample=np.random.default_rng(seed+q).integers(0,1<<(q+1),size=32)
    max_error=0.
    with path.open('rb',buffering=0) as f:
        for index in map(int,sample):
            old=index&((1<<q)-1);bit=(index>>q)&1;control=(old>>target)&1
            coefficient=v[bit]
            if gate=='cx_product_control' and bit:old^=1<<target
            elif gate=='cx_product_target':coefficient=v[bit^control]
            elif gate=='cz' and bit and control:coefficient=-coefficient
            expected=coefficient*complex(component(2*old),component(2*old+1))
            actual=np.frombuffer(os.pread(f.fileno(),16,index*16),np.complex128)[0]
            max_error=max(max_error,float(abs(actual-expected)))
    if max_error>1e-12:raise AssertionError(f'Large-file sample failed: {max_error}')
    return max_error

commands=[]
for q in cfg['q_values']:
    cases=[p for p in planned if p['q_old']==q and p['config_id'] not in done]
    if not cases:continue
    retry_ids={p['config_id'] for p in cases}
    skips=[s for s in skips if s['config_id'] not in retry_ids]
    save_skips()
    plan=capacity(q,False)
    if not plan['fits']:
        for spec in cases:skip(spec,plan,'combined input/output exceeds 70% guest/host free-space budget')
        print(f'SKIPPED q={q}: required={plan["required_bytes"]} budget={plan["budget_bytes"]}',flush=True)
        continue
    with tempfile.TemporaryDirectory(prefix=f'qthin-q{q}-',dir=directory) as temp:
        temp=Path(temp);input_path=temp/'input.bin'
        cmd=[str(common.BINARY),'--action','generate','--q',str(q),'--output',str(input_path),'--seed',str(seed)]
        print(f'Generating q={q}, {(16<<q)/1024**3:.2f} GiB; {len(cases)} scheduled runs',flush=True)
        r=subprocess.run(cmd,capture_output=True,text=True);commands.append(cmd);r.check_returncode()
        record=json.loads(r.stdout);record.update(q=q,file_path=str(input_path),retained=False,timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat())
        input_records.append(record);pd.DataFrame(input_records).to_csv(out/'input_generation.csv',index=False)
        for spec in cases:
            plan=capacity(q,True)
            if not plan['fits']:
                skip(spec,plan,'output exceeds current 70% guest/host free-space budget');continue
            output=temp/(spec['config_id']+'.bin');v=product_vector(spec['product_state'],spec['product_seed'])
            cmd=[str(common.BINARY),'--input',str(input_path),'--output',str(output),'--q',str(q),'--policy',spec['policy'],
                 '--gate',spec['gate'],'--target',str(spec['target']),'--chunk-bytes',str(spec['chunk_bytes']),'--mode',spec['io_mode']]+factor_args(v)
            if environment['device_stat_path']:cmd+=['--device-stat',environment['device_stat_path']]
            noise=dict(load_average_before=list(os.getloadavg()),available_memory_before=psutil.virtual_memory().available)
            commands.append(cmd);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
            r=subprocess.run(cmd,capture_output=True,text=True)
            (out/'logs'/f'{spec["config_id"]}.json').write_text(json.dumps(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2))
            r.check_returncode();measured=parse_native(r.stdout)
            error=sample_output(output,q,spec['gate'],spec['target'],v)
            row=dict(**measured)
            row.update(spec,actual_order=len(rows),timestamp=start,filesystem=environment['filesystem'],
                       storage_environment_class=environment['storage_environment_class'],device=environment['device'],
                       direct_io_supported=environment['direct_io']['supported'],sync_mode='fdatasync',
                       binary_sha256=proof['binary_sha256'],sample_max_abs_error=error,sample_count=32,
                       alpha_real=v[0].real,alpha_imag=v[0].imag,beta_real=v[1].real,beta_imag=v[1].imag,
                       force_materialization_control=(spec['gate']=='cx_product_target' and spec['product_state']=='plus'),
                       **noise,**{k:plan[k] for k in ['guest_free_bytes','host_free_bytes']})
            rows.append(row)
            with journal.open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
            pd.DataFrame(rows).to_csv(out/'raw_runs.csv',index=False,na_rep='NA')
            output.unlink()
            print(f'{len(rows)} / {len(planned)} | q={q} {spec["study"]} {spec["gate"]} {spec["product_state"]} {spec["policy"]} {spec["io_mode"]} {measured["total_elapsed_s"]:.3f}s',flush=True)
    print(f'Cleaned q={q} input and outputs',flush=True)

save_skips()
common.frozen_check()
with (out/'reproducibility.txt').open('w') as f:
    f.write('Measured regular-file storage path; no raw block writes.\n')
    for cmd in [['git','branch','--show-current'],['git','rev-parse','HEAD'],['git','rev-parse','HEAD^'],['git','status','--short'],
                [sys.executable,'--version'],['g++','--version'],['cmake','--version'],[sys.executable,'-m','pip','freeze'],['uname','-a']]:
        f.write('$ '+' '.join(cmd)+'\n'+subprocess.check_output(cmd,text=True)+'\n')
    f.write('\nENVIRONMENT\n'+(out/'environment.json').read_text())
    f.write('\nCONFIG\n'+json.dumps(cfg,indent=2)+'\nCONFIG SHA256 '+common.digest(common.ROOT/'configs/ssd_materialization.yaml'))
    f.write('\nCODE\n'+json.dumps(common.code_hashes(),indent=2)+'\nCOMMANDS\n'+json.dumps(commands,indent=2))
(out/'execution_status.json').write_text(json.dumps(dict(status='PASS',completed_runs=len(rows),planned_runs=len(planned),
    skipped_runs=len(skips),prior_files_unchanged=common.frozen_check(),workdir_files=list(map(str,directory.rglob('*')))),indent=2))
print('Experiment complete',len(rows),'measured runs;',len(skips),'skips',flush=True)
