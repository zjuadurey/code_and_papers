from pathlib import Path
import hashlib, json, shutil, subprocess, difflib
from datetime import datetime, timezone

REPO=Path('/home/audrey/code_and_papers/2026/FSE/qrefactorbench')
OLD=REPO/'pilot/baseline-v0.1/restricted-codex'
OUT=REPO/'pilot/baseline-v0.1/conditional-plan-diagnostic'
EXT=Path('/home/audrey/qrefactor_conditional_plan_diagnostic')
PACKET=REPO/'pilot/packets-v0.1/baseline'
def sha(data): return hashlib.sha256(data).hexdigest()
def dump(path,obj):
    with path.open('x') as f: json.dump(obj,f,indent=2); f.write('\n')

assert not OUT.exists() and not EXT.exists(), 'Refuse overwrite'
historical=json.loads((OLD/'ARTIFACT_HASHES.json').read_text())
for path,digest in historical.items():
    assert sha((OLD/path).read_bytes())==digest, path
# Byte fingerprints only: do not parse or expose protected reference annotations.
before={str(p.relative_to(REPO)):sha(p.read_bytes()) for p in sorted(REPO.rglob('*'))
        if p.is_file() and not any(x in p.parts for x in ['__pycache__','.pytest_cache','.git'])}
OUT.mkdir(); EXT.mkdir()
for d in ['prompt','inputs','schema','raw','parsed','metadata','logs']:
    (EXT/d).mkdir()
(OUT/'validation').mkdir()
dump(OUT/'validation/protected-before.json',before)
instruction='''Whenever structural quantumizability = YES, always provide a
conditional migration plan describing HOW the computation could be
quantumized, even if practical suitability = NO or UNCERTAIN.

The conditional migration plan describes a technically plausible
quantum reformulation under stated assumptions. It does NOT imply a
recommendation to deploy the quantum version.

Therefore:

    Structural = YES
    Practical = NO / UNCERTAIN
    Decision = REMAIN_CLASSICAL

is still compatible with:

    plan != null

Any unresolved semantic, exactness, resource, encoding, oracle,
certification, or feasibility requirement must remain explicitly
identified inside the plan rather than being silently assumed away.
'''
(EXT/'prompt/conditional_plan_instruction.txt').write_text(instruction)
ids=[f'pilot-{i:03d}' for i in range(1,11)]
records=[]; diffs=[]
for cid in ids:
    original=(PACKET/'prompts'/f'{cid}.md').read_bytes()
    oldmeta=json.loads((OLD/'metadata'/f'{cid}.json').read_text())
    assert sha(original)==oldmeta['input_sha256']
    diagnostic=original+b'\n\n'+instruction.encode()
    (EXT/'inputs'/cid).mkdir()
    target=f'inputs/{cid}/prompt.md'
    (EXT/target).write_bytes(diagnostic)
    records.append({'destination':target,'source_packet_path':f'prompts/{cid}.md',
                    'sha256':sha(diagnostic),'original_prompt_sha256':sha(original),
                    'frozen_case_input_sha256':sha(original),
                    'transformation':'original bytes + two LF bytes + approved instruction bytes'})
    diff=''.join(difflib.unified_diff(original.decode().splitlines(True),diagnostic.decode().splitlines(True),
              fromfile=f'pilot-v0.1/{cid}.md',tofile=f'conditional-plan-v1/{cid}.md'))
    diffs.append(f'## {cid}\n\n```diff\n{diff}```\n')
for p in sorted((PACKET/'schemas').glob('*.json')):
    target=f'schema/{p.name}'; shutil.copyfile(p,EXT/target)
    records.append({'destination':target,'source_packet_path':f'schemas/{p.name}','sha256':sha(p.read_bytes())})
dump(EXT/'metadata/input_manifest.json',{'version':'conditional-plan-v1','case_ids':ids,'files':records,
    'instruction_sha256':sha(instruction.encode()),'model_visible_files_per_case':['/work/prompt.md'],
    'audit':'Only frozen public rendered prompts, the approved appended instruction and generic schemas copied. No responses, reference annotations or retrospective diagnosis copied.'})
runner=Path('/home/audrey/qrefactor_baseline_v01/run_baseline.py').read_bytes()
assert runner==(OLD/'runner_snapshot.txt').read_bytes()
(EXT/'run_baseline.py').write_bytes(runner)
cli=Path('/home/audrey/.local/bin/codex').resolve()
old_command=json.loads((OLD/'metadata/pilot-001.json').read_text())['command']
assert str(cli) in old_command
version=subprocess.check_output([str(cli),'--version'])
assert version.strip()==b'codex-cli 0.154.0'
(EXT/'metadata/cli-version.txt').write_bytes(version)
(EXT/'metadata/exec-help.txt').write_bytes(subprocess.check_output([str(cli),'exec','--help']))
status=subprocess.run([str(cli),'login','status'],capture_output=True)
assert status.returncode==0
(EXT/'metadata/login-status.txt').write_bytes(status.stdout+status.stderr)
dump(EXT/'metadata/protocol-lock.json',{'locked_utc':datetime.now(timezone.utc).isoformat(),
 'runner_sha256':sha(runner),'original_runner_identical':True,'cli_binary':str(cli),
 'cli_binary_sha256':sha(cli.read_bytes()),'cli_version':version.decode().strip(),
 'model':'gpt-5.6-sol','reasoning':'high','authentication':'existing ChatGPT login',
 'retry_policy':'one first attempt per case; no scientific retries or repairs',
 'only_scientific_change':'append exact approved conditional-plan instruction',
 'previous_responses_exposed':False,'reference_annotations_exposed':False})
(OUT/'PROMPT_DIFF.md').write_text('# Conditional-plan diagnostic prompt diff\n\nVersion: conditional-plan-v1. The sole scientific edit appends the researcher-approved instruction to each original rendered prompt, separated by two LF bytes. All original bytes, including case content, remain an exact prefix. No wrapper/config/schema change. Original and diagnostic SHA-256 values are recorded per case in metadata/input_manifest.json. The instruction is in prompt/conditional_plan_instruction.txt.\n\n'+'\n'.join(diffs))
readme='''# Controlled conditional-plan diagnostic — protocol locked before runs

This is a controlled diagnostic rerun testing conditional-plan elicitation. It is not an independent model baseline and must not be counted as a separate model in benchmark comparisons.

Ten frozen pilot-v0.1 rendered model inputs are used with one appended researcher-approved instruction. No prior response, diagnosis or private annotation is supplied. The original runner is copied byte-for-byte: ChatGPT authentication, codex-cli 0.154.0, gpt-5.6-sol, high reasoning, one fresh ephemeral read-only Codex invocation per case in a Bubblewrap namespace. Only that case's prompt is mounted into /work; no repository, other inputs, host configuration/history or previous responses are mounted. CLI built-in harness descriptions remain as in the original experiment.

One non-scientific fixed-token smoke test precedes the ten sequential first-attempt calls. No scientific retries, repairs, tool use, feedback, or prompt tuning. Unmodified schemas validate outputs afterward; null/invalid responses are preserved. No reference scoring is planned. The original server snapshot and sampling seed are unexposed; matching configuration does not guarantee deterministic sampling.

The scientific task addition is prompt/conditional_plan_instruction.txt. Per-input hashes and the model-visible allowlist are in metadata/input_manifest.json; configuration lock in metadata/protocol-lock.json. Per-case metadata records commands, timestamps, hashes, exits, parse states and retries. raw/ preserves exact final-message bytes; parsed/ preserves byte-identical copies only for valid JSON objects. Logs retain events/stderr. The runner refuses overwrite. Never run it from the repository.
'''
(EXT/'README_EXPERIMENT.md').write_text(readme)
print(json.dumps({'external':str(EXT),'results':str(OUT),'protected_files':len(before),
 'original_manifest_files_verified':len(historical),'copied_model_inputs':len(records),
 'runner_byte_identical':True,'only_prompt_addition_verified':True}))
