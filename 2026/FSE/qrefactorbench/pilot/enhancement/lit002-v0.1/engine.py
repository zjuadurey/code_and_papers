"""Data-only QUBO templates and exact feedback; never executes model code."""
from __future__ import annotations

import ast
from collections import defaultdict
from fractions import Fraction
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'pilot/semantic_verification/v0.1'
sys.path.insert(0, str(OLD))
spec = importlib.util.spec_from_file_location('lit002_exact_base', OLD / 'evaluate.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


class InvalidTemplate(ValueError):
    pass


class TemplateBudget(ValueError):
    pass


def syntax(source: str, names: set[str]) -> ast.AST:
    if not isinstance(source, str):
        raise InvalidTemplate('Expressions must be strings')
    if len(source) > 160:
        raise TemplateBudget('Expression exceeds 160 characters')
    try:
        node = ast.parse(source, mode='eval')
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise InvalidTemplate('Invalid arithmetic expression') from exc
    if len(list(ast.walk(node))) > 64:
        raise TemplateBudget('Expression exceeds 64 AST nodes')
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name,
               ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.UAdd, ast.USub)
    for item in ast.walk(node):
        if not isinstance(item, allowed):
            raise InvalidTemplate('Only integer arithmetic + - * / ** is supported')
        if isinstance(item, ast.Constant) and type(item.value) is not int:
            raise InvalidTemplate('Only integer literals are supported')
        if isinstance(item, ast.Name) and item.id not in names:
            raise InvalidTemplate('Name not available in this summation scope: ' + item.id)
    return node.body


def arithmetic(node: ast.AST, env: dict[str, int]) -> Fraction:
    if isinstance(node, ast.Constant):
        result = Fraction(node.value)
    elif isinstance(node, ast.Name):
        result = Fraction(env[node.id])
    elif isinstance(node, ast.UnaryOp):
        result = arithmetic(node.operand, env)
        if isinstance(node.op, ast.USub):
            result = -result
    else:
        a, b = arithmetic(node.left, env), arithmetic(node.right, env)
        if isinstance(node.op, ast.Add):
            result = a + b
        elif isinstance(node.op, ast.Sub):
            result = a - b
        elif isinstance(node.op, ast.Mult):
            result = a * b
        elif isinstance(node.op, ast.Div):
            if b == 0:
                raise InvalidTemplate('Division by zero')
            result = a / b
        else:
            if b.denominator != 1 or abs(b) > 32:
                raise TemplateBudget('Exponent must be an integer in [-32,32]')
            if a == 0 and b < 0:
                raise InvalidTemplate('Zero raised to negative power')
            result = a ** int(b)
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > 256:
        raise TemplateBudget('Exact arithmetic exceeds 256 bits')
    return result


def parse(raw: str) -> dict:
    if len(raw.encode()) > 32768:
        raise TemplateBudget('Response exceeds 32768 bytes')
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise InvalidTemplate('Duplicate JSON key: ' + key)
            value[key] = item
        return value
    try:
        obj = json.loads(raw, object_pairs_hook=unique)
    except (ValueError, RecursionError) as exc:
        raise InvalidTemplate(str(exc)) from exc
    if not isinstance(obj, dict) or set(obj) != {'version', 'sense', 'decode', 'terms', 'explanation'}:
        raise InvalidTemplate('Expected version, sense, decode, terms, explanation only')
    if obj['version'] != 'qubo-template-v1' or obj['sense'] not in ('min', 'max'):
        raise InvalidTemplate('Invalid version or optimization sense')
    if not isinstance(obj['explanation'], str):
        raise InvalidTemplate('Explanation must be a string')
    d = obj['decode']
    if not isinstance(d, dict) or set(d) != {'index', 'complement'} or type(d['complement']) is not bool:
        raise InvalidTemplate('Decoder requires index and boolean complement')
    syntax(d['index'], {'n', 'i'})
    if not isinstance(obj['terms'], list):
        raise InvalidTemplate('Terms must be a list')
    if len(obj['terms']) > 32:
        raise TemplateBudget('At most 32 templates allowed')
    for term in obj['terms']:
        if not isinstance(term, dict) or set(term) != {'over', 'coefficient', 'factors'}:
            raise InvalidTemplate('A term requires over, coefficient, factors')
        if term['over'] not in ('once', 'vertices', 'edges', 'pairs'):
            raise InvalidTemplate('Invalid summation scope')
        names = {'n'} | ({'i'} if term['over'] == 'vertices' else
                         {'i', 'j'} if term['over'] in ('edges', 'pairs') else set())
        syntax(term['coefficient'], names)
        if not isinstance(term['factors'], list) or len(term['factors']) > 2:
            raise InvalidTemplate('At most two factors per term')
        for factor in term['factors']:
            if (not isinstance(factor, dict) or set(factor) != {'index', 'complement'}
                    or type(factor['complement']) is not bool):
                raise InvalidTemplate('A factor requires index and boolean complement')
            syntax(factor['index'], names)
    return obj


def compile_template(obj: dict, problem: dict) -> dict:
    n = problem['n']
    def index(expression, env):
        value = arithmetic(syntax(expression, set(env)), env)
        if value.denominator != 1 or not 0 <= value < n:
            raise InvalidTemplate('Variable index must be an integer within [0,n)')
        return int(value)
    permutation = [index(obj['decode']['index'], {'n': n, 'i': i}) for i in range(n)]
    if sorted(permutation) != list(range(n)):
        raise InvalidTemplate('Decoder must be a bijection')
    total = defaultdict(Fraction)
    for term in obj['terms']:
        rows = ([{}] if term['over'] == 'once' else
                [{'i': i} for i in range(n)] if term['over'] == 'vertices' else
                [{'i': i, 'j': j} for i, j in (problem['edges'] if term['over'] == 'edges'
                                               else combinations(range(n), 2))])
        for row in rows:
            env = {'n': n, **row}
            coefficient = arithmetic(syntax(term['coefficient'], set(env)), env)
            expanded = {(): coefficient}
            for factor in term['factors']:
                pos = index(factor['index'], env)
                updated = defaultdict(Fraction)
                for indices, value in expanded.items():
                    if factor['complement']:
                        updated[indices] += value
                    updated[tuple(sorted(set((*indices, pos))))] += value * (-1 if factor['complement'] else 1)
                expanded = updated
            for indices, value in expanded.items():
                total[indices] += value
    return {'kind': 'cover', 'sense': obj['sense'],
            'decode': {'permutation': permutation, 'complement': [int(obj['decode']['complement'])] * n},
            'terms': [{'coefficient': str(value), 'variables': list(indices)}
                      for indices, value in total.items() if value]}


def evaluate(raw: str, tests: list[dict]) -> dict:
    start = time.monotonic()
    report = {'status': 'not_run', 'format_valid': None, 'finite_semantic_pass': None,
              'task_pass': None, 'tests_planned': len(tests), 'tests_executed': 0, 'tests': []}
    try:
        obj = parse(raw)
        report['format_valid'] = True
        for test in tests:
            try:
                claim = compile_template(obj, test['input'])
                failures = base.check_claim('cover', test['input'], claim)
                row = {'id': test['id'], 'status': 'candidate_error' if failures else 'passed',
                       'failures': failures}
                report['tests_executed'] += 1
            except (InvalidTemplate, base.InvalidClaim) as exc:
                row = {'id': test['id'], 'status': 'candidate_error', 'reason': str(exc)}
            except (TemplateBudget, base.CheckBudget) as exc:
                row = {'id': test['id'], 'status': 'candidate_budget_exceeded', 'reason': str(exc)}
            report['tests'].append(row)
        statuses = {r['status'] for r in report['tests']}
        report['status'] = ('candidate_error' if 'candidate_error' in statuses else
                            'candidate_budget_exceeded' if 'candidate_budget_exceeded' in statuses else 'passed')
        report['finite_semantic_pass'] = (False if 'candidate_error' in statuses else
                                        None if 'candidate_budget_exceeded' in statuses else True)
    except InvalidTemplate as exc:
        report.update(status='candidate_format_error', format_valid=False, reason=str(exc))
    except TemplateBudget as exc:
        report.update(status='candidate_budget_exceeded', reason=str(exc))
    except Exception as exc:
        # Preserve infrastructure errors; do not score them as incorrect model answers.
        report.update(status='infrastructure_error', finite_semantic_pass=None,
                      reason=type(exc).__name__ + ': ' + str(exc))
    report['elapsed_seconds'] = time.monotonic() - start
    return report


def feedback(raw: str, tests: list[dict]) -> dict:
    report = evaluate(raw, tests)
    result = {'status': report['status'], 'scope': 'Finite development checks only; no proof for all graphs.'}
    if report['status'] == 'infrastructure_error':
        raise RuntimeError(report['reason'])
    if 'reason' in report:
        result['reason'] = report['reason']
    for row in report['tests']:
        if row['status'] != 'passed':
            test = next(t for t in tests if t['id'] == row['id'])
            result['counterexample'] = {'input': test['input'], 'diagnostic': row}
            break
    return result
