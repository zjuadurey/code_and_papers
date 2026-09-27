"""Reproduce private sidecars without editing any public input or pending label."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from oracles import expected

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('prior_labels', ROOT / 'pilot/provisional_labels/v0.1/evaluate.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)


def graph(n, edges):
    return {'n': n, 'edges': edges}


def sat(n, clauses, locked=()):
    return {'n': n, 'clauses': clauses, 'locked': list(locked)}


def request(pairs, mode='counts', repetitions=9):
    return {'records': [{'id': f'r{i}', 'left': a, 'right': b} for i, (a, b) in enumerate(pairs)],
            'mode': mode, 'repetitions': repetitions}


SPECS = {
    'lit-002': ('cover', [
        ('empty', 'boundary', graph(0, []), 'empty decoding'),
        ('no_edges', 'boundary', graph(3, []), 'unnecessary selected vertices'),
        ('single_edge', 'discriminating', graph(2, [[0, 1]]), 'positive superincreasing tie reversal'),
        ('tuple_not_mask', 'discriminating', graph(4, [[0, 1], [0, 2], [1, 3], [2, 3]]), 'numeric mask is not tuple lexicographic order'),
        ('triangle', 'normal', graph(3, [[0, 1], [0, 2], [1, 2]]), 'insufficient constraint penalty'),
        ('star', 'discriminating', graph(4, [[0, 1], [0, 2], [0, 3]]), 'feasible but nonminimum cover'),
    ]),
    'lit-004': ('clique', [
        ('empty', 'boundary', graph(0, []), 'empty decoding'),
        ('no_edges', 'discriminating', graph(3, []), 'missing nonedge penalty'),
        ('complete', 'normal', graph(3, [[0, 1], [0, 2], [1, 2]]), 'optimization direction'),
        ('path', 'discriminating', graph(3, [[0, 1], [1, 2]]), 'incorrect canonical numeric mask'),
        ('isolated', 'boundary', graph(1, []), 'rejecting singleton cliques'),
    ]),
    'lit-005': ('predicate', [
        ('empty', 'boundary', sat(0, []), 'empty conjunction is true'),
        ('force_true', 'normal', sat(1, [[[0, 1]] * 3]), 'wrong literal polarity'),
        ('force_false', 'normal', sat(1, [[[0, 0]] * 3]), 'wrong literal polarity'),
        ('locked', 'discriminating', sat(2, [], [[0, 1]]), 'ignored lock'),
        ('unsatisfiable', 'discriminating', sat(1, [[[0, 1]] * 3, [[0, 0]] * 3]), 'missing clause / false absence certificate'),
        ('lex', 'discriminating', sat(2, [[[0, 1], [1, 1], [1, 1]]]), 'arbitrary satisfying assignment instead of lex first'),
        ('tautology', 'boundary', sat(1, [[[0, 0], [0, 1], [0, 1]]]), 'repeated/contradictory literals mishandled'),
    ]),
    'lit-008': ('receipts', [
        ('empty', 'boundary', request([]), 'empty full report'),
        ('normal', 'normal', request([(10, 20), (61, 9), (47, 8)]), 'ignored rows / incorrect count'),
        ('endian', 'discriminating', request([(1, 0)]), 'wrong bit ordering / missing leading zeroes'),
        ('overflow', 'boundary', request([(255, 0), (2, 0)]), 'missing modulo 256 prefix checksum'),
        ('inspect', 'normal', request([(2, 0), (1, 0)], 'inspect'), 'counts in inspect / reordered output'),
    ]),
}

SCOPES = {
    'cover': 'B: ground-state feasibility, minimum cardinality and canonical tuple decoding on valid normalized graphs. Not quantum execution or full inspection reports.',
    'clique': 'B: ground-state compatibility, maximum cardinality and canonical mask decoding on valid eligible graphs. Not request normalization, greedy preview or migration execution.',
    'predicate': 'B: marking predicate on every Boolean vector and core lex-first/absence selection. Not reversible circuit construction, Grover success probability or context retention of valid current.',
    'receipts': 'A/context obligation evidence: exact report examples, not an opportunity label or quantum mapping. No executable candidate migration is submitted or certified.',
}


def build():
    labels, refs = prior.references('C')
    manifest = ROOT / labels['input_manifest']
    rows = json.loads(manifest.read_text())['conditions']
    pins = {str(manifest.relative_to(ROOT)): prior.sha256(manifest),
            'pilot/provisional_labels/v0.1/labels.json': prior.sha256(prior.HERE / 'labels.json'),
            'schemas/phase1_prediction.schema.json': prior.sha256(ROOT / 'schemas/phase1_prediction.schema.json'),
            'pilot/how_review/v0.2/PROTOCOL.md': prior.sha256(ROOT / 'pilot/how_review/v0.2/PROTOCOL.md')}
    cases = []
    for ref in refs:
        cid = ref['mother_case_id']
        entry = next(r for r in rows if r['case_id'] == cid and r['condition'] == 'C')
        path = manifest.parent / entry['file']
        public, _ = prior.packet_sources(path)
        pins[str(path.relative_to(ROOT))] = prior.sha256(path)
        kind, tests = SPECS.get(cid, (None, []))
        cases.append({
            'case_id': cid, 'prediction_case_id': ref['case_id'], 'condition': 'C',
            'input_path': str(path.relative_to(ROOT)), 'input_sha256': entry['sha256'],
            'task_levels': {'A': 'candidate location, concrete family correspondence and conditions',
                            'B': 'conditional plan when structural YES, even if REMAIN_CLASSICAL',
                            'C': 'not required; no executable migration score'},
            'agent_visible': public,
            'submission_contract': {'format': 'unchanged Phase-1 prediction JSON schema 0.2.0',
                'schema': 'schemas/phase1_prediction.schema.json',
                'required_content': 'candidate_regions, separate eligibility/practical/support, decision, rationale; conditional plan on structural YES',
                'not_required': 'private polynomial/tables/receipts are reviewer evidence, NOT new agent outputs'},
            'premises': public['input_domain'],
            'missing_information': 'No measured hardware, oracle/circuit cost, workload frequency or benefit; do not infer positive/negative advantage.',
            'reference': {'structural_eligibility': ref['structural_eligibility'], 'status': 'PENDING',
                          'source': 'pilot/provisional_labels/v0.1/labels.json', 'gold': False,
                          'review_needed': 'candidate boundaries, alternate families, full migration and practical suitability'},
            'oracle_kind': kind, 'verification_scope': SCOPES.get(kind, 'Contract catalogued; executable scoped-claim checks not implemented in this version.'),
            'claim_scope': ('direct_canonical_ground_state' if kind in ('cover', 'clique') else
                            'predicate_and_core_selection' if kind == 'predicate' else
                            'full_receipt_examples' if kind == 'receipts' else None),
            'oracle_basis': 'Original public software definition; independent finite enumeration/bit truth table in oracles.py, not model agreement.',
            'equivalences': ('All binary variable permutations/complements with explicit bijective decode; arbitrary exact constant offset; positive rescaling, or negative rescaling with reversed sense. Every ground state must decode correctly. Alternate constructions outside this data representation remain unjudged.'
                             if kind in ('cover', 'clique', 'predicate') else
                             'Object key order irrelevant; specified list order, eight-bit width and exact counts mandatory. Any implementation producing the contract behavior may be valid.'),
            'scoring': {'format': 'independent validity record', 'opportunity': 'reference agreement only; pending and alternative answers need review',
                        'semantics': 'per-obligation finite evidence, no explanation/format points can offset a counterexample',
                        'completion': 'separate HOW v0.2 ledger; missing claim is insufficient_evidence',
                        'execution': None, 'quality': 'exact, no tolerance or stochastic threshold introduced',
                        'stability_and_resources': 'no model/QPU/stochastic solver measured', 'task_pass': None},
            'tests': [{'id': name, 'category': category, 'input': problem, 'expected': expected(kind, problem),
                       'expected_source': 'Original contract definition, independently computed by oracles.py; anchors also asserted in tests.',
                       'target_error': fault, 'premises': 'Valid normalized core input' if kind != 'receipts' else 'Valid complete public JSON request'}
                      for name, category, problem, fault in tests],
        })
    return {'version': '0.1', 'private': True, 'mother_cases': 10,
            'scope_policy': 'Representative selection fixed by task types: cover, search, unresolved control; clique reuses graph checker. No model-dependent case exclusion.',
            'source_sha256': pins, 'cases': cases}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with args.output.open('x') as handle:
        json.dump(build(), handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write('\n')
