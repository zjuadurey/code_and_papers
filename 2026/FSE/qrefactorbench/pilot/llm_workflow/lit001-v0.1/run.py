"""Single-LLM JSON action loop over trusted tools; no delegated agents."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback

import engine as e

HERE, ROOT = e.HERE, e.ROOT
MODEL = 'gpt-5.6-sol'
MAX_CALLS = 8
OLD = ROOT / 'pilot/enhancement/state-workflow-v0.3'


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def transport():
    t = load_module('lit001_transport', ROOT / 'pilot/model_comparison/20260922-c-v0.1/run.py')
    binary = shutil.which('codex')
    if not binary: raise RuntimeError('codex CLI not found on PATH')
    t.CODEX = Path(binary).resolve()
    t.CONFIG += ['model_catalog_json="/model-catalog.json"',
                 'tools.update_plan.enabled=false', 'tools.experimental_request_user_input.enabled=false']
    original = t.isolated
    def isolated(inputs, outputs, args):
        cmd = original(inputs, outputs, args)
        cmd[1:1] = ['--ro-bind', str(OLD / 'tool-free-sol-catalog.json'), '/model-catalog.json']
        return cmd
    t.isolated = isolated
    return t


TASK = '''You are the model in a single-case classical-to-quantum workflow.
The controller executes your JSON actions and returns observations in the next request.
Generate your own circuit from the supplied classical source; no previous solution is provided.
Goal: run one simple quantum migration, preserve exact source behavior, and infer when its
complete cost could beat the classical implementation. A negative cost conclusion is valid.
Use QAOA for the supplied four-node MaxCut workload to exercise a quantum optimization path.
Choose a small circuit and concrete angles/shots without requesting a training campaign.
Quantum output is a candidate; exactness is provided by a trusted certificate/fallback helper.
No hand-written answer or computed optimum may be embedded as an X-only answer circuit.
Return exactly one JSON object {"tool": NAME, "arguments": OBJECT}; no Markdown.
Available actions:
1. read_program, arguments {}: get original program.py, kernel.py, public task and workload.
2. verify_candidate, arguments {"plan": nonempty explanation of mapping, angles and contract,
   "qasm": complete OpenQASM 3.0 text, "shots": integer 1..64,
   "decoder": "connected_all_edges_certificate_else_original"}.
   QASM grammar: exact declarations OPENQASM 3.0; include "stdgates.inc"; qubit[4] q; bit[4] r;
   then h q[i]; x q[i]; cx q[i], q[j]; rx(angle) q[i]; rz(angle) q[i];
   angles use numeric literals, pi and +-*/. End with r[i] = measure q[i]; for i=0..3.
   No loops, custom gates, other includes, or other declarations. At most 200 gates.
   Helper checks connected positive-edge graph and whether a measured mask cuts ALL positive
   edges; then complement canonicalization gives the source's minimum-mask tie. Otherwise it
   calls the original exact solver. Other workloads retain the original program.
   Tool returns actual QDK simulation, independent probabilities, all measurement outcomes,
   certificate/fallback and exact source output comparisons. Errors may be corrected by
   submitting a new candidate; all attempts retained. This is an engineering run, not an eval score.
3. estimate_cost, arguments {}: estimates latest successfully verified circuit using real QDK,
   measures original and strong classical costs, includes classical recovery and six overheads,
   returns hypothetical hardware points and full-cost break-even conditions. Inspect returned
   assumptions. Simulation wall time is not QPU time. Cost model is steady-state fixed workload.
4. finish, arguments {"candidate_sha256": string matching tools,
   "decision": "REMAIN_CLASSICAL" or "CONDITIONAL_QUANTUMIZE",
   "summary_zh": Chinese explanation of actual behavior, resources and complete cost,
   "resource_conditions_zh": Chinese necessary time/qubit conditions from observed data,
   "assumptions_zh": Chinese scenario assumptions and scope}.
   Finish only after successful verify_candidate AND estimate_cost for the same circuit.
Do not claim quantum advantage on a tiny workload just because it can be quantumized.
You have at most eight model turns including finish. Start by read_program.
'''


def preflight(t, folder: Path) -> None:
    """Inspect actual serialized inference request using a local rejecting sink."""
    folder.mkdir()
    with tempfile.TemporaryDirectory(prefix='qrb-lit001-preflight-') as tmp:
        tmp = Path(tmp)
        inputs, outputs = tmp / 'input', tmp / 'output'
        inputs.mkdir(); outputs.mkdir()
        (inputs / 'prompt.txt').write_text(TASK)
        dummy = tmp / 'dummy-auth.json'
        dummy.write_text('{}')
        def local(args, executable='/codex'):
            cmd = t.isolated(inputs, outputs, args)
            cmd[cmd.index(str(t.AUTH))] = str(dummy)
            cmd.insert(1, '--unshare-net')
            cmd[len(cmd)-len(args)-1] = executable
            return cmd
        capture = subprocess.run(local(['-c', (OLD / 'capture_request.py').read_text(), json.dumps(t.CONFIG)],
                                       '/usr/bin/python3'), capture_output=True, timeout=50)
        (folder / 'capture.stdout').write_bytes(capture.stdout)
        (folder / 'capture.stderr').write_bytes(capture.stderr)
        for p in outputs.iterdir():
            if p.is_file(): (folder / p.name).write_bytes(p.read_bytes())
        if capture.returncode: raise RuntimeError('Offline request capture failed')
        request = json.loads((outputs / 'captured-request.json').read_text())
        tools = request.get('tools', []) + [tool for item in request.get('input', [])
                                         if item.get('type') == 'additional_tools' for tool in item.get('tools', [])]
        if tools: raise RuntimeError('Model transport unexpectedly exposes built-in tools')
        if request['model'] != MODEL: raise RuntimeError('Model differs from protocol')
        if request.get('reasoning', {}).get('effort') != 'medium': raise RuntimeError('Wrong reasoning effort')
        serialized = json.dumps(request, ensure_ascii=False)
        for marker in ('FSE 工作区入口', 'Audrey 的全局', 'provisional_labels', 'workflow_smoke'):
            if marker in serialized: raise RuntimeError('Unexpected repository/private context')
        if TASK not in [part.get('text') for msg in request.get('input', [])
                        for part in msg.get('content', []) if isinstance(part, dict)]:
            raise RuntimeError('Exact prompt missing')
        probe = 'from pathlib import Path; import json; print(json.dumps([p for p in ' + repr([
            str(ROOT), str(Path.home() / '.codex/config.toml')]) + ' if Path(p).exists()]))'
        fs = subprocess.run(local(['-c', probe], '/usr/bin/python3'), capture_output=True, timeout=10)
        if fs.returncode or json.loads(fs.stdout) != []: raise RuntimeError('Private paths visible')
    e.save(folder / 'passed.json', {'tools': tools, 'model': request['model'], 'offline': True,
        'model_calls': 0, 'private_paths_visible': [], 'credentials': 'dummy only',
        'cli_version': subprocess.check_output([str(t.CODEX), '--version'], text=True).strip()})


def model_call(t, output: Path, step: int, history: list) -> dict:
    prompt = TASK + '\nController transcript (ordered JSON):\n' + json.dumps(history, ensure_ascii=False)
    name = f'turn-{step:02}'
    path = output / 'inputs' / f'{name}.txt'
    path.write_text(prompt)
    t.HERE = output
    record = t.run_case(MODEL, {'case_id': name, 'prediction_case_id': 'lit001-workflow',
                        'file': path.name, 'sha256': e.sha(path)},
                        {'cli_version': subprocess.check_output([str(t.CODEX), '--version'], text=True).strip()})
    if record['exit_code'] or record['errors'] or record['tool_items'] or not record['turn_completed']:
        raise RuntimeError('Model transport failed; raw output retained without automatic retry')
    raw = (output / 'runs' / MODEL / name / 'response.txt').read_text()
    return json.loads(raw)


def check_finish(args: dict, verified: dict | None, cost: dict | None) -> None:
    if verified is None or cost is None or verified['status'] != 'passed':
        raise ValueError('Need successful behavior and cost tools before finish')
    if set(args) != {'candidate_sha256', 'decision', 'summary_zh', 'resource_conditions_zh', 'assumptions_zh'}:
        raise ValueError('Incorrect finish fields')
    if args['candidate_sha256'] != verified['application_sha256']:
        raise ValueError('Conclusion refers to a different candidate')
    if args['decision'] not in ('REMAIN_CLASSICAL', 'CONDITIONAL_QUANTUMIZE'):
        raise ValueError('Unsupported conclusion')
    for k in ('summary_zh', 'resource_conditions_zh', 'assumptions_zh'):
        if not isinstance(args[k], str) or not args[k].strip(): raise ValueError(f'Missing {k}')
    if args['decision'] == 'CONDITIONAL_QUANTUMIZE' and not any(
            p['timing_relation'] == 'faster' for p in cost['points']):
        raise ValueError('No estimated profile supports faster complete cost')


def run(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=False)
    (output / 'inputs').mkdir()
    t = transport()
    files = [HERE / 'run.py', HERE / 'engine.py', OLD / 'tool-free-sol-catalog.json',
             ROOT / 'pilot/model_comparison/20260922-c-v0.1/run.py', OLD / 'capture_request.py',
             ROOT / 'qrefactorbench/resource_workflow.py', ROOT / 'qrefactorbench/_qdk_resource_worker.py',
             *[e.CASE / p for p in ('program.py', 'kernel.py', 'public_task.json')]]
    protocol = {'version': 'lit001-llm-workflow-v0.1', 'authorization':
        '2026-09-28 side conversation: user requests actual LLM/tool/feedback lit-001 workflow, then says 做.',
        'model': MODEL, 'reasoning_effort': 'medium', 'max_model_calls': MAX_CALLS,
        'transport': 'Existing subscription, isolated tools=[] text inference; controller dispatches JSON actions.',
        'retry': 'No inference transport retries by runner; failed tool calls feed back within eight turns.',
        'input_allowlist': ['program.py', 'kernel.py', 'public_task.json', 'fixed instance', 'tool documentation', 'current tool observations'],
        'excluded': 'Prior generated circuits, model outputs, labels and private reference solutions',
        'scope': 'One workload engineering run; no comparison experiment or new benchmark labels',
        'scenario': {'dispatch_seconds': 1e-6, 'communication_seconds': 1e-6,
                     'compilation_seconds_per_request': 0, 'mode': 'steady-state precompiled fixed workload'},
        'source_sha256': {str(p.relative_to(ROOT)): e.sha(p) for p in files},
        'cli_version': subprocess.check_output([str(t.CODEX), '--version'], text=True).strip(),
        'cli_sha256': e.sha(t.CODEX), 'created_utc': datetime.now(timezone.utc).isoformat()}
    e.save(output / 'protocol.json', protocol)
    history, candidate, verified, cost = [], None, None, None
    read = False
    try:
        preflight(t, output / 'preflight')
        for step in range(1, MAX_CALLS+1):
            try:
                action = model_call(t, output, step, history)
            except json.JSONDecodeError as exc:
                history.append({'model_parse_error': str(exc), 'controller': 'Return strict JSON action'})
                e.save(output / f'transcript-{step:02}.json', history)
                continue
            history.append({'model_action': action})
            tool_folder = output / f'tool-{step:02}'
            tool_folder.mkdir()
            try:
                if set(action) != {'tool', 'arguments'} or not isinstance(action['arguments'], dict):
                    raise ValueError('Expected tool and arguments object')
                name, args = action['tool'], action['arguments']
                print(f'controller step={step} tool={name}', flush=True)
                if name == 'read_program':
                    if args: raise ValueError('read_program takes no arguments')
                    read = True
                    result = {'files': {p: (e.CASE / p).read_text() for p in
                              ('program.py', 'kernel.py', 'public_task.json')}, 'workload': e.INSTANCE}
                elif name == 'verify_candidate':
                    if not read: raise ValueError('Read the original program first')
                    candidate, verified, cost = None, None, None
                    e.save(tool_folder / 'candidate.json', args)
                    result = e.verify(args, tool_folder)
                    candidate, verified = args, result
                elif name == 'estimate_cost':
                    if args: raise ValueError('estimate_cost takes no arguments')
                    if candidate is None or verified is None: raise ValueError('Verify a candidate first')
                    result = e.compare(candidate, verified, tool_folder)
                    cost = result
                elif name == 'finish':
                    check_finish(args, verified, cost)
                    result = {'status': 'accepted'}
                    e.save(output / 'conclusion.json', args)
                else:
                    raise ValueError('Unknown tool')
            except Exception as exc:
                result = {'status': 'error', 'error': f'{type(exc).__name__}: {exc}'}
                (tool_folder / 'error.txt').write_text(traceback.format_exc())
            e.save(tool_folder / 'observation.json', result)
            history.append({'tool_observation': result})
            e.save(output / f'transcript-{step:02}.json', history)
            if (output / 'conclusion.json').exists():
                changed = [p for p, h in protocol['source_sha256'].items() if e.sha(ROOT / p) != h]
                if changed: raise RuntimeError(f'Source changed during run: {changed}')
                e.save(output / 'summary.json', {'status': 'completed', 'actual_model_calls': step,
                    'model': MODEL, 'candidate_sha256': verified['application_sha256'],
                    'verification': verified['status'], 'actual_fallback_used': verified['fallback_used'],
                    'decision': args['decision'], 'cost_points': len(cost['points']),
                    'model_generated_circuit': True, 'all_source_hashes_unchanged': True})
                e.save(output / 'manifest.json', {str(p.relative_to(output)): e.sha(p)
                    for p in sorted(output.rglob('*')) if p.is_file()})
                return 0
        raise RuntimeError('Eight-turn budget exhausted without accepted conclusion')
    except Exception as exc:
        e.save(output / 'failed.json', {'error': str(exc), 'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.output.resolve()))
