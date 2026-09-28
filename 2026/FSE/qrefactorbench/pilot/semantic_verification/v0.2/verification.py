"""Versioned extension of the unchanged v0.1 data-only verifier."""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.with_name('v0.1')


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Only trusted repository modules; no candidate imports. Distinct names avoid
# changing the v0.1 evaluator used by its regression tests in the same process.
sys.path.insert(0, str(PREVIOUS))
try:
    base = load('verification_v02_base', PREVIOUS / 'evaluate.py')
    old_controls = load('verification_v02_old_controls', PREVIOUS / 'controls.py')
finally:
    sys.path.remove(str(PREVIOUS))
extension = load('verification_v02_oracles', HERE / 'oracle_extensions.py')
old_expected, old_check, old_evaluate = base.expected, base.check_claim, base.evaluate
NEW_KINDS = {'maxcut', 'signed', 'knapsack', 'coloring', 'linear', 'iteration'}


def expected(kind: str, p: dict[str, Any]) -> Any:
    return extension.expected(kind, p) if kind in NEW_KINDS else old_expected(kind, p)


def numeric_equal(actual: Any, wanted: Any) -> bool:
    """Exact finite fixture comparison, explicitly no newly invented tolerance."""
    if isinstance(wanted, dict):
        return isinstance(actual, dict) and actual.keys() == wanted.keys() and all(numeric_equal(actual[k], v) for k, v in wanted.items())
    if isinstance(wanted, list):
        return isinstance(actual, list) and len(actual) == len(wanted) and all(numeric_equal(a, b) for a, b in zip(actual, wanted))
    if type(wanted) in (int, float):
        return type(actual) in (int, float) and actual == wanted
    return type(actual) is type(wanted) and actual == wanted


def check_claim(kind: str, p: dict[str, Any], claim: dict[str, Any]) -> list[dict[str, Any]]:
    if kind not in NEW_KINDS:
        return old_check(kind, p, claim)
    if kind in ('linear', 'iteration'):
        actual, truth = claim.get('result'), expected(kind, p)
        if not isinstance(actual, dict):
            raise base.InvalidClaim('A numerical behavior claim needs a result object')
        failures = []
        for key, value in truth.items():
            if not numeric_equal(actual.get(key), value):
                failures.append({'obligation': key, 'expected': value, 'actual': actual.get(key)})
        if set(actual) - set(truth):
            failures.append({'obligation': 'result_fields', 'expected': sorted(truth), 'actual': sorted(actual)})
        return failures
    count = claim.get('variable_count', p['n'])
    if type(count) is not int or count < 0:
        raise base.InvalidClaim('Invalid variable count')
    if count > base.MAX_VARIABLES:
        raise base.CheckBudget('Encoded variables exceed finite reviewer budget')
    decode = base.decoder(claim, count)
    if kind == 'coloring':
        return coloring(p, claim, count, decode)
    if count < p['n'] or (kind != 'knapsack' and count != p['n']):
        raise base.InvalidClaim('Logical/auxiliary variable correspondence has wrong size')
    energy = base.polynomial(claim, count)
    truth = expected(kind, p)
    values = [(energy(bits), bits) for bits in base.assignments(count)]
    optimum = (min if claim['sense'] == 'min' else max)(e for e, _ in values)
    failures = []
    for e, bits in values:
        if e != optimum:
            continue
        chosen = [i for i, v in enumerate(decode(bits)[:p['n']]) if v]
        if chosen != truth:
            obligation = 'objective_or_canonical_decode'
            if kind == 'knapsack' and sum(p['items'][i]['weight'] for i in chosen) > p['capacity']:
                obligation = 'capacity'
            failures.append({'obligation': obligation, 'expected': truth, 'actual': chosen,
                             'encoded_bits': list(bits), 'optimal_energy': str(optimum)})
    return failures


def coloring(p: dict[str, Any], claim: dict[str, Any], count: int, decode) -> list[dict[str, Any]]:
    rep, n, k = claim.get('representation'), p['n'], p['colors']
    truth, failures = expected('coloring', p), []
    if rep == 'binary_predicate':
        width = max(1, (k - 1).bit_length())
        if count != n * width:
            raise base.InvalidClaim('Binary color registers have the wrong width')
        table = claim.get('marked')
        if not isinstance(table, list) or len(table) != 2 ** count or any(type(v) is not bool for v in table):
            raise base.InvalidClaim('Expected complete Boolean marking table')
        for bits, marked in zip(base.assignments(count), table):
            logical = decode(bits)
            colors = [sum(logical[i * width + j] * 2 ** j for j in range(width)) for i in range(n)]
            wanted = colors in truth['solutions']
            if wanted != marked:
                failures.append({'obligation': 'color_predicate', 'encoded_bits': list(bits),
                                 'decoded_colors': colors, 'expected': wanted, 'actual': marked})
    elif rep == 'one_hot_qubo':
        if count != n * k:
            raise base.InvalidClaim('One-hot registers have wrong size')
        energy = base.polynomial(claim, count)
        level = base.rational(claim.get('feasible_energy', 0))
        for bits in base.assignments(count):
            logical = decode(bits)
            valid = all(sum(logical[i * k:(i + 1) * k]) == 1 for i in range(n))
            colors = [next((j for j in range(k) if logical[i * k + j]), -1) for i in range(n)]
            wanted = valid and colors in truth['solutions']
            value = energy(bits)
            actual = value == level
            if wanted != actual:
                failures.append({'obligation': 'zero_energy_iff_valid_coloring', 'encoded_bits': list(bits),
                                 'expected': wanted, 'actual': actual})
            if (value < level if claim['sense'] == 'min' else value > level):
                failures.append({'obligation': 'feasible_energy_is_bound', 'encoded_bits': list(bits),
                                 'expected': f'{claim["sense"]} bound {level}', 'actual': str(value)})
    else:
        raise base.InvalidClaim('Unrecognized coloring representation')
    if not numeric_equal(claim.get('selected'), truth['first']):
        failures.append({'obligation': 'lex_first_or_absence', 'expected': truth['first'], 'actual': claim.get('selected')})
    return failures


def evaluate(case: dict[str, Any], submission: Any) -> dict[str, Any]:
    if isinstance(submission, dict) and isinstance(submission.get('claims'), dict) and case['oracle_kind'] == 'coloring':
        submission = deepcopy(submission)
        for claim in submission['claims'].values():
            if isinstance(claim, dict) and ('selected' not in claim or claim.get('representation') not in ('binary_predicate', 'one_hot_qubo')):
                claim['kind'] = 'unreviewed_or_incomplete_coloring_representation'
    return old_evaluate(case, submission)


# Extend only this newly loaded module instance; v0.1 source/results remain intact.
base.expected, base.check_claim, base.evaluate = expected, check_claim, evaluate


def load_suite() -> dict[str, Any]:
    suite = base.load_document(HERE / 'contracts.json')
    for path, sha in suite['source_sha256'].items():
        if base.digest(base.safe_path(ROOT, path)) != sha:
            raise base.DataError(f'Pinned source changed: {path}')
    for case in suite['cases']:
        for test in case['tests']:
            if expected(case['oracle_kind'], test['input']) != test['expected']:
                raise base.DataError(f'Invalid saved expectation: {case["case_id"]}/{test["id"]}')
    return suite


def aggregate(suite: dict[str, Any], submissions: list[dict[str, Any]]) -> dict[str, Any]:
    report = base.aggregate(suite, submissions)
    report['protocol'] = 'scoped-semantic-verification-v0.2'
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--claims', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = aggregate(load_suite(), base.load_document(args.claims))
        report.update(claims_sha256=base.digest(args.claims), contracts_sha256=base.digest(HERE / 'contracts.json'))
        with args.output.open('x') as out:
            json.dump(report, out, ensure_ascii=False, indent=2, allow_nan=False)
            out.write('\n')
    except (OSError, base.DataError, KeyError, TypeError) as exc:
        print(f'Evaluation unavailable: {exc}', file=sys.stderr)
        raise SystemExit(2)
