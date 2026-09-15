import _common
import argparse
import json
import os
from pathlib import Path
import yaml
from htp.workload_discovery import scan, select, write_csv, FAILURE_FIELDS

parser = argparse.ArgumentParser()
parser.add_argument('--prior-repo', default=os.environ.get('HTP_PRIOR_QDAO_REPO'))
args = parser.parse_args()
config = yaml.safe_load(Path('configs/workloads.yaml').read_text())
analysis = yaml.safe_load(Path('configs/analysis.yaml').read_text())
sources = dict(config['sources'])
if args.prior_repo:
    prior = Path(args.prior_repo).expanduser().resolve()
    if not prior.is_dir():
        raise ValueError(f'Provided prior repository does not exist: {prior}')
    sources['prior_local_qdao'] = str(prior)
    # Inventory only; never execute unknown code.
    Path('results/manifests/prior_python_scripts.txt').write_text('\n'.join(str(p.relative_to(prior)) for p in sorted(prior.rglob('*.py'))))
rows, failures = [], []
for source, root in sources.items():
    found, failed = scan(root, source, config)
    rows.extend(found)
    failures.extend(failed)
    print(source, 'files/circuits', len(found), 'failures', len(failed), flush=True)
selected = select(rows, config, analysis)
for source in sources:
    write_csv(f'results/manifests/{source}.csv', [r for r in rows if r['source'] == source])
write_csv('results/manifests/selected_workloads.csv', selected)
write_csv('results/parse_failures.csv', failures, FAILURE_FIELDS)
Path('results/manifests/discovery.json').write_text(json.dumps(dict(
    prior_local_repository=args.prior_repo or 'not provided', scanned=len(rows), parse_success=sum(r['parse_ok'] for r in rows),
    parse_failures=len(failures), metadata_skips=sum(bool(r['metadata_skip']) for r in rows),
    selected=len(selected), source_counts={s:sum(r['source']==s for r in rows) for s in sources}), indent=2))
print('Selected',len(selected),'circuits without using outcome metrics')
