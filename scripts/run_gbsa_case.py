"""One GBSA reproduction measurement, same boundaries/counters as Phase A."""
import _e2e_common
import argparse, hashlib, json, os, resource, shutil, time
from pathlib import Path
import pandas as pd
import psutil
from qiskit import qpy
from htp.e2e.runtime import Counters
from htp.e2e.gbsa import GBSAReproduction

p=argparse.ArgumentParser();p.add_argument('--workload',required=True)
p.add_argument('--repetition',type=int,required=True);p.add_argument('--output',required=True)
a=p.parse_args()
row=pd.read_csv('results/end_to_end_workloads.csv').set_index('workload_id').loc[a.workload]
assert hashlib.sha256(Path(row.input_file).read_bytes()).hexdigest()==row['hash']
with open(row.input_file,'rb') as f:circuit=qpy.load(f)[0]
directory=Path(a.output).parent.parent/'workdir'/f'{a.workload}_GBSA_{a.repetition}_{os.getpid()}'
directory.mkdir(parents=True,exist_ok=False)
def proc_io():
    return {k:int(v) for k,v in (s.split(':') for s in Path('/proc/self/io').read_text().splitlines())}
def device_io():
    path=Path('/sys/class/block/sdd/stat')
    if not path.exists():return {}
    v=list(map(int,path.read_text().split()))
    return dict(device_read_bytes=v[2]*512,device_write_bytes=v[6]*512)

metadata=dict(workload_id=a.workload,family=row.family,n=int(row.n),gate_count=int(row.gate_count),
    depth=int(row.depth),system='GBSA reproduction',repetition=a.repetition,input_hash=row['hash'],
    m=16,t=12,chunk_bits=16,threads=1,io_mode='buffered_npy',load_average=os.getloadavg(),
    available_memory_before=psutil.virtual_memory().available,
    aer_state_injection='shared normalized set_statevector')
for key,path in [('runtime','src/htp/e2e/runtime.py'),('gbsa','src/htp/e2e/gbsa.py'),
                 ('compatibility_patch','patches/qdao_current_qiskit.patch')]:
    metadata[key+'_sha256']=hashlib.sha256(Path(path).read_bytes()).hexdigest()
before_proc=proc_io();before_device=device_io();before_cpu=resource.getrusage(resource.RUSAGE_SELF)
count=Counters();start=time.perf_counter()
model=GBSAReproduction(circuit,16,12,directory,count);model.run()
elapsed=time.perf_counter()-start
after_cpu=resource.getrusage(resource.RUSAGE_SELF);after_device=device_io();after_proc=proc_io()
metadata.update(wall_time_s=elapsed,user_cpu_s=after_cpu.ru_utime-before_cpu.ru_utime,
    system_cpu_s=after_cpu.ru_stime-before_cpu.ru_stime,peak_rss_bytes=after_cpu.ru_maxrss*1024,
    algorithmic_read_bytes=count.read_bytes,algorithmic_write_bytes=count.write_bytes,
    file_read_bytes=count.file_read_bytes,file_write_bytes=count.file_write_bytes,
    compute_unit_count=count.compute_units,state_traversals=count.traversals,
    sync_time_s=count.sync_s,sync_barrier_count=count.sync_barrier_count,fdatasync_calls=count.fdatasync_calls,
    gbsa_gate_blocks=model.gate_blocks,gbsa_swap_passes=model.swap_passes,
    gbsa_swap_count=model.swap_count,gbsa_search_s=model.search_s,gbsa_swap_s=model.swap_s,
    final_logical_to_physical=model.logical_to_physical)
metadata.update({f'proc_{k}':after_proc[k]-before_proc[k] for k in before_proc})
metadata.update({k:after_device[k]-before_device[k] for k in before_device})
Path(a.output).write_text(json.dumps(metadata,indent=2)+'\n')
shutil.rmtree(directory)
print(json.dumps({k:metadata[k] for k in ['workload_id','repetition','wall_time_s',
    'algorithmic_read_bytes','algorithmic_write_bytes','gbsa_gate_blocks','gbsa_swap_passes']}),flush=True)
