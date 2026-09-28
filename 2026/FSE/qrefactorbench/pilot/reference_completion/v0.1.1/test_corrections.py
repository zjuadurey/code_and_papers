"""Bound the patch: behavior regressions live beside cases; no scientific relabeling."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import build_package as build
from qrefactorbench.schema import schema_errors

HERE = Path(__file__).resolve().parent
OLD = HERE.with_name('v0.1')
ROOT = HERE.parents[2]


def test_original_artifacts_unchanged():
    for name, expected in json.loads((HERE / 'protected_before.json').read_text()).items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name


def test_contracts_labels_coordinates_and_examples_preserved():
    for folder in (HERE / 'cases').iterdir():
        previous = OLD / 'cases' / folder.name
        for name in ('public_task.json', 'core_task.json', 'example_request.json', 'example_report.json'):
            assert (folder / name).read_bytes() == (previous / name).read_bytes()
        current = json.loads((folder / 'case.json').read_text())
        original = json.loads((previous / 'case.json').read_text())
        assert not schema_errors(current, 'case')
        if folder.name in ('lit-005', 'lit-007', 'lit-009'):
            assert current['version'] == '0.1.1'
            current['version'] = original['version']
        assert current == original
        for region in current['candidate_regions']:
            tree = ast.parse((folder / region['file']).read_text())
            node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == region['function'])
            assert (node.lineno, node.end_lineno) == (region['start_line'], region['end_line'])


def test_only_approved_program_edits_and_no_kernel_algorithm_change():
    expected = {
        'lit-005': ('[features[i] for i, v in locked.items() if current[i] != v]',
                    '[name for i, name in enumerate(features) if i in locked and current[i] != locked[i]]'),
        'lit-009': ('[a - b for a, b in zip(x, current)]',
                    '[finite(a - b) for a, b in zip(x, current)]'),
    }
    for folder in (HERE / 'cases').iterdir():
        for name in ('program.py', 'common.py', 'kernel.py'):
            before = (OLD / 'cases' / folder.name / name).read_text()
            after = (folder / name).read_text()
            if name == 'program.py' and folder.name in expected:
                old, new = expected[folder.name]
                assert before.count(old) == 1 and after == before.replace(old, new)
            elif name == 'kernel.py' and folder.name == 'lit-007':
                a, b = ast.parse(before), ast.parse(after)
                assert ast.dump(ast.Module(body=a.body[1:], type_ignores=[])) == ast.dump(ast.Module(body=b.body[1:], type_ignores=[]))
            else:
                assert before == after


def test_no_case_specific_algorithm_cue_and_license_retained():
    case = HERE / 'cases/lit-007'
    notice = (case / 'NOTICE.txt').read_text()
    old_notice = (OLD / 'cases/lit-007/NOTICE.txt').read_text()
    assert notice.split('Source license text:\n', 1)[1] == old_notice.split('Source license text:\n', 1)[1]
    assert 'Copyright' in notice or 'copyright 2026 Infleqtion' in notice
    assert 'SupermarQ' in notice and 'https://github.com/Infleqtion/client-superstaq' in notice
    for condition in 'ABC':
        message = (HERE / f'review_inputs/lit-007-{condition}.txt').read_text()
        # The shared task/menu still names QAOA for every case; only case-specific input is audited.
        public = message.split('\nPUBLIC TASK\n', 1)[1].split('\nSHARED DRAFT CONTRACTS\n', 1)[0]
        for cue in ('qaoa', '_gen_sk_hamiltonian', '_get_opt_angles', '_get_energy_for_bitstring'):
            assert cue not in public.lower()
        assert 'FILE case.json' not in message and 'ADAPTATION.md' not in message
    assert 'QAOAVanillaProxy' in (case / 'ADAPTATION.md').read_text()
    assert 'qaoa_vanilla_proxy.py' in json.loads((case / 'case.json').read_text())['source_url']


def test_thirty_packets_with_exact_seven_changed_and_cue_only_pairs():
    manifest = json.loads((HERE / 'review_inputs/manifest.json').read_text())
    old_manifest = json.loads((OLD / 'review_inputs/manifest.json').read_text())
    assert manifest['model_calls'] == 0 and manifest['mother_cases'] == 10
    assert manifest['task_sha256'] == old_manifest['task_sha256']
    assert len(manifest['conditions']) == 30
    changed = set()
    for row in manifest['conditions']:
        content = (HERE / 'review_inputs' / row['file']).read_bytes()
        assert hashlib.sha256(content).hexdigest() == row['sha256']
        old = (OLD / 'review_inputs' / row['file']).read_bytes()
        if content != old:
            changed.add(row['file'])
        assert content.split(b'\nSHARED DRAFT CONTRACTS\n', 1)[1] == old.split(b'\nSHARED DRAFT CONTRACTS\n', 1)[1]
    assert changed == {f'lit-{n:03}-{c}.txt' for n, conditions in ((5, 'BC'), (7, 'ABC'), (9, 'BC')) for c in conditions}
    for n in range(1, 11):
        a, b, c = [(HERE / f'review_inputs/lit-{n:03}-{condition}.txt').read_text() for condition in 'ABC']
        prefix, hint = b.split('\nLOCATION CUE\n')
        assert prefix == c
        assert set(json.loads(hint)) == {'file', 'start_line', 'end_line'}
        assert '\nLOCATION CUE\n' not in a and '\nLOCATION CUE\n' not in c


def test_regeneration_and_overwrite_refusal(tmp_path):
    output = tmp_path / 'packets'
    build.prepare(output)
    assert {p.name for p in output.iterdir()} == {p.name for p in (HERE / 'review_inputs').iterdir()}
    for path in output.iterdir():
        assert path.read_bytes() == (HERE / 'review_inputs' / path.name).read_bytes()
    with pytest.raises(FileExistsError):
        build.prepare(output)


@pytest.mark.parametrize('case_id', [f'lit-{n:03}' for n in range(5, 11)])
def test_examples_still_match_complete_reports(case_id):
    folder = HERE / 'cases' / case_id
    result = subprocess.run([sys.executable, '-B', str(folder / 'program.py')],
                            input=(folder / 'example_request.json').read_text(), text=True,
                            capture_output=True, check=True)
    assert json.loads(result.stdout) == json.loads((folder / 'example_report.json').read_text())
