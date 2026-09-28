"""Catch provenance/coverage regressions that would misrepresent the scientific record."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('how_v02_validate', HERE/'validate.py')
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


@pytest.mark.parametrize('corruption', ['drop_failure', 'invent_failure_claim', 'alter_quote', 'erase_correctness_completion_difference'])
def test_corrupt_record_rejected(corruption):
    review = copy.deepcopy(json.loads((HERE/'review.json').read_text()))
    rows = review['rows']
    if corruption == 'drop_failure':
        rows[:] = [r for r in rows if r['response_status'] != 'budget_exhausted_no_final']
    elif corruption == 'invent_failure_claim':
        next(r for r in rows if r['response_status'] == 'budget_exhausted_no_final')['assessments'] = rows[0]['assessments']
    elif corruption == 'alter_quote':
        rows[0]['excerpts']['/plan/formulation'] = 'fabricated quotation'
    else:
        row = next(r for r in rows if r['model'] == 'deepseek-v4-pro' and r['mother_case'] == 'lit-002')
        row['completion'][2]['completion_state'] = 'deferred'
    with pytest.raises(AssertionError):
        validation.check_review(review)
