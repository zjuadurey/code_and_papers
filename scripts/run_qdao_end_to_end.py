"""Sequential, resumable experiment orchestrator. No parallel timed processes."""
import _e2e_common
import argparse, fcntl, json, os, random, shutil, subprocess, sys, time
from pathlib import Path
import pandas as pd
from htp.storage.environment_probe import host_free,host_volume

p=argparse.ArgumentParser();p.add_argument('--sizes',nargs='+',type=int,default=[20,22,24])
p.add_argument('--systems',nargs='+',default=['QDAO','QThin'])
p.add_argument('--repetitions',type=int,default=3);p.add_argument('--families',nargs='+')
p.add_argument('--output',default='results/qdao_end_to_end');a=p.parse_args()
root=Path(a.output);(root/'raw').mkdir(parents=True,exist_ok=True)
verification=json.loads(Path('results/qdao_end_to_end/correctness.json').read_text())
assert verification['failures']==0 and verification['cases']>=100
lock=open('build/e2e-performance.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
df=pd.read_csv('results/end_to_end_workloads.csv')
rng=random.Random(20260916)
skips=[];sequence=[]
host=host_volume() if 'microsoft' in os.uname().release.lower() else None
for n in a.sizes:
    host_capacity=host_free(host['DriveLetter']) if host else None
    with (root/'capacity_checks.jsonl').open('a') as f:
        f.write(json.dumps(dict(n=n,time_unix=time.time(),host_free_bytes=host_capacity,
                               guest_free_bytes=shutil.disk_usage(root).free))+'\n')
    selected=df[df.n==n]
    if a.families:selected=selected[selected.family.isin(a.families)]
    for _,row in selected.iterrows():
        for repetition in range(a.repetitions):
            systems=a.systems.copy();rng.shuffle(systems)
            for system in systems:
                output=root/'raw'/f'{row.workload_id}_{system}_{repetition}.json'
                if output.exists():
                    assert json.loads(output.read_text())['input_hash']==row['hash']
                    continue
                free=shutil.disk_usage(root).free
                if host_capacity is not None:free=min(free,host_capacity)
                required=(16*(1<<n))*3
                if required>free*.7:
                    skips.append(dict(workload=row.workload_id,system=system,repetition=repetition,reason='LOW_DISK'))
                    continue
                cmd=[sys.executable,'scripts/run_e2e_case.py','--workload',row.workload_id,'--system',system,
                     '--repetition',str(repetition),'--output',str(output)]
                sequence.append(dict(command=cmd,start_unix=time.time()))
                with (root/'execution_order.jsonl').open('a') as f:f.write(json.dumps(sequence[-1])+'\n')
                print('START',n,row.family,system,repetition,flush=True)
                subprocess.run(cmd,check=True,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
                records=[json.loads(x.read_text()) for x in sorted((root/'raw').glob('*.json'))]
                pd.DataFrame([{k:v for k,v in r.items() if k!='events'} for r in records]).to_csv(root/'raw_runs.csv',index=False)
                events=[dict(workload_id=r['workload_id'],repetition=r['repetition'],**e) for r in records for e in r['events']]
                pd.DataFrame(events).to_csv(root/'qthin_events.csv',index=False)
pd.DataFrame(skips,columns=['workload','system','repetition','reason']).to_csv(root/'skipped_cases.csv',index=False)
print('BATCH COMPLETE',flush=True)
