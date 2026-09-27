"""Read-only integrity, two-ledger coverage, replay and reviewer allowlist checks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODELS = {'gpt-5.6-sol', 'gpt-6-astra', 'deepseek-v4-pro', 'deepseek-flash'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_review(review: dict) -> dict:
    assert review['method_status'] == 'ACCEPTED_A_D026'
    assert review['case_review_status'] == 'AI_PENDING' and review['human_reviews'] == []
    assert review['overall_score'] is None and review['new_model_calls'] == 0
    assert review['previous_review_sha256'] == sha(HERE.parent/'v0.1/review.json')
    expected = {(m, f'lit-{i:03}') for m in MODELS for i in range(1, 11)}
    rows = review['rows']
    assert len(rows) == 40 and {(r['model'], r['mother_case']) for r in rows} == expected
    assert sum(bool(r['assessments']) for r in rows) == 39
    claims = obligations = excerpts = 0
    for row in rows:
        path = ROOT/row['response_path']
        assert sha(path) == row['response_sha256']
        assert sha(ROOT/row['input_path']) == row['input_sha256']
        assert row['human_reviews'] == [] and row['task_pass'] is None
        assert not row['complete_migration_verified']
        assert [o['obligation'] for o in row['completion']] == ['mapping', 'encoding', 'selection', 'certification', 'context']
        obligations += len(row['completion'])
        if not path.read_text().strip():
            assert (row['model'], row['mother_case']) == ('deepseek-flash', 'lit-009')
            assert row['assessments'] == [] and row['excerpts'] == {}
            assert all(o['completion_state'] == 'no_response' and not o['response_pointers'] for o in row['completion'])
            assert sha(ROOT/row['failure_evidence']['metadata_path']) == row['failure_evidence']['metadata_sha256']
            continue
        assert row['review_status'] == 'AI_PENDING'
        assert [a['dimension'] for a in row['assessments']] == list('MECW')
        original = json.loads(path.read_text())
        for pointer, excerpt in row['excerpts'].items():
            value = original
            for part in pointer.lstrip('/').split('/'):
                value = value[part]
            assert value == excerpt
            excerpts += 1
        for claim in row['assessments']:
            assert claim['evidence_state'] in {'supported', 'contradicted', 'unresolved', 'not_addressed', 'not_reviewed', 'not_applicable'}
            assert claim['reason'] and claim['response_pointers'] and not claim['complete_migration_verified']
            assert all(p in row['excerpts'] for p in claim['response_pointers'])
            assert all((HERE/p).is_file() for p in claim['evidence'])
            claims += 1
        for obligation in row['completion']:
            assert obligation['completion_state'] in {'provided', 'partial', 'deferred', 'not_addressed', 'not_applicable'}
            assert obligation['human_reviews'] == [] and obligation['response_pointers']
            assert all(p in row['excerpts'] for p in obligation['response_pointers'])
    assert claims == 156 and obligations == 200
    # Semantic regression sentinels for the agreed separation, not model rankings.
    indexed = {(r['model'], r['mother_case']): r for r in rows}
    for model in ['deepseek-v4-pro', 'deepseek-flash']:
        row = indexed[model, 'lit-002']
        assert row['completion'][2]['completion_state'] == 'provided'
        assert row['assessments'][2]['evidence_state'] == 'contradicted'
    assert indexed['gpt-6-astra', 'lit-002']['completion'][2]['completion_state'] == 'deferred'
    return {'requests': len(rows), 'reviewed_answers': 39, 'claims': claims, 'completion_records': obligations,
            'exact_source_fields': excerpts, 'inherited_answers': sum(r['inherited_v01_claim_review'] for r in rows)}


def check_packet() -> dict:
    packet = HERE/'reviewer_packet'
    manifest = json.loads((packet/'MANIFEST.json').read_text())
    expected = {'GUIDE.md', 'obligations.json', 'blank_reviews.json'} | {f'inputs/lit-{i:03}-C.txt' for i in range(1, 11)}
    assert set(manifest['payload_files']) == expected
    assert {str(p.relative_to(packet)) for p in packet.rglob('*') if p.is_file()} == expected | {'MANIFEST.json'}
    assert all(sha(packet/p) == digest for p, digest in manifest['payload_files'].items())
    for i in range(1, 11):
        name = f'lit-{i:03}-C.txt'
        assert (packet/'inputs'/name).read_bytes() == (ROOT/'pilot/reference_completion/v0.1.1/review_inputs'/name).read_bytes()
    blanks = json.loads((packet/'blank_reviews.json').read_text())
    assert len(blanks) == 10 and all(r['reviewer'] is None and r['review_status'] == 'UNFILLED' for r in blanks)
    for row in blanks:
        assert all(value is None for key, value in row.items() if key not in {'mother_case', 'input_sha256', 'review_status'})
    with tempfile.TemporaryDirectory(prefix='qrefactor-reviewer-') as temp:
        fresh = Path(temp)/'packet'
        subprocess.run([sys.executable, '-B', str(HERE/'build_reviewer_packet.py'), str(fresh)], check=True)
        assert all((fresh/p).read_bytes() == (packet/p).read_bytes() for p in expected | {'MANIFEST.json'})
    return {'payload_files': len(expected), 'human_reviews_filled': 0, 'replay_equal': True,
            'scope': 'Allowlist excludes model outputs/private labels/coordinator verdicts; checklist remains AI authored.'}


def run() -> dict:
    protected = json.loads((HERE/'protected_before.json').read_text())
    assert all((ROOT/p).is_file() and sha(ROOT/p) == digest for p, digest in protected.items())
    review = json.loads((HERE/'review.json').read_text())
    coverage = check_review(review)
    for script, filename in [('build_review.py', 'review.json'), ('check_evidence.py', 'checks.json')]:
        replay = json.loads(subprocess.check_output([sys.executable, '-B', str(HERE/script)], text=True))
        assert replay == json.loads((HERE/filename).read_text()), script
    packet = check_packet()
    links = 0
    docs = list(HERE.rglob('*.md')) + [ROOT/p for p in
            ['PROJECT_STATUS.md', 'NEXT_ACTIONS.md', 'TODO.md', 'DECISIONS.md', 'CHANGELOG.md', 'docs/research_log.md']]
    for path in docs:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            target = target.split('#', 1)[0].strip('<>')
            if not target or re.match(r'^[a-z]+://', target):
                continue
            dest = (path.parent/target).resolve()
            if dest == HERE/'validation.json' and not dest.exists():
                continue
            assert dest.exists(), (path, target)
            links += 1
    return {'status': 'passed', 'coverage': coverage, 'reviewer_packet': packet,
            'protected_files_unchanged': len(protected), 'existing_local_links': links,
            'review_and_new_math_replay_equal': True, 'new_model_calls': 0, 'quantum_runs': 0,
            'known_initial_check_failure': 'Wrong lit-001 source path caused FileNotFoundError; corrected before successful math checks.',
            'limit': 'Integrity and bounded arithmetic evidence, not independent human adjudication or complete migration proof.'}


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))
