"""Instantiate only an authorized size variant; preserve canonical manifest rows."""
import _e2e_common
import argparse
import csv
import fcntl
import hashlib
from pathlib import Path

from qiskit import qpy
from htp.e2e.workloads import suite, lower

p = argparse.ArgumentParser()
p.add_argument('--size', type=int, choices=[28], default=28)
p.add_argument('--families', nargs='+', choices=['cdkm_superposed', 'qaoa'], default=['cdkm_superposed'])
a = p.parse_args()
lock = open('build/e2e-performance.lock', 'a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
manifest = Path('results/end_to_end_workloads.csv')
original = manifest.read_bytes()
with manifest.open(newline='') as handle:
    reader = csv.DictReader(handle)
    columns = reader.fieldnames
    rows = list(reader)
selected = set(a.families)
additions = []
for family, circuit, source in suite(a.size):
    if family not in selected:
        continue
    circuit = lower(circuit)
    path = Path('results/end_to_end_scaling/inputs') / f'{family}_{a.size}.qpy'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with path.open('rb') as handle:
            assert qpy.load(handle)[0] == circuit
    else:
        with path.open('xb') as handle:
            qpy.dump(circuit, handle)
    row = dict(workload_id=path.stem, family=family, n=a.size, source=source,
        input_file=str(path), hash=hashlib.sha256(path.read_bytes()).hexdigest(),
        gate_count=len(circuit.data), depth=circuit.depth(),
        representation='lowered_u_cx_optimization_0', m=16, t=12, threads=1, precision='complex128')
    existing = [r for r in rows if r['workload_id'] == path.stem]
    if existing:
        assert all(str(row[k]) == existing[0][k] for k in columns)
    else:
        additions.append(row)
    selected.remove(family)
    if not selected:
        break
assert not selected
assert manifest.read_bytes() == original
with manifest.open('a', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=columns)
    writer.writerows(additions)
assert manifest.read_bytes().startswith(original)
print('Added canonical size variants:', [r['workload_id'] for r in additions])
