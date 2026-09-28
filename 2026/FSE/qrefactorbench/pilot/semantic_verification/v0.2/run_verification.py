"""Run and archive controls for all ten cases; no model or quantum execution."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

from verification import HERE, ROOT, base, evaluate, load_suite
from control_extensions import VARIANTS, submission


def run(output: Path) -> int:
    suite = load_suite()
    output.mkdir(parents=True, exist_ok=False)
    candidates, rows = [], []
    for case in suite['cases']:
        for variant in VARIANTS[case['oracle_kind']]:
            candidate = submission(case, variant)
            candidates.append(candidate)
            start = time.monotonic()
            report = evaluate(case, candidate)
            wanted = 'passed' if variant in ('correct', 'equivalent', 'one_hot', 'one_hot_equivalent') else 'candidate_error'
            rows.append({'case_id': case['case_id'], 'control': variant, 'expected_status': wanted,
                         'matched_expected': report['status'] == wanted,
                         'seconds': time.monotonic() - start, **report})
    code = list(HERE.glob('*.py')) + [HERE / 'contracts.json', ROOT / 'tests/test_semantic_verification_v02.py']
    report = {'protocol': 'scoped-semantic-verification-v0.2', 'created_utc': datetime.now(timezone.utc).isoformat(),
              'population': {'mother_cases': 10, 'input_conditions': 30, 'cases_with_scoped_oracle': len(suite['cases']),
                             'cases_actually_checked': len({r['case_id'] for r in rows}),
                             'test_inputs': sum(len(c['tests']) for c in suite['cases']),
                             'synthetic_controls': len(rows),
                             'correct_controls_passed': sum(r['expected_status'] == 'passed' and r['matched_expected'] for r in rows),
                             'wrong_controls_rejected': sum(r['expected_status'] == 'candidate_error' and r['matched_expected'] for r in rows),
                             'model_calls': 0, 'whole_task_passed': None},
              'source_sha256': {str(p.relative_to(ROOT)): base.digest(p) for p in code},
              'scope': 'Local mathematical/behavior claims, not full migration, gold labels or model performance',
              'results': rows}
    for filename, value in [('controls.json', candidates), ('results.json', report)]:
        with (output / filename).open('x') as out:
            json.dump(value, out, indent=2, ensure_ascii=False, allow_nan=False)
            out.write('\n')
    print(json.dumps(report['population']))
    return 0 if all(r['matched_expected'] for r in rows) else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    raise SystemExit(run(parser.parse_args().output))
