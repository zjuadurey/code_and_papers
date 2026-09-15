import csv
import hashlib
import json
import os
import re
from pathlib import Path
import numpy as np
from .loaders import EXTENSIONS, sha256, load_circuits

FAILURE_FIELDS = ['source', 'file', 'sha256', 'format', 'error_type', 'error_message']


def write_csv(path, rows, fields=None):
    rows = list(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def infer_family(path):
    s = str(path).lower()
    if re.search(r'(^|[/_.-])hea([/_.-]|$)',s):
        return 'hea'
    rules = [(['adder', 'add_', 'multiplier', 'comparator', 'modular', 'square_root', 'arithmetic'], 'arithmetic'),
             (['grover', 'oracle'], 'grover_oracle'), (['inverseqft', 'qft'], 'qft'),
             (['qaoa'], 'qaoa'), (['efficient'], 'hea'),
             (['cliff'], 'clifford'), (['random', 'qv_', '/qv/', 'quantum_volume'], 'random'),
             (['qubit_mapping', 'queko'], 'mapping'), (['reversible', 'rev_circuit', 'toffoli', 'fredkin'], 'reversible'),
             (['/pe/', 'pea_', 'ipea', 'phase_estimation'], 'phase_estimation'),
             (['vqe', 'variational', 'uccsd'], 'vqe'), (['ising'], 'ising'),
             (['/bv/', 'bv_', 'bernstein'], 'bernstein_vazirani'),
             (['shor', 'factor'], 'factoring'), (['qec', 'error_correction'], 'qec'),
             (['cat_state', 'ghz', 'bell', 'wstate'], 'state_preparation'),
             (['qwalk', 'quantumwalk'], 'quantum_walk'), (['qram'], 'qram'),
             (['swap_test'], 'swap_test'), (['dnn', 'qcnn', 'qnn'], 'quantum_ml'),
             (['iqp'], 'iqp'), (['graph_state'], 'state_preparation'),
             (['hidden_linear_function'], 'hidden_linear_function'), (['quadratic_form'], 'arithmetic')]
    return next((family for tokens, family in rules if any(token in s for token in tokens)), 'unknown')


def scan(root, source, config):
    root = Path(root)
    rows, failures = [], []
    cache={}
    manifest=Path(f'results/manifests/{source}.csv')
    if manifest.exists():
        with manifest.open() as f:
            for old in csv.DictReader(f):
                if old['parse_ok']=='True':
                    cache.setdefault((old['path'],old['sha256']),[]).append(old)
    for index, path in enumerate(sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in EXTENSIONS)):
        relative = str(path.relative_to(root))
        digest = sha256(path)
        item = dict(source=source, path=relative, absolute_path=str(path.resolve()), sha256=digest,
                    format=path.suffix.lower(), bytes=path.stat().st_size, n=None, gate_count=None,
                    depth_if_parseable=None, family_if_inferable=infer_family(relative), parse_ok=False,
                    metadata_skip='', circuit_index=0)
        cached=cache.get((relative,digest),[])
        if cached:
            for old in cached:
                rows.append(dict(item,**{k:int(old[k]) for k in ['n','gate_count','depth_if_parseable','circuit_index']},parse_ok=True))
            continue
        n_hint = 0
        if path.suffix.lower() != '.qpy':
            with path.open(errors='replace') as f:
                head = f.read(65536)
            n_hint = sum(map(int, re.findall(r'\bqreg\s+\w+\[(\d+)\]', head)))
        if item['bytes'] > config['max_parse_bytes'] or n_hint > config['max_parse_qubits']:
            item.update(n=n_hint or None, metadata_skip='size_guard_not_attempted')
            rows.append(item)
            continue
        try:
            for ci, circuit in enumerate(load_circuits(path)):
                rows.append(dict(item, circuit_index=ci, n=circuit.num_qubits, gate_count=len(circuit.data),
                                 depth_if_parseable=circuit.depth(), parse_ok=True))
        except Exception as e:
            rows.append(item)
            failures.append(dict(source=source, file=relative, sha256=digest, format=path.suffix.lower(),
                                 error_type=type(e).__name__, error_message=str(e)[:1500]))
        if (index+1) % 200 == 0:
            print(f'{source}: scanned {index+1}', flush=True)
    return rows, failures


def select(rows, config, analysis):
    strata, seen, selected = {}, set(), []
    for row in rows:
        if not row['parse_ok']:
            row['selection_reason'] = row['metadata_skip'] or 'parse_failure'
        elif row['n'] > analysis['max_analysis_qubits'] or row['gate_count'] > analysis['max_analysis_gates']:
            row['selection_reason'] = 'analysis_size_guard'
        elif row['gate_count'] == 0 or row['n'] == 0:
            row['selection_reason'] = 'empty'
        elif (row['sha256'], row['circuit_index']) in seen:
            row['selection_reason'] = 'duplicate_source_bytes'
        elif '_transpiled' in row['path'] and any(r['source'] == row['source'] and r['path'] == row['path'].replace('_transpiled', '') for r in rows):
            row['selection_reason'] = 'paired_source_transpilation_duplicate'
        else:
            seen.add((row['sha256'], row['circuit_index']))
            key = (row['source'], row['family_if_inferable'], int(np.digitize(row['n'], config['size_bins'])),
                   int(np.digitize(row['gate_count'], config['gate_bins'])))
            strata.setdefault(key, []).append(row)
            row['selection_reason'] = 'stratum_not_selected'
    for key, candidates in sorted(strata.items()):
        # Even coverage of width/gate count; tie break is input hash, never results.
        candidates.sort(key=lambda r: (r['n'], r['gate_count'], r['sha256']))
        count = min(len(candidates), config['per_source_family_size_gate_stratum'])
        for idx in np.linspace(0, len(candidates)-1, count, dtype=int):
            row = candidates[idx]
            row['selection_reason'] = 'selected'
            selected.append(row.copy())
    return selected
