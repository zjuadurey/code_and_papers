"""Post-run preservation/audit/validation only; never invokes a model."""
from pathlib import Path
import hashlib, json, shutil, subprocess, re
from datetime import datetime, timezone

REPO=Path('/home/audrey/code_and_papers/2026/FSE/qrefactorbench')
OLD=REPO/'pilot/baseline-v0.1/restricted-codex'
OUT=REPO/'pilot/baseline-v0.1/conditional-plan-diagnostic'
EXT=Path('/home/audrey/qrefactor_conditional_plan_diagnostic')
PY='/home/audrey/miniconda3/envs/palqo/bin/python'
def sha(data): return hashlib.sha256(data).hexdigest()
def dump(path,obj):
    with path.open('x') as f: json.dump(obj,f,indent=2); f.write('\n')
ids=[f'pilot-{i:03d}' for i in range(1,11)]
assert all((EXT/'metadata'/f'{cid}.json').is_file() for cid in ids)
audit=[]; threads=[]
manifest=json.loads((EXT/'metadata/input_manifest.json').read_text())
for f in manifest['files']:
    assert sha((EXT/f['destination']).read_bytes())==f['sha256']
instruction=(EXT/'prompt/conditional_plan_instruction.txt').read_bytes()
assert sha(instruction)==manifest['instruction_sha256']
lock=json.loads((EXT/'metadata/protocol-lock.json').read_text())
assert sha((EXT/'run_baseline.py').read_bytes())==lock['runner_sha256']
assert sha(Path(lock['cli_binary']).read_bytes())==lock['cli_binary_sha256']
for cid in ids:
    m=json.loads((EXT/'metadata'/f'{cid}.json').read_text())
    om=json.loads((OLD/'metadata'/f'{cid}.json').read_text())
    original=(REPO/'pilot/packets-v0.1/baseline/prompts'/f'{cid}.md').read_bytes()
    prompt=(EXT/'inputs'/cid/'prompt.md').read_bytes()
    assert prompt==original+b'\n\n'+instruction
    assert sha(original)==om['prompt_sha256']==om['input_sha256']
    assert sha(prompt)==m['prompt_sha256']==m['input_sha256']
    def argv_norm(argv):
        return [re.sub(r'/tmp/qrb-pilot-\d{3}-[^/]+/', '/tmp/qrb-CASE-UNIQUE/', arg) for arg in argv]
    assert argv_norm(m['command'])==argv_norm(om['command']), cid
    for field in ['cli_version','model_argument','reasoning_effort','sandbox','ephemeral','wrapper','authentication']:
        assert m[field]==om[field], (cid,field)
    events=[json.loads(line) for line in (EXT/'logs'/f'{cid}.events.jsonl').read_text().splitlines()]
    items=[e['item'] for e in events if e.get('type')=='item.completed']
    messages=[i for i in items if i.get('type')=='agent_message']
    unexpected=[i for i in items if i.get('type') not in ['agent_message','error']]
    rawpath=EXT/'raw'/f'{cid}.txt'; raw=rawpath.read_bytes() if rawpath.exists() else None
    assert raw is None or sha(raw)==m['raw_output_sha256']
    parsed=EXT/'parsed'/f'{cid}.json'
    assert not parsed.exists() or parsed.read_bytes()==raw
    warnings=[i.get('message') for i in items if i.get('type')=='error']
    threads.extend(m['thread_ids'])
    audit.append({'case_id':cid,'exit_code':m['exit_code'],'parse_status':m['parse_status'],
      'turns_started':sum(e.get('type')=='turn.started' for e in events),
      'final_messages':len(messages),'raw_matches_event':raw is not None and len(messages)==1 and raw.decode().rstrip('\n')==messages[0]['text'].rstrip('\n'),
      'unexpected_items':unexpected,'tool_items':m['tool_items'],'errors':m['errors'],
      'startup_warnings':warnings,'retry_count':m['retry_count'],'argv_matches_except_temp_paths':True,
      'only_approved_prompt_addition':True})
dump(EXT/'metadata/run-audit.json',{'cases':audit,'unique_threads':len(set(threads)),
    'all_ten_thread_ids_distinct':len(threads)==len(set(threads))==10,
    'audit_note':'No gold/reference correctness comparisons. Native bounded transport retries not fully observable; startup warnings retained.'})
for d in ['prompt','inputs','schema','raw','parsed','metadata','logs']:
    shutil.copytree(EXT/d,OUT/d)
shutil.copyfile(EXT/'run_baseline.py',OUT/'runner_snapshot.txt')
shutil.copyfile(EXT/'README_EXPERIMENT.md',OUT/'README_EXPERIMENT.md')
shutil.copyfile(__file__,OUT/'postrun_audit.py')
checks=[
 ('collection',[PY,'scripts/prepare_pilot.py','collect','--responses',str(OUT/'parsed'),'--output',str(OUT/'predictions.json')]),
 ('pytest-core',[PY,'-m','pytest','-q']),
 ('pytest-optional',['/home/audrey/miniconda3/envs/htp-static/bin/python','-m','pytest','-q','tests/test_optional.py']),
 ('dataset-validation',[PY,'-m','qrefactorbench','validate','cases/']),
 ('dataset-summary',[PY,'-m','qrefactorbench','summarize','cases/','--json']),
]
results=[]
for name,cmd in checks:
    result=subprocess.run(cmd,cwd=REPO,capture_output=True)
    (OUT/'validation'/f'{name}.stdout').write_bytes(result.stdout)
    (OUT/'validation'/f'{name}.stderr').write_bytes(result.stderr)
    results.append({'name':name,'command':cmd,'cwd':str(REPO),'exit_code':result.returncode,
                    'stdout':f'{name}.stdout','stderr':f'{name}.stderr'})
    print(json.dumps({'validation':name,'exit_code':result.returncode,'stdout':result.stdout.decode()[:1000]}),flush=True)
dump(OUT/'validation/commands.json',results)
before=json.loads((OUT/'validation/protected-before.json').read_text())
changed=[f for f,d in before.items() if not (REPO/f).is_file() or sha((REPO/f).read_bytes())!=d]
dump(OUT/'validation/preservation.json',{'files_checked':len(before),'changed':changed,
    'original_baseline_files_checked':sum(f.startswith('pilot/baseline-v0.1/restricted-codex/') for f in before),
    'frozen_v01_packet_files_checked':sum(f.startswith('pilot/packets-v0.1/') for f in before),
    'checked_utc':datetime.now(timezone.utc).isoformat()})
assert not changed,changed
print('Post-run preservation PASS:',len(before),'pre-existing files unchanged')
