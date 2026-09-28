"""Descriptive paired fields only; no evaluator/reference-label access."""
from pathlib import Path
from collections import Counter
import json

ROOT=Path('/home/audrey/code_and_papers/2026/FSE/qrefactorbench/pilot/baseline-v0.1')
NEW=ROOT/'conditional-plan-diagnostic'; OLD=ROOT/'restricted-codex'
FIELDS=['structural_eligibility','practical_suitability','decision','migration_family',
        'computational_intent','candidate_regions','benchmark_supported','contract_applicability']
pairs=[]; preds=[]
for i in range(1,11):
    cid=f'pilot-{i:03d}'
    old=json.loads((OLD/'parsed'/f'{cid}.json').read_text())
    new=json.loads((NEW/'parsed'/f'{cid}.json').read_text()); preds.append(new)
    pairs.append({'case_id':cid,'original':{k:old[k] for k in FIELDS},
        'diagnostic':{k:new[k] for k in FIELDS},'original_plan_present':old['plan'] is not None,
        'diagnostic_plan_present':new['plan'] is not None,
        'exact_field_changes':{k:old[k]!=new[k] for k in FIELDS}})
yes=[p for p in preds if p['structural_eligibility'] is True]
conditional=[p for p in yes if p['practical_suitability'] in [False,None] and p['decision']=='REMAIN_CLASSICAL']
no=[p for p in preds if p['structural_eligibility'] is False]
audit=json.loads((NEW/'metadata/run-audit.json').read_text())
summary={'experiment_type':'controlled diagnostic; not independent baseline',
 'case_count':len(preds),'successful_cli_executions':sum(c['exit_code']==0 for c in audit['cases']),
 'schema_valid_predictions':json.loads((NEW/'validation/collection.stdout').read_text())['prediction_count'],
 'malformed_predictions':sum(c['parse_status']!='json_object' for c in audit['cases']),
 'operator_retries':sum(c['retry_count'] for c in audit['cases']),
 'observed_tool_items':sum(len(c['tool_items']) for c in audit['cases']),
 'structural_yes':len(yes),'structural_yes_plan_present':sum(p['plan'] is not None for p in yes),
 'structural_yes_practical_no_or_unknown_remain_classical':len(conditional),
 'conditional_subset_plan_present':sum(p['plan'] is not None for p in conditional),
 'structural_no':len(no),'structural_no_plan_null':sum(p['plan'] is None for p in no),
 'decisions':dict(Counter(p['decision'] for p in preds)),
 'practical':dict(Counter('UNCERTAIN' if p['practical_suitability'] is None else 'YES' if p['practical_suitability'] else 'NO' for p in preds)),
 'families':dict(Counter(p['migration_family'] or 'null' for p in preds)),
 'exact_field_change_counts':{k:sum(p['exact_field_changes'][k] for p in pairs) for k in FIELDS},
 'interpretation_notes':['Intent wording differences are not a semantic error metric.','Plan-content classifications are separately reviewed in PLAN_CONTENT_REVIEW.md.','No ground-truth agreement computed.']}
for filename,data in [('paired_fields.json',pairs),('SUMMARY.json',summary)]:
    with (NEW/filename).open('x') as f: json.dump(data,f,indent=2); f.write('\n')
print(json.dumps(summary,indent=2))
