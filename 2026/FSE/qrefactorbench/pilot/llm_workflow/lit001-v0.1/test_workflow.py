from copy import deepcopy
import itertools

import pytest

import engine as e
import run as runner


def test_certificate_and_strong_baseline_all_four_node_graphs():
    edges = list(itertools.combinations(range(4), 2))
    for graph in range(64):
        request = {'equipment': ['A', 'B', 'C', 'D'], 'requirements': [
            {'first': chr(65+i), 'second': chr(65+j), 'weight': 1 + k % 3}
            for k, (i, j) in enumerate(edges) if graph & (1 << k)]}
        before = deepcopy(request)
        expected = e.program.schedule(request)
        assert e.strong_classical(request) == expected
        for mask in range(16):
            assert e.finish(request, [mask])[0] == expected
        assert e.finish(request, [])[0] == expected
        assert request == before


@pytest.mark.parametrize('payload', [None, {}, {'equipment': [], 'requirements': []},
    {'equipment': ['A', 'A'], 'requirements': []},
    {'equipment': ['A', 'B'], 'requirements': [{'first': 'A', 'second': 'B', 'weight': True}]}])
def test_boundary_behavior(payload):
    try:
        expected = e.program.schedule(payload)
    except Exception as exc:
        with pytest.raises(type(exc), match=str(exc)):
            e.finish(payload, [0])
    else:
        assert e.finish(payload, [0])[0] == expected
        assert e.strong_classical(payload) == expected


@pytest.mark.parametrize('expression', ['__import__("os")', 'pi.__class__', '[1][0]', '1e999', '2**100', '1/0'])
def test_angle_does_not_execute_code(expression):
    with pytest.raises((ValueError, ZeroDivisionError)):
        e.angle(expression)


def test_gate_parser_and_bit_order():
    source = 'OPENQASM 3.0; include "stdgates.inc"; qubit[4] q; bit[4] r; x q[0];'
    source += ''.join(f'r[{i}] = measure q[{i}];' for i in range(4))
    assert e.probabilities(e.parse_qasm(source))[1] == 1
    with pytest.raises(ValueError): e.parse_qasm(source.replace('stdgates.inc', '/tmp/private.inc'))
    with pytest.raises(ValueError): e.parse_qasm(source + 'h q[0];')


def test_finish_requires_feedback_and_matching_candidate():
    args = {'candidate_sha256': 'a', 'decision': 'REMAIN_CLASSICAL', 'summary_zh': '结果',
            'resource_conditions_zh': '条件', 'assumptions_zh': '假设'}
    with pytest.raises(ValueError): runner.check_finish(args, None, None)
    verified = {'status': 'passed', 'application_sha256': 'b'}
    with pytest.raises(ValueError): runner.check_finish(args, verified, {'points': []})
    verified['application_sha256'] = 'a'
    runner.check_finish(args, verified, {'points': []})
    args['decision'] = 'CONDITIONAL_QUANTUMIZE'
    with pytest.raises(ValueError): runner.check_finish(args, verified, {'points': [{'timing_relation': 'not_faster'}]})
