"""Offline collection with fixed denominators; never invokes a model."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from engine import HERE, ROOT, evaluate, feedback, base
from build import save, digest
from run import revision_prompt

ARMS = ('initial', 'self_review', 'counterexample')
MODEL = 'gpt-5.6-sol'


def summarize(here: Path) -> dict:
    rows = []
    for rep in range(1, 6):
        for arm in ARMS:
            folder = here / 'runs' / MODEL / f'{rep:02}-{arm}'
            row = {'replicate': rep, 'arm': arm, 'attempted': (folder / 'started.json').exists(),
                   'execution_success': None, 'format_valid': None, 'finite_semantic_pass': None,
                   'status': 'not_run', 'final_tests_executed': 0, 'model_seconds': 0,
                   'checker_seconds': 0, 'usage': {}}
            if (folder / 'metadata.json').exists():
                meta = json.loads((folder / 'metadata.json').read_text())
                row['execution_success'] = bool(meta['turn_completed'] and meta['exit_code'] == 0
                                                 and not meta['errors'] and not meta['tool_items'])
                row['model_seconds'] = meta['elapsed_seconds']
                row['status'] = 'unjudged' if row['execution_success'] else (
                    'request_timeout' if meta['timeout'] else 'infrastructure_error')
                for usage in meta['usage']:
                    for key, value in usage.items():
                        if isinstance(value, int):
                            row['usage'][key] = row['usage'].get(key, 0) + value
            elif row['attempted']:
                row['status'] = 'interrupted_or_running'
            if (folder / 'evaluation.json').exists():
                ev = json.loads((folder / 'evaluation.json').read_text())
                result = ev['final']
                row.update(status=result['status'], format_valid=result['format_valid'],
                           finite_semantic_pass=result['finite_semantic_pass'],
                           final_tests_executed=result['tests_executed'],
                           checker_seconds=ev['development']['elapsed_seconds'] + result['elapsed_seconds'])
                row['failed_obligations'] = dict(Counter(f['obligation'] for t in result['tests'] for f in t.get('failures', [])))
                if not row['execution_success']:
                    row.update(status='infrastructure_error', finite_semantic_pass=None)
            rows.append(row)
    arms = {}
    for arm in ARMS:
        selected = [r for r in rows if r['arm'] == arm]
        usage = Counter()
        for r in selected:
            usage.update(r['usage'])
        arms[arm] = {'planned': 5, 'attempted': sum(r['attempted'] for r in selected),
                     'execution_success': sum(r['execution_success'] is True for r in selected),
                     'format_valid': sum(r['format_valid'] is True for r in selected),
                     'finite_pass': sum(r['finite_semantic_pass'] is True for r in selected),
                     'final_tests_executed': sum(r['final_tests_executed'] for r in selected),
                     'statuses': dict(Counter(r['status'] for r in selected)), 'usage': dict(usage),
                     'model_seconds': sum(r['model_seconds'] for r in selected),
                     'checker_seconds': sum(r['checker_seconds'] for r in selected)}
    pairs = []
    for rep in range(1, 6):
        pairs.append({'replicate': rep, **{r['arm']: r['finite_semantic_pass']
                     for r in rows if r['replicate'] == rep}})
    feedback_states = []
    for rep in range(1, 6):
        path = here / f'feedback-{rep:02}.json'
        if path.exists():
            item = json.loads(path.read_text())
            feedback_states.append({'replicate': rep, 'status': item['status'],
                                    'counterexample_supplied': 'counterexample' in item})
    return {'created_utc': datetime.now(timezone.utc).isoformat(), 'mother_cases': 1,
            'planned_requests': 15, 'actual_requests': sum(r['attempted'] for r in rows),
            'arms': arms, 'pairs': pairs, 'feedback_states': feedback_states, 'rows': rows,
            'whole_migration_success': None, 'quantum_advantage': None}


def without_elapsed(value):
    if isinstance(value, dict):
        return {k: without_elapsed(v) for k, v in value.items() if k != 'elapsed_seconds'}
    if isinstance(value, list):
        return [without_elapsed(v) for v in value]
    return value


def audit(here=HERE):
    protocol = json.loads((here / 'protocol.json').read_text())
    protected = json.loads((here / 'protected_before.json').read_text())
    errors = []
    for path, sha in {**protected, **protocol['source_sha256']}.items():
        if not (ROOT / path).exists() or digest(ROOT / path) != sha:
            errors.append('Changed source: ' + path)
    tests = json.loads((here / 'tests.json').read_text())
    for t in tests['development'] + tests['final']:
        if base.expected('cover', t['input']) != t['expected']:
            errors.append('Oracle mismatch: ' + t['id'])
    original = (here / 'prompt.txt').read_text()
    replayed = 0
    for rep in range(1, 6):
        initial = here / 'runs' / MODEL / f'{rep:02}-initial' / 'response.txt'
        initial_raw = initial.read_text() if initial.exists() else ''
        fpath = here / f'feedback-{rep:02}.json'
        diagnostic = json.loads(fpath.read_text()) if fpath.exists() else None
        if diagnostic is not None and feedback(initial_raw, tests['development']) != diagnostic:
            errors.append('Feedback not bound to initial: ' + str(rep))
        for arm in ARMS:
            ident = f'{rep:02}-{arm}'
            folder = here / 'runs' / MODEL / ident
            prompt = here / 'inputs' / f'{ident}.txt'
            if prompt.exists():
                wanted = original if arm == 'initial' else revision_prompt(original, initial_raw, arm, diagnostic)
                if prompt.read_text() != wanted:
                    errors.append('Prompt boundary mismatch: ' + ident)
            if (folder / 'metadata.json').exists():
                meta = json.loads((folder / 'metadata.json').read_text())
                if digest(prompt) != meta['input_sha256']:
                    errors.append('Prompt hash: ' + ident)
                if meta['tool_items']:
                    errors.append('Tools used: ' + ident)
                if (folder / 'response.txt').exists() and digest(folder / 'response.txt') != meta.get('raw_output_sha256'):
                    errors.append('Raw response hash: ' + ident)
            if (folder / 'evaluation.json').exists():
                raw = (folder / 'response.txt').read_text()
                old = json.loads((folder / 'evaluation.json').read_text())
                fresh = {key: evaluate(raw, tests[key]) for key in ('development', 'final')}
                if without_elapsed(old) != without_elapsed(fresh):
                    errors.append('Replay mismatch: ' + ident)
                replayed += 1
    return {'passed': not errors, 'errors': errors, 'protected_files_unchanged': len(protected) if not errors else None,
            'replayed_responses': replayed, 'definition_expectations_checked': sum(map(len, tests.values())),
            'protocol_source_files_checked': len(protocol['source_sha256']),
            'prompt_boundaries': 'Reconstructed from public task + same initial + development-only feedback; final tests absent.',
            'runtime_isolation': 'Reused bwrap transport; tools disabled; private repository not mounted. Not a general security certification.'}


def main():
    result = summarize(HERE)
    checks = audit()
    save(HERE / 'SUMMARY.json', result)
    save(HERE / 'audit.json', checks)
    print(json.dumps({'arms': result['arms'], 'audit': checks}, ensure_ascii=False, indent=2))
    if not checks['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
