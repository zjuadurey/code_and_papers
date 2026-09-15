import _materialization_common as common
import argparse
import gc
import json
import resource
import subprocess
import sys
import time
import numpy as np
import pandas as pd
import psutil
from htp.fused_materialization import fused_cx_product_control,naive_cx_product_control

parser=argparse.ArgumentParser()
parser.add_argument('--worker',choices=['naive','fused'])
parser.add_argument('--q',type=int)
args=parser.parse_args()
out,config=common.OUT,common.CONFIG

if args.worker:
    q=args.q
    if q not in config['microbenchmark_q']: raise ValueError('Unregistered benchmark size')
    size=1<<q
    backing=np.empty(size,dtype=np.complex128)
    backing.real.fill(1/np.sqrt(size));backing.imag.fill(0)
    factor=np.array([np.sqrt(.3),1j*np.sqrt(.7)])
    before=psutil.Process().memory_info().rss
    start=time.perf_counter()
    output=(naive_cx_product_control if args.worker=='naive' else fused_cx_product_control)(backing,factor,0)
    elapsed=time.perf_counter()-start
    # Access pages and check normalization without a full-size temporary.
    norm=float(np.vdot(output,output).real)
    assert abs(norm-1)<1e-10
    b=backing.nbytes;new=output.nbytes
    # NumPy does two compact input reads, not an ideal single streaming read.
    # naive: expansion 4B + output.copy 4B + branch permutation 2B.
    # fused: compact reads 2B + output writes 2B. These are array-pass estimates,
    # not measured cache/DRAM transactions.
    estimated_bytes=10*b if args.worker=='naive' else 4*b
    print(json.dumps(dict(q=q,policy=args.worker,wall_seconds=elapsed,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                         rss_before_kernel=before,logical_output_bytes=new,bytes_allocated_for_outputs=2*new if args.worker=='naive' else new,
                         algorithmic_kernel_bytes=b+3*new if args.worker=='naive' else b+new,
                         implementation_copy_volume_estimate=estimated_bytes,norm=norm)))
else:
    verification=json.loads((out/'verification.json').read_text())
    assert verification['status']=='PASS' and verification['false_virtual']==0 and verification['fused_correctness_cases']>=1000
    rows=[];skips=[]
    for q in config['microbenchmark_q']:
        required=5*(16<<q)+512*1024**2
        if psutil.virtual_memory().available<required*1.5:
            skips.append(dict(q=q,reason='available RAM guard',estimated_required_bytes=required));continue
        for repetition in range(config['microbenchmark_repeats']):
            for policy in (['naive','fused'] if repetition%2==0 else ['fused','naive']):
                process=subprocess.run([sys.executable,__file__,'--worker',policy,'--q',str(q)],capture_output=True,text=True,timeout=120,check=True)
                row=json.loads(process.stdout.strip());rows.append(dict(row,repetition=repetition))
                print(q,policy,round(row['wall_seconds'],4),'seconds',flush=True)
    pd.DataFrame(rows).to_csv(out/'microbenchmark.csv',index=False)
    (out/'microbenchmark_status.json').write_text(json.dumps(dict(status='PASS' if rows else 'SKIPPED',skips=skips,
        scope='CPU NumPy memory mechanism sanity check; NOT SSD traffic or simulator speedup',isolated_process_per_trial=True),indent=2))
    common.check_frozen()
