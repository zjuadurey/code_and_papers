"""Source identity, unchanged scientific fields and blind-condition export checks."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pytest
import build_package as build
from qrefactorbench.schema import schema_errors

HERE=Path(__file__).resolve().parent


def test_pinned_source_integrity_and_actual_license_files():
    records=json.loads((HERE/'sources/manifest.json').read_text())
    assert len(records)==22
    for row in records:
        assert hashlib.sha256((HERE/'sources'/row['file']).read_bytes()).hexdigest()==row['sha256']
    assert 'MIT License' in (HERE/'sources/quanplus.LICENSE').read_text()
    assert 'JawadKotaichh' in next(r['url'] for r in records if r['file']=='quanplus_qiskit.jsonl')


def test_source_problem_specs_not_assumed_reference_answers():
    q=[json.loads(line) for line in (HERE/'sources/quanbench.jsonl').read_text().splitlines()]
    plus=[json.loads(line) for line in (HERE/'sources/quanplus_qiskit.jsonl').read_text().splitlines()]
    sat=next(r for r in q if r['task_id']=='03');other=next(r for r in plus if r['task_id']=='03')
    expression='(x1 | x2 | x3)&(~x1 | x2 | x3)&(~x1 | ~x2 | ~x3)&(~x1 | ~x2 | x3)&(x1 | x2 | ~x3)&(~x1 | x2 | ~x3)'
    assert expression in sat['canonical_solution']
    assert '3-CNF' in other['complete_prompt'] and '((_not(x1)) | (x2) | (_not(x3)))' in other['complete_prompt']
    bag=next(r for r in q if r['task_id']=='05')
    assert 'items_value=[3, 3, 1, 1, 5]' in bag['complete_prompt']
    assert '"1001"' in bag['test']
    tree=ast.parse(bag['canonical_solution'])
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='qaoa_knapsack')
    assert not any(isinstance(n,ast.Return) for n in fn.body)
    # Source discrepancy is retained, not copied into our classical expected mask.
    actual=json.loads((HERE/'cases/lit-006/example_report.json').read_text())
    assert actual['windows'][0]['proposal']['ids']==['item0','item4']


def test_six_schema_valid_draft_records_and_bounded_nominations():
    science=['structural_eligibility','practical_suitability','benchmark_supported','computational_intent','migration_family','expected_decision','reference_plan']
    for path in (HERE/'cases').glob('*/case.json'):
        case=json.loads(path.read_text());assert not schema_errors(case,'case')
        assert case['annotation_status']=='DRAFT' and all(case[k] is None for k in science)
        for region in case['candidate_regions']:
            tree=ast.parse((path.parent/region['file']).read_text())
            fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==region['function'])
            assert (fn.lineno,fn.end_lineno)==(region['start_line'],region['end_line'])
        assert (path.parent/'common.py').read_bytes()==(HERE/'common.py').read_bytes()


def test_thirty_messages_ten_groups_only_location_differs():
    manifest=json.loads((HERE/'review_inputs/manifest.json').read_text())
    assert manifest['mother_cases']==10 and manifest['model_calls']==0
    assert len(manifest['conditions'])==30
    for number in range(1,11):
        case=f'lit-{number:03}';a=(HERE/'review_inputs'/f'{case}-A.txt').read_text()
        b=(HERE/'review_inputs'/f'{case}-B.txt').read_text();c=(HERE/'review_inputs'/f'{case}-C.txt').read_text()
        prefix,hint=b.split('\nLOCATION CUE\n');assert prefix==c
        assert set(json.loads(hint))=={'file','start_line','end_line'}
        assert '\nLOCATION CUE\n' not in a and '\nLOCATION CUE\n' not in c
        for msg in (a,b,c):
            public=json.JSONDecoder().raw_decode(msg.split('\nPUBLIC TASK\n',1)[1])[0]
            assert set(public)=={'case_id','title','software_contract','input_domain','execution_assumptions'}
            for forbidden in ('FILE case.json','FILE test_program.py','ADAPTATION.md','annotation_assist','DRAFT AI construction proposal','METHOD_RESULTS','example_report.json'):
                assert forbidden not in msg
            assert 'FILE NOTICE.txt' in msg


def test_regeneration_and_overwrite_refusal(tmp_path):
    output=tmp_path/'review';build.prepare(output)
    existing=HERE/'review_inputs'
    assert {p.name for p in output.iterdir()}=={p.name for p in existing.iterdir()}
    assert all(p.read_bytes()==(existing/p.name).read_bytes() for p in output.iterdir())
    with pytest.raises(FileExistsError):build.prepare(output)


def test_standalone_classical_examples_match_saved_reports():
    for folder in (HERE/'cases').iterdir():
        r=subprocess.run([sys.executable,'-B',str(folder/'program.py')],input=(folder/'example_request.json').read_text(),text=True,capture_output=True,check=True)
        assert json.loads(r.stdout)==json.loads((folder/'example_report.json').read_text())
