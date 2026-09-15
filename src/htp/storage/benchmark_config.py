from pathlib import Path
import os
import yaml
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'results/ssd_materialization'
BINARY=ROOT/'build/ssd_materialization/qthin_storage'

def config():
    return yaml.safe_load((ROOT/'configs/ssd_materialization.yaml').read_text())

def bench_dir():
    c=config()
    p=Path(os.environ.get('HTP_SSD_BENCH_DIR') or c['benchmark_dir'] or OUT/'workdir').resolve()
    if p==Path('/dev') or Path('/dev') in p.parents: raise ValueError('Device paths prohibited')
    p.mkdir(parents=True,exist_ok=True)
    if not p.is_dir(): raise ValueError('Benchmark directory required')
    return p

def disk_plan(q,guest_free,host_free=None,input_exists=False,fraction=.7):
    if not 1<=q<=40 or not 0<fraction<=.7: raise ValueError('Invalid size/fraction')
    needed=(2 if input_exists else 3)*(16<<q)
    free=min(guest_free,host_free) if host_free is not None else guest_free
    # Reserve a further 256 MiB for filesystem bookkeeping and small result files.
    return dict(required_bytes=needed+256*1024**2,budget_bytes=int(free*fraction),
                fits=needed+256*1024**2<=int(free*fraction))

def product_vector(name,seed):
    if name=='plus': return np.array([1,1],complex)/np.sqrt(2)
    if name=='basis0': return np.array([1,0],complex)
    if name=='basis1': return np.array([0,1],complex)
    if name!='random_seeded':raise ValueError('Unknown product-state generator')
    rng=np.random.default_rng(seed)
    a=rng.normal(size=2)+1j*rng.normal(size=2)
    return a/np.linalg.norm(a)

def factor_args(v):
    return ['--ar',repr(float(v[0].real)),'--ai',repr(float(v[0].imag)),
            '--br',repr(float(v[1].real)),'--bi',repr(float(v[1].imag))]

def logical_mapping(q,virtual_label):
    # Existing addresses remain unchanged when the virtual wire becomes bit q.
    if q<0 or virtual_label in range(q):raise ValueError('New logical label must be distinct from existing wires')
    return {**{i:i for i in range(q)},virtual_label:q}
