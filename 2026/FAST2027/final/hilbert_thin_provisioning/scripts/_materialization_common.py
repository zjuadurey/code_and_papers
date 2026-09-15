import _common
import hashlib
import json
import subprocess
from pathlib import Path
import yaml
from htp.loaders import sha256

OUT=Path('results/materialization_model')
CONFIG=yaml.safe_load(Path('configs/materialization_model.yaml').read_text())


def check_frozen():
    frozen=json.loads((OUT/'prior_results_frozen.json').read_text())
    for p,h in frozen['sha256'].items():
        assert sha256(p)==h,f'Previous result changed: {p}'
    return frozen


def code_hashes():
    return {str(p):sha256(p) for base in ['src/htp','scripts','configs'] for p in sorted(Path(base).glob('*')) if p.is_file()}


def read_view(row):
    from htp.loaders import load_circuits,unitary_prefix,semantic_circuit,lower
    assert sha256(row['input_path'])==row['source_sha256']
    c=load_circuits(row['input_path'])[int(row['circuit_index'])]
    c,_=unitary_prefix(c)
    return semantic_circuit(c) if row['representation']=='semantic' else lower(c)
