"""Post-hoc witness against Sol's lit-009 unique-marker claim, not its fallback.

Trace the unchanged trusted original program. Do not reimplement elimination and
do not execute model-generated code. This witness was found after reading responses.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import run as runner

HERE, ROOT = runner.HERE, runner.ROOT
CASE = ROOT / 'pilot/reference_completion/v0.1.1/cases/lit-009'
sys.path.insert(0, str(CASE))
try:
    common = runner.module('pivot_witness_common', str((CASE / 'common.py').relative_to(ROOT)))
    # The original program imports these two names; execute in this fresh process.
    kernel = runner.module('pivot_witness_kernel', str((CASE / 'kernel.py').relative_to(ROOT)))
    sys.modules['common'], sys.modules['kernel'] = common, kernel
    program = runner.module('pivot_witness_program', str((CASE / 'program.py').relative_to(ROOT)))
finally:
    sys.path.remove(str(CASE))


def witness():
    scale = 2.5e307
    coefficients = [[1, 0, 0, 1, 1], [-1, 1, 0, 1, 1], [-1, -1, 1, 1, 1],
                    [-1, -1, -1, 1, 1], [-1, -1, -1, 1, -1]]
    return {'variables': list('abcde'), 'matrix': [[scale * v for v in row] for row in coefficients],
            'rhs': [1.0] * 5, 'current': [0.0] * 5, 'mode': 'solve', 'residual_limit': 1.0}


def trace_request(request):
    # Verify the full request and pre-solve residual before the solve-only experiment.
    inspection = program.review({**request, 'mode': 'inspect'})
    traces = []

    def trace(frame, event, arg):
        if frame.f_code is kernel.solve.__code__ and event == 'line' and frame.f_lineno == 14:
            state = frame.f_locals
            col, n, rows = state['col'], state['n'], state['rows']
            active = list(range(col, n))
            values = {i: abs(rows[i][col]) for i in active}
            # Literal all-at-least/no-earlier-equal predicate stated by the model.
            marked = [i for i in active if all(values[i] >= values[k] for k in active)
                      and not any(values[j] == values[i] for j in active if j < i)]
            # Separate reviewer control: Python first-incumbent strict-improvement scan.
            incumbent = active[0]
            for i in active[1:]:
                if values[i] > values[incumbent]:
                    incumbent = i
            traces.append({'column': col, 'active_rows': active,
                           'absolute_values_repr': [repr(values[i]) for i in active],
                           'has_nonfinite': any(not math.isfinite(v) for v in values.values()),
                           'original_pivot': state['pivot'], 'model_predicate_marked': marked,
                           'corrected_control_pivot': incumbent,
                           'model_claim_matches': marked == [state['pivot']],
                           'corrected_control_matches': incumbent == state['pivot']})
        return trace

    previous = sys.gettrace()
    try:
        sys.settrace(trace)
        result = {'report': program.review(request)}
    except ValueError as exc:
        result = {'exception': type(exc).__name__, 'message': str(exc)}
    finally:
        sys.settrace(previous)
    return {'input': request, 'inspection': inspection, 'original_result': result, 'pivot_trace': traces}


def run(output):
    runner.verify()
    raw = HERE / 'runs/gpt-5.6-sol/lit-009/response.txt'
    response = runner.deep.load_document(raw)
    quote = response['plan']['formulation']
    assert 'abs(rows[i][col]) is at least every remaining candidate magnitude' in quote
    assert 'same unique index as Python max' in quote
    ordinary = {'variables': ['a', 'b'], 'matrix': [[1.0, 0.0], [0.0, 1.0]],
                'rhs': [1.0, 2.0], 'current': [0.0, 0.0], 'mode': 'solve', 'residual_limit': 1.0}
    normal, failure = trace_request(ordinary), trace_request(witness())
    assert all(t['model_claim_matches'] for t in normal['pivot_trace'])
    assert any(not t['model_claim_matches'] for t in failure['pivot_trace'])
    assert all(t['corrected_control_matches'] for d in (normal, failure) for t in d['pivot_trace'])
    assert failure['original_result'] == {'exception': 'ValueError', 'message': 'numerical overflow'}
    output.mkdir(parents=True, exist_ok=False)
    runner.save(output / 'result.json', {
        'status': 'explicit_predicate_equivalence_contradicted', 'review_status': 'AI_REVIEW_PENDING',
        'case_id': 'lit-009', 'model': 'gpt-5.6-sol', 'post_hoc': True,
        'provenance': {'response_path': str(raw.relative_to(ROOT)), 'response_sha256': runner.digest(raw),
                       'pointer': '/plan/formulation', 'quote': quote,
                       'interpretation': 'At-least is >= over the actual Python binary64 values, with no earlier equal magnitude.'},
        'normal_control': normal, 'counterexample': failure,
        'source_sha256': {str(p.relative_to(ROOT)): runner.digest(p) for p in [Path(__file__), CASE / 'kernel.py', CASE / 'program.py', CASE / 'common.py']},
        'task_pass': None, 'migration_execution_success': None,
        'limits': ['Counterexample to the stated unique-marker predicate only.',
                   'The proposed exact classical fallback can still preserve the final exception.',
                   'Corrected scan is a reviewer control, not model output or a quantum speedup.',
                   'Post-hoc witness, not part of the frozen 61-input suite or a held-out score.']})
    print(json.dumps({'normal_trace_matches': len(normal['pivot_trace']),
                      'counterexample_columns': [t['column'] for t in failure['pivot_trace'] if not t['model_claim_matches']],
                      'corrected_control_all_matches': True, 'task_pass': None}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)
