"""Replay an actual model-produced candidate without any model invocation."""
import argparse
import json
from pathlib import Path

import engine as e


def replay(source: Path, output: Path) -> None:
    summary = json.loads((source / 'summary.json').read_text())
    manifest = json.loads((source / 'manifest.json').read_text())
    for name, digest in manifest.items():
        if e.sha(source / name) != digest:
            raise ValueError(f'Frozen run changed: {name}')
    candidates = list(source.glob('tool-*/candidate.json'))
    selected = [p for p in candidates if __import__('hashlib').sha256(
        json.loads(p.read_text())['qasm'].encode()).hexdigest() == summary['candidate_sha256']]
    if not selected: raise ValueError('No candidate matches the final conclusion')
    candidate = json.loads(selected[-1].read_text())
    output.mkdir(parents=True, exist_ok=False)
    verify_dir, cost_dir = output / 'verification', output / 'cost'
    verify_dir.mkdir(); cost_dir.mkdir()
    e.save(output / 'candidate.json', candidate)
    verified = e.verify(candidate, verify_dir)
    cost = e.compare(candidate, verified, cost_dir)
    previous = json.loads((selected[-1].parent / 'verification.json').read_text())
    old_costs = [json.loads(p.read_text()) for p in sorted(source.glob('tool-*/resource-analysis.json'))]
    old_resource = [r for r in old_costs if r['application_sha256'] == verified['application_sha256']][-1]
    resource = json.loads((cost_dir / 'resource-analysis.json').read_text())
    result = {'source_run': str(source), 'model_calls': 0,
        'behavior_passed': verified['status'] == 'passed',
        'simulation_identical': previous == verified,
        'resource_estimates_identical': old_resource['estimation_runs'] == resource['estimation_runs'],
        'local_host_costs': 'remeasured; expected to vary by machine/load',
        'complete_cost_points': len(cost['points'])}
    e.save(output / 'replay.json', result)
    e.save(output / 'manifest.json', {str(p.relative_to(output)): e.sha(p)
                                    for p in sorted(output.rglob('*')) if p.is_file()})
    print(json.dumps(result, indent=2))
    if not result['behavior_passed'] or not result['resource_estimates_identical']:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    replay(args.run.resolve(), args.output.resolve())
