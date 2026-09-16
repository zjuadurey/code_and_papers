"""Serial, resume-safe Phase B. Phase A must be complete, frozen and idle."""
import _e2e_common
import argparse, fcntl, hashlib, json, os, random, shutil, subprocess, sys, time
from pathlib import Path
import pandas as pd
from htp.storage.environment_probe import host_free,host_volume

p=argparse.ArgumentParser();p.add_argument('--sizes',nargs='+',type=int,default=[20,22,24])
a=p.parse_args();root=Path('results/gbsa_comparison');(root/'raw').mkdir(exist_ok=True)
v=json.loads((root/'correctness.json').read_text())
assert v['validated'] and v['failures']==0 and v['cases']>=195
assert v['source_sha256']==hashlib.sha256(Path('src/htp/e2e/gbsa.py').read_bytes()).hexdigest()
for manifest in ['phase_a_hashes.json','previous_results_hashes.json']:
    for path,digest in json.loads((Path('results/qdao_end_to_end')/manifest).read_text()).items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
assert len(pd.read_csv('results/qdao_end_to_end/raw_runs.csv'))==144
lock=open('build/e2e-performance.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
df=pd.read_csv('results/end_to_end_workloads.csv');rng=random.Random(20260916)
host=host_volume() if 'microsoft' in os.uname().release.lower() else None
skips=[]
for n in a.sizes:
    if n==26:raise ValueError('26q requires completed Phase A 26q first')
    for repetition in range(3):
        rows=list(df[df.n==n].itertuples());rng.shuffle(rows)
        for row in rows:
            output=root/'raw'/f'{row.workload_id}_GBSA_{repetition}.json'
            if output.exists():
                saved=json.loads(output.read_text())
                assert saved['input_hash']==row.hash
                assert saved['gbsa_sha256']==v['source_sha256']
                continue
            free=shutil.disk_usage(root).free
            capacity=host_free(host['DriveLetter']) if host else None
            if capacity is not None:free=min(free,capacity)
            if 3*16*(1<<n)>free*.7:
                skips.append(dict(workload_id=row.workload_id,n=n,repetition=repetition,reason='LOW_DISK'))
                continue
            cmd=[sys.executable,'scripts/run_gbsa_case.py','--workload',row.workload_id,
                 '--repetition',str(repetition),'--output',str(output)]
            with (root/'execution_order.jsonl').open('a') as f:
                f.write(json.dumps(dict(command=cmd,start_unix=time.time(),free_bytes=free))+'\n')
            print('START',n,row.family,repetition,flush=True)
            subprocess.run(cmd,check=True,env=dict(os.environ,OMP_NUM_THREADS='1',
                OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
            records=[json.loads(f.read_text()) for f in sorted((root/'raw').glob('*.json'))]
            pd.DataFrame(records).to_csv(root/'raw_runs.csv',index=False)
pd.DataFrame(skips,columns=['workload_id','n','repetition','reason']).to_csv(root/'skipped_cases.csv',index=False)
print('PHASE B BATCH COMPLETE',flush=True)
