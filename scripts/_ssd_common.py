import _common
from htp.storage.benchmark_config import ROOT,OUT,BINARY,config,bench_dir
import hashlib
import json
from pathlib import Path

(OUT/'logs').mkdir(parents=True,exist_ok=True)

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def frozen_check():
    r=json.loads((OUT/'prior_results_frozen.json').read_text())
    for p,h in r['sha256'].items():
        assert digest(p)==h,f'Prior result changed: {p}'
    return len(r['sha256'])

def code_hashes():
    files=list((ROOT/'native/ssd_materialization').glob('*'))+list((ROOT/'src/htp/storage').glob('*.py'))
    files+=list((ROOT/'scripts').glob('*ssd*'))+[ROOT/'configs/ssd_materialization.yaml']
    return {str(p.relative_to(ROOT)):digest(p) for p in files if p.is_file()}
