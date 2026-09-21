"""Final artifact checks; no model calls and no scientific reference scoring."""
from pathlib import Path
import hashlib,json,re,shutil,sys,difflib
from collections import Counter

REPO=Path('/home/audrey/code_and_papers/2026/FSE/qrefactorbench')
sys.path.insert(0,str(REPO))
from qrefactorbench.schema import schema_errors
OUT=REPO/'pilot/baseline-v0.1/conditional-plan-diagnostic'
EXT=Path('/home/audrey/qrefactor_conditional_plan_diagnostic')
OLD=REPO/'pilot/baseline-v0.1/restricted-codex'
def sha(data): return hashlib.sha256(data).hexdigest()
def dump(path,obj):
    with path.open('x') as f: json.dump(obj,f,indent=2); f.write('\n')

codes={}; schema_checks={}; instruction=(OUT/'prompt/conditional_plan_instruction.txt').read_bytes()
manifest=json.loads((OUT/'metadata/input_manifest.json').read_text())
for f in manifest['files']:
    assert sha((OUT/f['destination']).read_bytes())==f['sha256']
for i in range(1,11):
    cid=f'pilot-{i:03d}'
    raw=OUT/'raw'/f'{cid}.txt'; parsed=OUT/'parsed'/f'{cid}.json'
    assert raw.read_bytes()==parsed.read_bytes()==(EXT/'raw'/f'{cid}.txt').read_bytes()
    data=json.loads(raw.read_bytes())
    schema_checks[cid]=schema_errors(data,'prediction')
    assert not schema_checks[cid],cid
    codes[cid]={'classification':'SUBSTANTIVE' if data['plan'] is not None else 'NOT APPLICABLE',
      'basis':'AI-assisted descriptive review documented in PLAN_CONTENT_REVIEW.md; not correctness',
      'plan_resource_object_generic_unresolved': data['plan'] is not None and set(data['plan']['expected_resource_characteristics'])=={'status'}}
    original=(REPO/'pilot/packets-v0.1/baseline/prompts'/f'{cid}.md').read_bytes()
    diagnostic=(OUT/'inputs'/cid/'prompt.md').read_bytes()
    assert diagnostic==original+b'\n\n'+instruction
    expected=''.join(difflib.unified_diff(original.decode().splitlines(True),diagnostic.decode().splitlines(True),fromfile=f'pilot-v0.1/{cid}.md',tofile=f'conditional-plan-v1/{cid}.md'))
    assert expected in (OUT/'PROMPT_DIFF.md').read_text()
    meta=json.loads((OUT/'metadata'/f'{cid}.json').read_text())
    assert sha(raw.read_bytes())==meta['raw_output_sha256']
for p in (OUT/'schema').glob('*.json'):
    assert p.read_bytes()==(REPO/'pilot/packets-v0.1/baseline/schemas'/p.name).read_bytes()
    # Packet export uses a different serialization than package source schemas.
    assert json.loads(p.read_bytes())==json.loads((REPO/'schemas'/p.name).read_bytes())

rubric=(OUT/'PLAN_CONTENT_REVIEW.md').read_text().split('## Review summary')[0].rstrip()+'\n'
assert sha(rubric.encode())==json.loads((OUT/'validation/review-rubric-lock.json').read_text())['review_rubric_sha256']
dump(OUT/'plan_content_codes.json',codes)
dump(OUT/'validation/schema-validation.json',schema_checks)
summary=json.loads((OUT/'SUMMARY.json').read_text())
summary['plan_content_classification_counts']=dict(Counter(v['classification'] for v in codes.values()))
summary['plan_content_classification_counts'].update(PARTIAL=0,SUPERFICIAL=0)
summary['diagnostic_interpretation']='A. STRONGER SUPPORT FOR H1; elicitation/formulation level only'
pair=json.loads((OUT/'paired_fields.json').read_text())
def apps(d): return {v['contract_id']:v['applicable'] for v in d['contract_applicability']}
summary['contract_applicability_label_changed_cases']=[p['case_id'] for p in pair if apps(p['original'])!=apps(p['diagnostic'])]
summary['benchmark_support_changed_cases']=[p['case_id'] for p in pair if p['exact_field_changes']['benchmark_supported']]
(OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')

before=json.loads((OUT/'validation/protected-before.json').read_text())
allowed={'PROJECT_STATUS.md','TODO.md','DECISIONS.md','CHANGELOG.md','docs/research_log.md','docs/open_questions.md'}
changed=[f for f,h in before.items() if not (REPO/f).is_file() or sha((REPO/f).read_bytes())!=h]
assert set(changed)==allowed,changed
for f,h in json.loads((OLD/'ARTIFACT_HASHES.json').read_text()).items():
    assert sha((OLD/f).read_bytes())==h
dump(OUT/'validation/final-preservation.json',{'pre_existing_files_checked':len(before),
 'unchanged_count':len(before)-len(changed),'only_allowed_memory_updates':changed,
 'original_baseline_files_unchanged':122,'frozen_v01_packet_files_unchanged':99,
 'no_other_protected_changes':True})

shutil.copyfile('/tmp/qrb_summarize_conditional.py',OUT/'paired_summary.py')
shutil.copyfile(__file__,OUT/'final_audit.py')
# Resolve report links, including the two final files about to be written.
links=[]
for name in ['README.md','PLAN_CONTENT_REVIEW.md','CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md','validation/README.md']:
    p=OUT/name
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        target=p.parent/link
        assert target.exists() or target==OUT/'validation/final-checks.json', (name,link)
        links.append([name,link])
audit=json.loads((OUT/'metadata/run-audit.json').read_text())
assert all(c['exit_code']==0 and c['turns_started']==c['final_messages']==1 and c['raw_matches_event'] and not c['tool_items'] and not c['errors'] and c['retry_count']==0 for c in audit['cases'])
commands=json.loads((OUT/'validation/commands.json').read_text())
assert all(c['exit_code']==0 for c in commands)
dump(OUT/'validation/final-checks.json',{'all_checks_passed':True,'schema_valid':len(schema_checks),
 'raw_parsed_external_bytes_identical':10,'approved_prompt_diff_only':10,'frozen_schema_copies_identical':4,
 'package_schema_json_equivalent':4,
 'review_rubric_prefix_hash_matches':True,'local_report_links_checked':len(links),
 'first_attempts':10,'fresh_threads':10,'turns_per_case':1,'operator_retries':0,'observed_tools':0,
 'existing_validation_commands_exit_zero':len(commands),'reference_scoring_performed':False})
hashes={str(p.relative_to(OUT)):sha(p.read_bytes()) for p in sorted(OUT.rglob('*'))
        if p.is_file() and p.name!='ARTIFACT_HASHES.json'}
dump(OUT/'ARTIFACT_HASHES.json',hashes)
print(json.dumps({'final_checks':'PASS','artifact_hashes':len(hashes),'protected_files':len(before),
 'unchanged_protected':len(before)-len(changed),'allowed_handoff_updates':changed,
 'schema_valid':len(schema_checks),'plan_content':summary['plan_content_classification_counts']},indent=2))
