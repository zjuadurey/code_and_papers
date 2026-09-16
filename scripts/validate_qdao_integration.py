import _e2e_common
import hashlib, json, tempfile, time
from pathlib import Path
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from htp.e2e.runtime import Counters, QThinEngine, original
from htp.e2e.workloads import suite, lower

def cases():
    for n in [6,8,10,12]:
        for family, circuit, _ in suite(n):
            yield f'{family}_{n}', lower(circuit)
    rng = np.random.default_rng(20260916)
    for k in range(160):
        n = int(rng.integers(3,10)); c = QuantumCircuit(n)
        for _ in range(35):
            if rng.random() < .65: c.u(*rng.uniform(-3,3,3),int(rng.integers(n)))
            else: c.cx(*rng.choice(n,2,replace=False))
        yield f'random_{k}',c
    for kind in ['no_materialization','staged','early_entangling']:
        c = QuantumCircuit(8)
        c.h(range(8))
        if kind == 'staged':
            c.rz(.7,7);c.cx(0,1);c.ry(.3,4);c.cx(4,5);c.cx(1,5);c.cx(5,7)
        if kind == 'early_entangling':
            c.rz(.2,range(8))
            for j in range(7):c.cx(j,j+1)
        yield kind,lower(c)

start=time.time(); rows=[]
for name,circuit in cases():
    reference=Statevector(circuit)
    with tempfile.TemporaryDirectory(prefix='qthin-correctness-') as d:
        count=Counters(); m=min(5,circuit.num_qubits);t=min(2,m-1)
        baseline=original(circuit,m,t,Path(d)/'original',count).full_small_state()
        qthin=QThinEngine(circuit,m,t,Path(d)/'thin',Counters());qthin.run()
        output=qthin.full_small_state()
        errors=[]
        for state in [baseline,output]:
            overlap=np.vdot(reference.data,state)
            phase=overlap/abs(overlap) if abs(overlap)>0 else 1
            errors.append(float(np.max(np.abs(state/phase-reference.data))))
        assert max(errors)<1e-10,(name,errors)
        rows.append(dict(case=name,n=circuit.num_qubits,qdao_error=errors[0],qthin_error=errors[1],
                         qphysical=len(qthin.physical)))
    if len(rows)%20==0:print('validated',len(rows),flush=True)
result=dict(cases=len(rows),failures=0,seed=20260916,tolerance=1e-10,elapsed_s=time.time()-start,
            runtime_sha256=hashlib.sha256(Path('src/htp/e2e/runtime.py').read_bytes()).hexdigest(),
            methods=['Qiskit Statevector','Original QDAO','QThin'],comparisons=rows)
Path('results/qdao_end_to_end/correctness.json').write_text(json.dumps(result,indent=2))
print('PASS',len(rows),'three-way exact comparisons')
