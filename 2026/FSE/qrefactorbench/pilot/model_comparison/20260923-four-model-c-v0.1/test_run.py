"""Offline scheduling/input tests. Never read a real key or call models."""
import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

SPEC = importlib.util.spec_from_file_location('four_model_repeat', Path(__file__).with_name('run.py'))
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)


def test_input_payload_excludes_private_evaluator_and_history():
    protocol = r.verify()
    for entry in protocol['entries']:
        payload = r.deep.payload({**protocol, **protocol['deepseek']}, 'deepseek-flash', entry)
        assert payload['messages'][1]['content'] == (r.HERE / 'inputs' / entry['file']).read_text()
        assert len(payload['messages']) == 2
        assert 'semantic_verification' not in payload['messages'][1]['content']
        assert 'tools' not in payload


@pytest.mark.parametrize('gpt_error,deep_error,expected', [(False, False, 40), (True, False, 22), (False, True, 22), (True, True, 4)])
def test_fixed_first_attempt_population_provider_stop_and_overwrite_refusal(tmp_path, monkeypatch, gpt_error, deep_error, expected):
    protocol = r.deep.load_document(r.HERE / 'protocol.json')
    monkeypatch.setattr(r, 'HERE', tmp_path)
    (tmp_path / 'preflight').mkdir()
    (tmp_path / 'preflight/passed.json').write_text('{}')
    g = {'exit_code': int(gpt_error), 'errors': [], 'tool_items': []}
    d = {'http_status': 401 if deep_error else 200, 'transport_error': None, 'unexpected_tool_calls': False}
    with patch.object(r, 'verify', return_value=protocol), patch.object(r.deep, 'credential', return_value='OFFLINE_FAKE'), \
         patch.object(r.gpt, 'run_case', return_value=g) as gt, patch.object(r.deep, 'call', return_value=d) as dt:
        r.execute(Path('NEVER_READ'))
        assert gt.call_count + dt.call_count == expected
        with pytest.raises(FileExistsError):
            r.execute(Path('NEVER_READ'))
        assert gt.call_count + dt.call_count == expected
    assert r.deep.load_document(tmp_path / 'run.completed.json')['attempted'] == expected
