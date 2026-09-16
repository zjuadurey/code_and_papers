import _e2e_common
import hashlib, json, platform, subprocess, sys
from pathlib import Path
import pandas as pd
import qiskit, qiskit_aer
from qiskit import qpy
from htp.e2e.workloads import suite, lower
root = Path('results/qdao_end_to_end')
root.mkdir(exist_ok=True)
rows = []
for n in [20,22,24,26]:
    for family, circuit, source in suite(n):
        circuit = lower(circuit)
        path = root/'inputs'/f'{family}_{n}.qpy'
        path.parent.mkdir(exist_ok=True)
        if path.exists():
            with path.open('rb') as f:
                old = qpy.load(f)[0]
            assert old == circuit
        else:
            with path.open('wb') as f: qpy.dump(circuit, f)
        rows.append(dict(workload_id=path.stem,family=family,n=n,source=source,input_file=str(path),
            hash=hashlib.sha256(path.read_bytes()).hexdigest(),gate_count=len(circuit.data),depth=circuit.depth(),
            representation='lowered_u_cx_optimization_0',m=16,t=12,threads=1,precision='complex128'))
pd.DataFrame(rows).to_csv('results/end_to_end_workloads.csv',index=False)
pd.DataFrame(rows).to_csv(root/'workloads.csv',index=False)
env = dict(python=sys.version,qiskit=qiskit.__version__,aer=qiskit_aer.__version__,kernel=platform.release(),
    qdao_sha='fb360e6670b9818a3d4e106fb21cf605838be0a4',m=16,t=12,threads=1,
    io_mode='QDAO npy buffered POSIX files',sync='fdatasync final surviving files only, identical for all systems',
    aer_state_injection='shared normalized set_statevector bridge; restore chunk norm after simulation',
    storage_environment='wsl2_ext4_vhdx',filesystem='ext4',device_counter_scope='shared guest-visible /dev/sdd',
    benchmark_dir=str((root/'workdir').resolve()),precision='complex128',
    git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
(root/'environment.json').write_text(json.dumps(env,indent=2))
print(pd.DataFrame(rows)[['workload_id','gate_count','depth']].to_string(index=False))
