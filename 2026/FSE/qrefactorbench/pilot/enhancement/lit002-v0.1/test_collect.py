import json
from collect import summarize, without_elapsed, ARMS, MODEL


def test_empty_run_is_not_success(tmp_path):
    result = summarize(tmp_path)
    assert result['actual_requests'] == 0
    for arm in ARMS:
        assert result['arms'][arm]['planned'] == 5
        assert result['arms'][arm]['finite_pass'] == 0
        assert result['arms'][arm]['statuses'] == {'not_run': 5}


def test_infrastructure_not_overridden_by_a_pass(tmp_path):
    folder = tmp_path / 'runs' / MODEL / '01-initial'
    folder.mkdir(parents=True)
    (folder / 'started.json').write_text('{}')
    (folder / 'metadata.json').write_text(json.dumps({
        'turn_completed': False, 'exit_code': 1, 'errors': ['error'], 'tool_items': [],
        'elapsed_seconds': 2, 'timeout': False, 'usage': []}))
    result = {'status': 'passed', 'format_valid': True, 'finite_semantic_pass': True,
              'tests_executed': 98, 'elapsed_seconds': 0.2, 'tests': []}
    (folder / 'evaluation.json').write_text(json.dumps({'final': result, 'development': result}))
    summary = summarize(tmp_path)
    assert summary['actual_requests'] == 1
    assert summary['arms']['initial']['finite_pass'] == 0
    assert summary['rows'][0]['status'] == 'infrastructure_error'


def test_elapsed_is_the_only_replay_field_ignored():
    assert without_elapsed({'elapsed_seconds': 1, 'tests': [{'elapsed_seconds': 2, 'status': 'passed'}]}) == {
        'tests': [{'status': 'passed'}]}
