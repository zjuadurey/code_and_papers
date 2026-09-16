"""Exact reference validation before any GBSA timed run; no Phase A writes."""
import _e2e_common
import hashlib, json, tempfile, time
from pathlib import Path
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from htp.e2e.gbsa import GBSAReproduction
from htp.e2e.runtime import Counters
from htp.e2e.workloads import suite, lower

def cases():
    for n in [6,8,10,12]:
        for family,circuit,_ in suite(n):yield f'{family}_{n}',lower(circuit)
    rng=np.random.default_rng(20260916)
    for k in range(160):
        n=int(rng.integers(3,10));c=QuantumCircuit(n)
        for _ in range(35):
            if rng.random()<.65:c.u(*rng.uniform(-3,3,3),int(rng.integers(n)))
            else:c.cx(*rng.choice(n,2,replace=False))
        yield f'random_{k}',c
    for kind in ['no_materialization','staged','early_entangling']:
        c=QuantumCircuit(8);c.h(range(8))
        if kind=='staged':
            c.rz(.7,7);c.cx(0,1);c.ry(.3,4);c.cx(4,5);c.cx(1,5);c.cx(5,7)
        if kind=='early_entangling':
            c.rz(.2,range(8))
            for j in range(7):c.cx(j,j+1)
        yield kind,lower(c)

start=time.time();rows=[]
for name,c in cases():
    reference=Statevector(c).data
    with tempfile.TemporaryDirectory(prefix='gbsa-correctness-') as d:
        count=Counters();m=min(5,c.num_qubits);t=min(2,m-1)
        model=GBSAReproduction(c,m,t,d,count);model.run()
        out=model.full_small_state()
        error=float(np.max(np.abs(reference-out)))
        assert error<1e-10,(name,error)
        rows.append(dict(case=name,n=c.num_qubits,max_abs_error=error,
            gate_blocks=model.gate_blocks,swap_passes=model.swap_passes))
    if len(rows)%20==0:print('validated',len(rows),flush=True)
result=dict(cases=len(rows),failures=0,validated=True,seed=20260916,tolerance=1e-10,
    elapsed_s=time.time()-start,methods=['Qiskit Statevector','GBSA reproduction'],
    source_sha256=hashlib.sha256(Path('src/htp/e2e/gbsa.py').read_bytes()).hexdigest(),
    comparisons=rows)
Path('results/gbsa_comparison/correctness.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'GBSA file-backed exact cases',flush=True)
