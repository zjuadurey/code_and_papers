"""Bind the same executed unique-marker witness to Pro's identical predicate claim."""
import run as runner


def bind():
    runner.verify()
    witness_path = runner.HERE / 'pivot-witness/result.json'
    witness = runner.deep.load_document(witness_path)
    raw = runner.HERE / 'runs/deepseek-v4-pro/lit-009/response.txt'
    response = runner.deep.load_document(raw)
    quote = response['plan']['formulation']
    assert 'abs(rows[i][c]) is at least as large as abs(rows[k][c]) for every k in D' in quote
    assert 'no earlier index j<i in D has the same absolute value' in quote
    assert response['case_id'] == 'lit-009'
    assert any(not t['model_claim_matches'] for t in witness['counterexample']['pivot_trace'])
    runner.save(runner.HERE / 'pivot-witness/pro-binding.json', {
        'model': 'deepseek-v4-pro', 'case_id': 'lit-009', 'review_status': 'AI_REVIEW_PENDING',
        'status': 'explicit_predicate_equivalence_contradicted', 'post_hoc': True,
        'response_path': str(raw.relative_to(runner.ROOT)), 'response_sha256': runner.digest(raw),
        'pointer': '/plan/formulation', 'quote': quote,
        'interpretation': 'i in active domain; abs_i >= abs_k for every active k; no earlier equal abs value. Identical predicate to the executed witness.',
        'shared_witness_path': str(witness_path.relative_to(runner.ROOT)),
        'shared_witness_sha256': runner.digest(witness_path),
        'output_decoding_quote': response['plan']['output_decoding'],
        'task_pass': None, 'migration_execution_success': None,
        'limit': 'Pro explicitly falls back to Python max. The incorrect unique-marker claim does not refute that complete conditional fallback plan.'})
    print('Pro predicate bound to the same reachable-NaN witness; full plan remains unjudged.')


if __name__ == '__main__':
    bind()
