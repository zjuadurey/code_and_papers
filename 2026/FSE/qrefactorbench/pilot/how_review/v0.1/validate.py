"""Offline provenance/coverage/replay checks; not scientific adjudication."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict:
    before = json.loads((HERE / 'protected_before.json').read_text())
    changed = [p for p, value in before.items() if not (ROOT/p).is_file() or sha(ROOT/p) != value]
    assert not changed, changed
    review = json.loads((HERE/'review.json').read_text())
    assert review['human_reviews'] == [] and review['model_calls'] == 0
    rows = review['rows']
    assert len(rows) == 40
    assert len({(r['model'], r['mother_case']) for r in rows}) == 40
    assert sum(r['selected_for_trial_review'] for r in rows) == 20
    assert sum(bool(r['assessments']) for r in rows) == 19
    assert sum(r['response_status'] == 'budget_exhausted_no_final' for r in rows) == 1
    excerpts = 0
    for row in rows:
        path = ROOT/row['response_path']
        assert sha(path) == row['response_sha256']
        assert sha(ROOT/row['input_path']) == row['input_sha256']
        assert row['human_reviews'] == [] and row['task_pass'] is None
        if row['response_status'] == 'budget_exhausted_no_final':
            assert not path.read_text().strip() and row['assessments'] == [] and row['excerpts'] == {}
            assert sha(ROOT/row['failure_evidence']['metadata_path']) == row['failure_evidence']['metadata_sha256']
            continue
        original = json.loads(path.read_text())
        for pointer, excerpt in row['excerpts'].items():
            value = original
            for part in pointer.lstrip('/').split('/'):
                value = value[part]
            assert value == excerpt, (path, pointer)
            excerpts += 1
        if not row['selected_for_trial_review']:
            assert row['review_status'] == 'NOT_REVIEWED' and row['assessments'] == []
        else:
            assert row['review_status'] == 'AI_PENDING'
            assert [r['dimension'] for r in row['assessments']] == list('MECW')
            for finding in row['assessments']:
                assert finding['evidence_state'] in {'supported', 'contradicted', 'unresolved', 'not_applicable'}
                assert not finding['complete_migration_verified']
                assert all(p in row['excerpts'] for p in finding['response_pointers'])
                assert all((HERE/p).is_file() for p in finding['evidence'])
    for script, target in [('build_review.py', 'review.json'), ('check_evidence.py', 'checks.json')]:
        replay = json.loads(subprocess.check_output([sys.executable, '-B', str(HERE/script)], text=True))
        assert replay == json.loads((HERE/target).read_text()), script
    docs = list(HERE.glob('*.md')) + [ROOT/p for p in
        ['PROJECT_STATUS.md', 'NEXT_ACTIONS.md', 'TODO.md', 'DECISIONS.md', 'CHANGELOG.md', 'docs/research_log.md']]
    links = 0
    for path in docs:
        for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            target = raw.split('#', 1)[0].strip('<>')
            if not target or re.match(r'^[a-z]+://', target):
                continue
            resolved = (path.parent/unquote(target)).resolve()
            if resolved == HERE/'validation.json' and not resolved.exists():
                continue
            assert resolved.exists(), (str(path), target)
            links += 1
    return {'status': 'passed', 'protected_files_unchanged': len(before), 'requests_in_inventory': 40,
            'trial_selected_requests': 20, 'trial_reviewed_answers': 19, 'budget_failures_preserved': 1,
            'answers_not_content_reviewed': 20, 'claim_records': 76, 'exact_source_excerpts': excerpts,
            'review_and_math_replay_equal': True, 'existing_local_document_links': links,
            'link_scope': 'file existence only, not fragment anchors or external URLs',
            'human_adjudications': 0, 'new_model_calls': 0, 'quantum_runs': 0,
            'scope_limit': 'No overall scores, whole-program proof or independent review.'}


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))
