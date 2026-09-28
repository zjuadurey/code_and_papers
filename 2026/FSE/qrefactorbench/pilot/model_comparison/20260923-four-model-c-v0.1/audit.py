"""Offline handoff audit. Never launches inference or reads credentials."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import collect
import review_formulas as review
import run as runner

HERE, ROOT = runner.HERE, runner.ROOT


def audit():
    protocol = runner.verify()
    summary = runner.deep.load_document(HERE / 'SUMMARY.json')
    completion = runner.deep.load_document(HERE / 'run.completed.json')
    _, refs = collect.evaluation.references('C')
    refs = {r['mother_case_id']: r for r in refs}
    attempted, tools_used, links_checked = 0, 0, 0
    for model in runner.MODELS:
        stored = summary['models'][model]
        fresh, predictions = [], []
        for entry in protocol['entries']:
            row, response, meta = collect.inspect(model, entry, refs[entry['case_id']])
            fresh.append(row)
            if row['valid']:
                predictions.append(response)
            folder = HERE / 'runs' / model / entry['case_id']
            if not meta:
                continue
            attempted += 1
            assert meta['operator_retries'] == 0
            assert meta['input_sha256'] == entry['sha256']
            if model in runner.deep.MODELS:
                request = runner.deep.load_document(folder / 'request.json')
                assert request == runner.deep.payload({**protocol, **protocol['deepseek']}, model, entry)
                assert runner.digest(folder / 'request.json') == meta['request_sha256']
                if (folder / 'api_response.json').exists():
                    assert runner.digest(folder / 'api_response.json') == meta['api_response_sha256']
                tools_used += int(bool(meta.get('unexpected_tool_calls')))
            else:
                tools_used += len(meta['tool_items'])
                cmd = meta['command']
                assert '--ignore-user-config' in cmd and '--ignore-rules' in cmd and '--ephemeral' in cmd
                assert not any(str(ROOT) in arg for arg in cmd)
        assert fresh == stored['rows']
        assert len(fresh) == 10
        assert len(predictions) == stored['valid_responses']
        if len(predictions) == 10:
            profile = '/medium/subscription-codex' if model in runner.gpt.MODELS else '/high/direct-api'
            expected = collect.evaluation.evaluate(predictions, 'C', model + profile)
            assert expected == runner.deep.load_document(HERE / f'evaluation.{model}.json')
    assert attempted == completion['attempted']
    assert summary['planned_requests'] == 40
    assert tools_used == 0

    suite = {c['case_id']: c for c in review.v.load_suite()['cases']}
    transcriptions = runner.deep.load_document(HERE / 'semantic-review/transcriptions.json')
    results = runner.deep.load_document(HERE / 'semantic-review/results.json')['records']
    assert len(transcriptions) == len(results)
    for submission, record in zip(transcriptions, results):
        case = suite[submission['case_id']]
        replay = review.primary_check(case, submission) if submission['claim_scope'] == 'primary_objective_only' else review.v.evaluate(case, submission)
        assert all(record[key] == value for key, value in replay.items())
        regenerated = {t['id']: review.polynomial(submission['recipe'], t['input']) for t in case['tests']}
        assert regenerated == submission['claims']

    with tempfile.TemporaryDirectory(prefix='qrb-pivot-replay-') as temp:
        replay_path = Path(temp) / 'evidence'
        command = [sys.executable, '-B', str(HERE / 'pivot_counterexample.py'), '--output', str(replay_path)]
        replay_process = subprocess.run(command, capture_output=True, text=True, check=True)
        assert runner.deep.load_document(replay_path / 'result.json') == runner.deep.load_document(HERE / 'pivot-witness/result.json')
    pro_binding = runner.deep.load_document(HERE / 'pivot-witness/pro-binding.json')
    assert runner.digest(ROOT / pro_binding['response_path']) == pro_binding['response_sha256']
    pro_response = runner.deep.load_document(ROOT / pro_binding['response_path'])
    assert pro_response['plan']['formulation'] == pro_binding['quote']
    assert pro_response['plan']['output_decoding'] == pro_binding['output_decoding_quote']
    assert runner.digest(ROOT / pro_binding['shared_witness_path']) == pro_binding['shared_witness_sha256']

    docs = [ROOT / p for p in ('PROJECT_STATUS.md', 'NEXT_ACTIONS.md', 'CHANGELOG.md', 'TODO.md', 'DECISIONS.md', 'docs/research_log.md')]
    docs += list(HERE.glob('*.md'))
    for path in docs:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#') or '<' in target:
                continue
            target = target.split('#')[0]
            linked = (path.parent / target).resolve()
            # The audit's own output is created below after every other check passes.
            if linked != HERE / 'validation.json':
                assert linked.exists(), (str(path), target)
            links_checked += 1
    code = list(HERE.glob('*.py'))
    runner.save(HERE / 'validation.json', {
        'status': 'passed', 'attempted': attempted, 'planned': 40,
        'valid_submissions': sum(m['valid_responses'] for m in summary['models'].values()),
        'protected_files_unchanged': len(runner.deep.load_document(HERE / 'protected_before.json')),
        'input_fingerprints_checked': 10, 'observed_tool_events': tools_used,
        'operator_retries': 0, 'output_repairs': 0, 'semantic_transcriptions_replayed': len(results),
        'post_hoc_pivot_witness_replayed': True,
        'post_hoc_pivot_claims_bound': 2,
        'local_markdown_links_checked': links_checked,
        'offline_tests': 'review-collector-validation.json',
        'initial_audit_failure': 'The first audit reached link checking, then rejected its own not-yet-created validation.json. Self-output existence is now deferred until write; all other links remain checked.',
        'source_sha256': {str(p.relative_to(ROOT)): runner.digest(p) for p in code},
        'document_sha256': {str(p.relative_to(ROOT)): runner.digest(p) for p in docs},
        'task_pass': None, 'new_inference_calls_by_audit': 0,
        'limitations': ['Replay is not independent human semantic review.', 'No quantum implementation or advantage tested.']})
    assert (HERE / 'validation.json').is_file()
    print(json.dumps({'attempted': attempted, 'links_checked': links_checked, 'semantic_replayed': len(results)}))


if __name__ == '__main__':
    audit()
