"""2026-09-23 authorized repeat: four named models, ten C cases, one attempt each."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))


def module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


GPT_PATH = 'pilot/model_comparison/20260922-c-v0.1/run.py'
DEEP_PATH = 'pilot/model_comparison/20260922-deepseek-c-v0.1/run.py'
gpt = module('repeat_gpt_transport', GPT_PATH)
deep = module('repeat_deep_transport', DEEP_PATH)
gpt.HERE = deep.HERE = HERE
MODELS = [*gpt.MODELS, *deep.MODELS]
save, digest = deep.save, deep.digest


def prepare() -> None:
    deep.evaluation.references('C')
    manifest_path = ROOT / 'pilot/reference_completion/v0.1.1/review_inputs/manifest.json'
    manifest = deep.load_document(manifest_path)
    entries = [e for e in manifest['conditions'] if e['condition'] == 'C']
    assert len(entries) == 10
    (HERE / 'inputs').mkdir()
    for entry in entries:
        source = manifest_path.parent / entry['file']
        assert digest(source) == entry['sha256']
        (HERE / 'inputs' / entry['file']).write_bytes(source.read_bytes())
    protected = {str(p.relative_to(ROOT)): digest(p)
                 for folder in ('cases', 'schemas', 'qrefactorbench', 'tests', 'pilot')
                 for p in (ROOT / folder).rglob('*')
                 if p.is_file() and not p.is_relative_to(HERE)
                 and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts}
    save(HERE / 'protected_before.json', protected)
    save(HERE / 'protocol.json', {
        'authorization': '2026-09-23 user: 这10个case再用deepseek flash pro gpt 5.6 sol 6 都跑一下？',
        'models': MODELS, 'condition': 'C', 'mother_cases': 10, 'planned_calls': 40,
        'attempts_per_case': 1, 'global_concurrency': 2, 'operator_retries': 0,
        'entries': entries, 'wrapper': gpt.WRAPPER,
        'cli_version': subprocess.check_output([str(gpt.CODEX), '--version'], text=True).strip(),
        'gpt': {'models': list(gpt.MODELS), 'reasoning_effort': 'medium', 'config': gpt.CONFIG,
                'timeout_seconds': 600, 'authentication': 'existing ChatGPT subscription',
                'temperature': None, 'seed': None, 'max_output_tokens': None},
        'deepseek': {'models': deep.MODELS, 'endpoint': deep.ENDPOINT, 'thinking': {'type': 'enabled'},
                     'reasoning_effort': 'high', 'max_tokens': 16384, 'socket_timeout_seconds': 600,
                     'temperature': None, 'seed': None, 'tools': [], 'stream': False},
        'source_sha256': {GPT_PATH: digest(ROOT / GPT_PATH), DEEP_PATH: digest(ROOT / DEEP_PATH),
                          str(Path(__file__).relative_to(ROOT)): digest(Path(__file__)),
                          'pilot/semantic_verification/v0.2/contracts.json': digest(ROOT / 'pilot/semantic_verification/v0.2/contracts.json')},
        'reference_labels_sha256': digest(ROOT / 'pilot/provisional_labels/v0.1/labels.json'),
        'input_manifest_sha256': digest(manifest_path), 'created_utc': deep.now(),
        'evaluation_policy': 'Frozen provisional diagnostics plus separately scoped, quote-bound post-hoc semantic review. No whole-task pass or model ranking.',
        'stop_policy': 'Stop the affected provider after account/transport/tool errors; retain failed attempt and continue the other provider. No retry/repair.',
        'comparison_limits': ['Same C inputs as first run; this is a repeat, not a new benchmark version or holdout.',
                              'GPT medium/Codex vs DeepSeek high/API are not matched compute or scaffolding.',
                              'No private contracts, test controls, annotations or prior answers in model input.',
                              'One additional sample per model/case; no stable ranking or automatic prose correctness score.'],
        'documentation': ['https://learn.chatgpt.com/docs/codex/cli',
                          'https://api-docs.deepseek.com/api/create-chat-completion/']})


def verify() -> dict[str, Any]:
    protocol = deep.load_document(HERE / 'protocol.json')
    if protocol['models'] != MODELS or protocol['planned_calls'] != 40:
        raise ValueError('Unexpected model population')
    for name, sha in protocol['source_sha256'].items():
        if digest(ROOT / name) != sha:
            raise ValueError(f'Frozen runner/reference changed: {name}')
    for name, sha in deep.load_document(HERE / 'protected_before.json').items():
        if digest(ROOT / name) != sha:
            raise ValueError(f'Protected artifact changed: {name}')
    for entry in protocol['entries']:
        if digest(HERE / 'inputs' / entry['file']) != entry['sha256']:
            raise ValueError('Public input changed')
    return protocol


def execute(key_file: Path) -> None:
    protocol = verify()
    if not (HERE / 'preflight/passed.json').exists():
        raise ValueError('Local isolation preflight required')
    key = deep.credential(key_file)  # Never printed or included in artifacts.
    save(HERE / 'run.started.json', {'utc': deep.now(), 'planned': 40})
    records, halted = [], {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for entry in protocol['entries']:
            for provider, models in [('gpt', gpt.MODELS), ('deepseek', deep.MODELS)]:
                if provider in halted:
                    continue
                if provider == 'gpt':
                    futures = [pool.submit(gpt.run_case, model, entry, protocol) for model in models]
                else:
                    config = {**protocol, **protocol['deepseek']}
                    futures = [pool.submit(deep.call, config, model, entry, key) for model in models]
                batch = [f.result() for f in futures]
                records.extend(batch)
                failed = (any(r['exit_code'] != 0 or r['errors'] or r['tool_items'] for r in batch) if provider == 'gpt' else
                          any(r['http_status'] != 200 or r['transport_error'] or r['unexpected_tool_calls'] or r.get('envelope_error') for r in batch))
                if failed:
                    halted[provider] = entry['case_id']
                    save(HERE / f'provider-halted.{provider}.json', {'case_id': entry['case_id'], 'reason': 'See immutable metadata; no retry'})
    save(HERE / 'run.completed.json', {'utc': deep.now(), 'attempted': len(records), 'planned': 40, 'halted_providers': halted})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'preflight', 'run'))
    parser.add_argument('--key-file', type=Path)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    elif args.action == 'preflight':
        verify()
        gpt.preflight()
    else:
        if args.key_file is None:
            parser.error('--key-file must name the already user-designated local file')
        execute(args.key_file)
