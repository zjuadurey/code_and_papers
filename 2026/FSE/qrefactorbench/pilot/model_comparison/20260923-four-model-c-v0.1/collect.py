"""Offline strict collection: preserve all forty slots; never repair predictions."""
from collections import Counter
import json
from pathlib import Path

import run as runner

HERE = Path(__file__).resolve().parent
evaluation = runner.deep.evaluation
load = runner.deep.load_document


def inspect(model, entry, ref):
    folder = HERE / 'runs' / model / entry['case_id']
    meta = load(folder / 'metadata.json') if (folder / 'metadata.json').exists() else {}
    errors, response = [], None
    if not meta:
        state = 'not_run' if not (folder / 'started.json').exists() else 'infrastructure_error'
        errors.append('No completed metadata record')
    elif model in runner.gpt.MODELS:
        state = ('candidate_budget_exceeded' if meta.get('timeout') else
                 'infrastructure_error' if meta.get('exit_code') != 0 or meta.get('errors') or not meta.get('turn_completed') else
                 'protocol_violation' if meta.get('tool_items') else 'delivered')
    else:
        state = ('candidate_budget_exceeded' if meta.get('finish_reason') == 'length' else
                 'protocol_violation' if meta.get('unexpected_tool_calls') else
                 'infrastructure_error' if meta.get('http_status') != 200 or meta.get('transport_error') or meta.get('envelope_error') else
                 'delivered' if meta.get('response_complete') else 'delivery_incomplete')
    if state != 'delivered':
        errors.append(state)
    raw = folder / 'response.txt'
    if raw.exists():
        recorded = meta.get('raw_output_sha256') if model in runner.gpt.MODELS else meta.get('response_sha256')
        if runner.digest(raw) != recorded:
            errors.append('Response fingerprint mismatch')
            state = 'infrastructure_error'
        try:
            response = load(raw)
            shape = runner.deep.schema_errors(response, 'prediction')
            errors.extend(shape)
            if not shape:
                if response.get('schema_version') != '0.2.0' or response['case_id'] != ref['case_id']:
                    errors.append('Wrong public task ID or schema version')
                errors.extend(evaluation.region_errors(response['candidate_regions'], ref['sources']))
                if response['plan'] and response['migration_family'] is not None and response['plan']['migration_family'] != response['migration_family']:
                    errors.append('Top-level and plan family mismatch')
            if errors and state == 'delivered':
                state = 'invalid_format'
        except runner.deep.DataError as exc:
            errors.append(str(exc))
            if state == 'delivered':
                state = 'invalid_format'
    else:
        errors.append('No final response file')
        if state == 'delivered':
            state = 'delivery_incomplete'
    valid = state == 'delivered' and not errors
    row = {'mother_case_id': entry['case_id'], 'prediction_case_id': ref['case_id'],
           'valid': valid, 'status': 'valid' if valid else state, 'errors': errors,
           'elapsed_seconds': meta.get('elapsed_seconds'), 'finish_reason': meta.get('finish_reason'),
           'returned_model': meta.get('returned_model'), 'response_path': str(raw.relative_to(runner.ROOT)) if raw.exists() else None,
           'response_sha256': runner.digest(raw) if raw.exists() else None,
           'input_sha256': entry['sha256'], 'operator_retries': meta.get('operator_retries'),
           'structural': response.get('structural_eligibility') if valid else None,
           'practical': response.get('practical_suitability') if valid else None,
           'supported': response.get('benchmark_supported') if valid else None,
           'family': response.get('migration_family') if valid else None,
           'decision': response.get('decision') if valid else None,
           'plan_present': response.get('plan') is not None if valid else None,
           'task_pass': None, 'semantic_review': 'pending_transcription' if valid else 'no_valid_submission'}
    return row, response, meta


def collect():
    protocol = runner.verify()
    _, refs = evaluation.references('C')
    refs = {ref['mother_case_id']: ref for ref in refs}
    summary = {'protocol': 'four-model-C-repeat-20260923', 'review_status': 'PENDING',
               'mother_cases': 10, 'planned_requests': 40, 'condition': 'C', 'models': {},
               'comparison_limits': protocol['comparison_limits'], 'task_pass': None}
    for model in runner.MODELS:
        rows, predictions, usage, positive_rows = [], [], Counter(), []
        for entry in protocol['entries']:
            row, response, meta = inspect(model, entry, refs[entry['case_id']])
            rows.append(row)
            if row['valid']:
                predictions.append(response)
            if refs[entry['case_id']]['structural_eligibility'] is True:
                positive_rows.append({
                    'case_id': entry['case_id'], 'valid': row['valid'],
                    'structural_agreement': row['structural'] is True if row['valid'] else None,
                    'plan_present': row['plan_present'] if row['valid'] else None,
                    'where_exact': evaluation.evaluate_candidates(
                        refs[entry['case_id']]['candidate_regions'], response['candidate_regions'])['candidate_correct'] if row['valid'] else None,
                })
            items = meta.get('usage') or []
            if isinstance(items, dict):
                items = [items]
            for item in items:
                usage.update({key: value for key, value in item.items() if type(value) is int})
        data = {'population': 10, 'valid_responses': len(predictions),
                'status_counts': dict(Counter(r['status'] for r in rows)), 'rows': rows,
                'usage': dict(usage), 'full_population_evaluation_available': len(predictions) == 10}
        data['reference_positive_diagnostics'] = {
            'fixed_population': 7, 'valid_submissions': sum(r['valid'] for r in positive_rows),
            'unavailable_submissions': sum(not r['valid'] for r in positive_rows),
            'structural_matches': sum(r['structural_agreement'] is True for r in positive_rows),
            'plans_present': sum(r['plan_present'] is True for r in positive_rows),
            'where_exact': sum(r['where_exact'] is True for r in positive_rows),
            'rows': positive_rows,
            'meaning': 'Pending-reference agreement/coverage with fixed denominator, not semantic accuracy. Missing answers are unavailable, not semantic errors.'}
        runner.save(HERE / f'validation.{model}.json', rows)
        if len(predictions) == 10:
            runner.save(HERE / f'predictions.{model}.json', predictions)
            profile = '/medium/subscription-codex' if model in runner.gpt.MODELS else '/high/direct-api'
            report = evaluation.evaluate(predictions, 'C', model + profile)
            runner.save(HERE / f'evaluation.{model}.json', report)
            positive = [r for r in report['results'] if r['plan_required_by_reference']]
            data.update(aggregate=report['aggregate'], plan_coverage=report['plan_coverage'],
                        decision_agreement=report['decision_agreement'],
                        where_reference_positive={'population': 7, 'exact_region_set_matches': sum(r['where_diagnostic']['candidate_correct'] for r in positive)})
        summary['models'][model] = data
    runner.save(HERE / 'SUMMARY.json', summary)
    print(json.dumps({m: {'valid': d['valid_responses'], 'population': 10, 'statuses': d['status_counts']} for m, d in summary['models'].items()}, indent=2))


if __name__ == '__main__':
    collect()
