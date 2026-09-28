"""Offline scoped-claim checks, not a parser/scorer of free-form model plans.

Input is private reviewer transcription (JSON data only). The agent's existing
Phase-1 submission format is unchanged. No exec/eval/import of candidate code.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from qrefactorbench.loader import DataError, load_document, safe_path
from oracles import assignments, expected

MAX_VARIABLES = 8  # Reviewer-check budget, NOT a new benchmark input restriction.
MAX_TERMS = 256


class InvalidClaim(ValueError):
    pass


class CheckBudget(ValueError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_suite() -> dict[str, Any]:
    suite = load_document(HERE / 'contracts.json')
    for name, sha in suite['source_sha256'].items():
        if digest(safe_path(ROOT, name)) != sha:
            raise DataError(f'Pinned source changed: {name}')
    for case in suite['cases']:
        for test in case['tests']:
            if expected(case['oracle_kind'], test['input']) != test['expected']:
                raise DataError(f'Stored expectation disagrees with definition: {test["id"]}')
    return suite


def rational(value: Any) -> Fraction:
    if type(value) is int:
        if value.bit_length() > 256:
            raise CheckBudget('Coefficient exceeds exact arithmetic budget')
        return Fraction(value)
    if isinstance(value, str) and len(value) <= 160:
        parts = value.split('/')
        if len(parts) in (1, 2) and all(p.lstrip('-').isdigit() for p in parts):
            try:
                return Fraction(value)
            except (ValueError, ZeroDivisionError):
                pass
    raise InvalidClaim('Coefficients must be exact integer or rational strings; no float/NaN')


def decoder(claim: dict[str, Any], n: int):
    """x_i = y[permutation[i]] xor complement[i]; all variable bijections allowed."""
    d = claim.get('decode', {})
    if not isinstance(d, dict):
        raise InvalidClaim('Decoder must be an object')
    perm, flip = d.get('permutation'), d.get('complement')
    if (not isinstance(perm, list) or any(type(i) is not int for i in perm)
            or sorted(perm) != list(range(n)) or not isinstance(flip, list)
            or len(flip) != n or any(type(v) is not int or v not in (0, 1) for v in flip)):
        raise InvalidClaim('Decoder must be a binary bijection with explicit variable correspondence')
    return lambda bits: [bits[perm[i]] ^ flip[i] for i in range(n)]


def polynomial(claim: dict[str, Any], n: int):
    terms = claim.get('terms')
    if not isinstance(terms, list):
        raise InvalidClaim('Missing polynomial terms')
    if len(terms) > MAX_TERMS:
        raise CheckBudget('Too many polynomial terms for review budget')
    parsed = []
    for term in terms:
        if not isinstance(term, dict) or set(term) != {'coefficient', 'variables'}:
            raise InvalidClaim('A term needs coefficient and variables')
        indices = term['variables']
        if (not isinstance(indices, list) or len(indices) > 2
                or any(type(i) is not int or not 0 <= i < n for i in indices)):
            raise InvalidClaim('Only binary quadratic terms in declared variables are supported')
        parsed.append((rational(term['coefficient']), indices))
    if claim.get('sense') not in ('min', 'max'):
        raise InvalidClaim('Optimization sense must be explicit')
    return lambda bits: sum((coefficient * all(bits[i] for i in indices)
                             for coefficient, indices in parsed), Fraction(0))


def check_claim(kind: str, problem: dict[str, Any], claim: dict[str, Any]) -> list[dict[str, Any]]:
    """Return semantic differences, considering EVERY ground state, not one lucky tie."""
    if kind != 'receipts' and problem['n'] > MAX_VARIABLES:
        raise CheckBudget('Finite enumeration exceeds reviewer budget; no candidate error inferred')
    truth = expected(kind, problem)
    failures = []
    if kind == 'receipts':
        actual = claim.get('report')
        if not isinstance(actual, dict):
            raise InvalidClaim('Missing report object')
        # JSON type equality: True must not compare equal to integer 1.
        if json.dumps(actual, sort_keys=True) != json.dumps(truth, sort_keys=True):
            failures.append({'obligation': 'full_ordered_report', 'expected': truth, 'actual': actual})
        return failures
    n = problem['n']
    decode = decoder(claim, n)
    bits = assignments(n)
    if kind in ('cover', 'clique'):
        energy = polynomial(claim, n)
        values = [(energy(b), b) for b in bits]
        optimum = (min if claim['sense'] == 'min' else max)(e for e, _ in values)
        for e, b in values:
            if e != optimum:
                continue
            selected = [i for i, bit in enumerate(decode(b)) if bit]
            edges = {tuple(edge) for edge in problem['edges']}
            feasible = (all(u in selected or v in selected for u, v in edges) if kind == 'cover'
                        else all((u, v) in edges for u in selected for v in selected if u < v))
            obligation = ('feasibility' if not feasible else
                          'optimal_cardinality' if len(selected) != len(truth) else 'canonical_selection')
            if selected != truth:
                failures.append({'obligation': obligation, 'expected': truth, 'actual': selected,
                                 'encoded_bits': list(b), 'optimal_energy': str(optimum)})
    elif kind == 'predicate':
        table = claim.get('marked')
        if (not isinstance(table, list) or len(table) != len(bits)
                or any(type(v) is not bool for v in table)):
            raise InvalidClaim('Marked table must contain one Boolean per canonical encoded assignment')
        for b, marked in zip(bits, table):
            wanted = decode(b) in truth['marked']
            if marked != wanted:
                failures.append({'obligation': 'predicate_equivalence', 'encoded_bits': list(b),
                                 'decoded_bits': decode(b), 'expected': wanted, 'actual': marked})
        # Selection policy is an independent obligation; absent means not checked.
        if 'selected' in claim:
            chosen = claim['selected']
            if chosen is not None and (not isinstance(chosen, list) or len(chosen) != n
                                      or any(type(v) is not int or v not in (0, 1) for v in chosen)):
                raise InvalidClaim('selected must be encoded bits or null')
            actual = None if chosen is None else decode(chosen)
            if actual != truth['first']:
                failures.append({'obligation': 'canonical_selection_or_absence',
                                 'expected': truth['first'], 'actual': actual})
    else:
        raise InvalidClaim('Unsupported representation; requires review')
    return failures


def result(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {'status': status, 'reason': reason,
            'scoped_semantic_pass': True if status == 'passed' else False if status == 'candidate_error' else None,
            'task_pass': None, 'migration_execution_success': None, 'practical_advantage': None, **extra}


def check_provenance(submission: dict[str, Any], case: dict[str, Any]) -> None:
    source = submission.get('provenance')
    if not isinstance(source, dict):
        raise InvalidClaim('Missing reviewer-transcription provenance')
    if source.get('kind') == 'synthetic_control':
        if source.get('is_model_result') is not False:
            raise InvalidClaim('Controls must explicitly disclaim model-result provenance')
        return
    if source.get('kind') != 'reviewer_transcription':
        raise InvalidClaim('Unknown claim provenance')
    for key in ('response_path', 'response_sha256', 'pointer', 'quote', 'interpretation', 'parameters_source'):
        if not isinstance(source.get(key), str) or not source[key]:
            raise InvalidClaim(f'Missing source binding: {key}')
    path = safe_path(ROOT, source['response_path'])
    if not path.is_relative_to(ROOT / 'pilot/model_comparison') or path.name != 'response.txt':
        raise InvalidClaim('Transcription sources must be archived model response.txt files')
    if digest(path) != source['response_sha256']:
        raise DataError('Response hash changed: transcription not usable')
    node = load_document(path)
    if not isinstance(node, dict) or node.get('case_id') != case['prediction_case_id']:
        raise DataError('Transcription response is bound to a different public case')
    for part in source['pointer'].strip('/').split('/'):
        node = node[part]
    if not isinstance(node, str) or source['quote'] not in node:
        raise DataError('Quote does not match pinned response pointer')
    # Byte binding does NOT prove that the reviewer formalization is faithful.


def evaluate(case: dict[str, Any], submission: Any) -> dict[str, Any]:
    """Score fixed test obligations, never candidate-supplied expected values or test selection."""
    if submission is None:
        return result('not_run', 'No transcribed claim submitted', tests=[])
    if not isinstance(submission, dict):
        return result('invalid_format', 'Reviewer claim must be an object', tests=[])
    if submission.get('case_id') != case['case_id']:
        return result('invalid_format', 'Wrong case ID', tests=[])
    if submission.get('delivery_status', 'delivered') != 'delivered':
        state = submission['delivery_status']
        allowed = {'candidate_budget_exceeded', 'infrastructure_error', 'not_run'}
        if state not in allowed:
            return result('invalid_format', 'Unknown delivery status', tests=[])
        return result(state, submission.get('diagnostic', 'Recorded delivery outcome'), tests=[])
    if not case['tests']:
        return result('insufficient_evidence', 'No audited executable claim oracle for this case', tests=[])
    if submission.get('claim_scope') != case['claim_scope']:
        return result('insufficient_evidence', 'Claim scope missing/different; do not reinterpret a core-only or fallback plan as a direct canonical objective', tests=[])
    try:
        check_provenance(submission, case)
    except InvalidClaim as exc:
        return result('insufficient_evidence', str(exc), tests=[])
    except Exception as exc:
        return result('infrastructure_error', f'Provenance verification: {type(exc).__name__}: {exc}', tests=[])
    claims = submission.get('claims')
    if not isinstance(claims, dict):
        return result('insufficient_evidence', 'No machine-checkable claims; prose requires review', tests=[])
    extra = set(claims) - {t['id'] for t in case['tests']}
    if extra:
        return result('invalid_format', f'Unknown test IDs: {sorted(extra)}', tests=[])
    rows = []
    for test in case['tests']:
        claim = claims.get(test['id'])
        if claim is None:
            rows.append(result('insufficient_evidence', 'Claim not transcribed for this input', test_id=test['id']))
            continue
        try:
            if not isinstance(claim, dict):
                raise InvalidClaim('Claim must be an object')
            if claim.get('kind') != case['oracle_kind']:
                rows.append(result('insufficient_evidence', 'Alternative representation needs review', test_id=test['id']))
                continue
            failures = check_claim(case['oracle_kind'], test['input'], claim)
            partial = case['oracle_kind'] == 'predicate' and 'selected' not in claim
            status = 'candidate_error' if failures else 'insufficient_evidence' if partial else 'passed'
            rows.append(result(status, 'Finite definition comparison; selection missing' if partial else
                               'Finite definition comparison', test_id=test['id'], failures=failures,
                               predicate_pass=(not any(f['obligation'] == 'predicate_equivalence' for f in failures))
                               if case['oracle_kind'] == 'predicate' else None))
        except CheckBudget as exc:
            rows.append(result('review_budget_exceeded', str(exc), test_id=test['id']))
        except InvalidClaim as exc:
            rows.append(result('invalid_format', str(exc), test_id=test['id']))
        except Exception as exc:
            rows.append(result('infrastructure_error', f'{type(exc).__name__}: {exc}', test_id=test['id']))
    counts = Counter(row['status'] for row in rows)
    priority = ['candidate_error', 'infrastructure_error', 'invalid_format',
                'review_budget_exceeded', 'insufficient_evidence', 'passed']
    status = next(s for s in priority if counts[s])
    return result(status, 'Only the declared finite claim scope; no whole-plan verdict',
                  format_valid=False if counts['invalid_format'] else
                  True if all(r['status'] in ('passed', 'candidate_error') for r in rows) else None, tests=rows,
                  test_counts={'total': len(rows), 'executed': sum(r['status'] in ('passed', 'candidate_error') for r in rows),
                               **dict(counts)})


def aggregate(suite: dict[str, Any], submissions: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(submissions, list) or any(not isinstance(row, dict) or not isinstance(row.get('case_id'), str) for row in submissions):
        raise DataError('Expected an array of case-bound reviewer claims')
    ids = [row['case_id'] for row in submissions]
    known = {c['case_id'] for c in suite['cases']}
    if len(set(ids)) != len(ids) or set(ids) - known:
        raise DataError('Duplicate/unknown case submissions; no silent population changes')
    by_id = {row['case_id']: row for row in submissions}
    rows = [{'case_id': case['case_id'], **evaluate(case, by_id.get(case['case_id']))} for case in suite['cases']]
    return {'protocol': 'scoped-semantic-verification-v0.1', 'task_pass': None,
            'population': {'mother_cases': len(rows), 'input_conditions': 30,
                           'cases_with_scoped_oracle': sum(bool(c['tests']) for c in suite['cases']),
                           'submitted_cases': len(submissions),
                           'cases_with_executed_checks': sum(any(t['status'] in ('passed', 'candidate_error') for t in r['tests']) for r in rows),
                           'fully_executed_cases': sum(bool(r['tests']) and all(t['status'] in ('passed', 'candidate_error') for t in r['tests']) for r in rows),
                           'scoped_passed_cases': sum(r['status'] == 'passed' for r in rows)},
            'status_counts': dict(Counter(r['status'] for r in rows)), 'results': rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--claims', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = aggregate(load_suite(), load_document(args.claims))
        report['claims_sha256'] = digest(args.claims)
        report['contracts_sha256'] = digest(HERE / 'contracts.json')
        with args.output.open('x') as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write('\n')
    except (OSError, DataError, KeyError, TypeError) as exc:
        print(f'Evaluation unavailable: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
