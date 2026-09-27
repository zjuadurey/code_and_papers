"""Offline collector regressions; fake metadata and copies of already saved output."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    spec = importlib.util.spec_from_file_location('repeat_collection_test', HERE / 'collect.py')
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
finally:
    sys.path.remove(str(HERE))


@pytest.fixture
def example(tmp_path, monkeypatch):
    entry = c.load(HERE / 'protocol.json')['entries'][0]
    _, refs = c.evaluation.references('C')
    ref = next(r for r in refs if r['mother_case_id'] == entry['case_id'])
    source = HERE / 'runs/deepseek-flash/lit-001'
    folder = tmp_path / 'runs/deepseek-flash/lit-001'
    folder.mkdir(parents=True)
    raw = (source / 'response.txt').read_text()
    meta = c.load(source / 'metadata.json')
    (folder / 'response.txt').write_text(raw)
    (folder / 'metadata.json').write_text(json.dumps(meta))
    monkeypatch.setattr(c, 'HERE', tmp_path)
    monkeypatch.setattr(c.runner, 'ROOT', tmp_path)
    return entry, ref, folder, meta


def test_valid_does_not_mean_semantic_pass(example):
    entry, ref, _, _ = example
    row, _, _ = c.inspect('deepseek-flash', entry, ref)
    assert row['valid'] and row['status'] == 'valid'
    assert row['task_pass'] is None
    assert row['semantic_review'] == 'pending_transcription'


@pytest.mark.parametrize('state,change', [
    ('candidate_budget_exceeded', {'finish_reason': 'length', 'response_complete': False}),
    ('infrastructure_error', {'http_status': 503}),
    ('protocol_violation', {'unexpected_tool_calls': True}),
])
def test_delivery_failures_not_scored_as_semantic_errors(example, state, change):
    entry, ref, folder, meta = example
    meta.update(change)
    (folder / 'metadata.json').write_text(json.dumps(meta))
    row, _, _ = c.inspect('deepseek-flash', entry, ref)
    assert row['status'] == state and not row['valid']
    assert row['task_pass'] is None


def test_corrupt_raw_is_infrastructure_failure(example):
    entry, ref, folder, _ = example
    (folder / 'response.txt').write_text('{}')
    row, _, _ = c.inspect('deepseek-flash', entry, ref)
    assert row['status'] == 'infrastructure_error'


def test_duplicate_json_key_not_repaired(example):
    entry, ref, folder, meta = example
    (folder / 'response.txt').write_text('{"case_id":"a","case_id":"b"}')
    meta['response_sha256'] = c.runner.digest(folder / 'response.txt')
    (folder / 'metadata.json').write_text(json.dumps(meta))
    row, _, _ = c.inspect('deepseek-flash', entry, ref)
    assert row['status'] == 'invalid_format' and not row['valid']


def test_missing_attempt_is_not_run(example):
    entry, ref, folder, _ = example
    (folder / 'response.txt').unlink()
    (folder / 'metadata.json').unlink()
    row, _, _ = c.inspect('deepseek-flash', entry, ref)
    assert row['status'] == 'not_run'


@pytest.mark.parametrize('budget_failure', [False, True])
def test_collection_preserves_all_slots_and_partial_reference_denominators(tmp_path, monkeypatch, budget_failure):
    protocol = c.load(HERE / 'protocol.json')
    old = c.load(HERE.parent / '20260922-c-v0.1/predictions.gpt-5.6-sol.json')
    _, refs = c.evaluation.references('C')
    refs = {r['mother_case_id']: r for r in refs}
    predictions = {p['case_id']: p for p in old}
    for model in c.runner.MODELS:
        for entry in protocol['entries']:
            case_id = entry['case_id']
            folder = tmp_path / 'runs' / model / case_id
            folder.mkdir(parents=True)
            (folder / 'response.txt').write_text(json.dumps(predictions[refs[case_id]['case_id']]))
            digest = c.runner.digest(folder / 'response.txt')
            meta = {'exit_code': 0, 'turn_completed': True, 'raw_output_sha256': digest,
                    'response_sha256': digest, 'http_status': 200, 'response_complete': True,
                    'finish_reason': 'length' if budget_failure and model == 'deepseek-v4-pro' and case_id == 'lit-002' else 'stop'}
            (folder / 'metadata.json').write_text(json.dumps(meta))
    monkeypatch.setattr(c, 'HERE', tmp_path)
    monkeypatch.setattr(c.runner, 'ROOT', tmp_path)
    monkeypatch.setattr(c.runner, 'verify', lambda: protocol)
    c.collect()
    result = c.load(tmp_path / 'SUMMARY.json')
    assert sum(len(m['rows']) for m in result['models'].values()) == 40
    pro = result['models']['deepseek-v4-pro']
    assert pro['valid_responses'] == (9 if budget_failure else 10)
    assert pro['reference_positive_diagnostics']['fixed_population'] == 7
    assert pro['reference_positive_diagnostics']['unavailable_submissions'] == int(budget_failure)
    assert pro['full_population_evaluation_available'] is not budget_failure
    assert result['task_pass'] is None
    with pytest.raises(FileExistsError):
        c.collect()
