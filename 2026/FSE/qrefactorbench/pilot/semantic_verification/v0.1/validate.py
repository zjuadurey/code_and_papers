"""Save repeatable local validation; reuse existing Python, no installations/calls."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def run(output: Path, before: Path) -> int:
    output.mkdir(exist_ok=False, parents=True)
    groups = [
        ['tests/test_semantic_verification.py'], ['tests'],
        ['pilot/provisional_labels/v0.1/test_labels.py'],
        ['pilot/how_review/v0.2/test_review.py'],
        ['pilot/reference_completion/v0.1.1/test_corrections.py'],
        ['pilot/reference_cases/v0.1/cases/context-002/test_program.py'],
        ['pilot/source_adaptations/v0.2-where/cases/lit-004/test_program.py'],
        ['pilot/reference_completion/v0.1.1/cases/lit-005/test_program.py'],
        ['pilot/reference_completion/v0.1.1/cases/lit-008/test_program.py'],
    ]
    commands = [[sys.executable, '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *g] for g in groups]
    commands.append([sys.executable, '-B', str(HERE / 'run_controls.py'), '--output', str(output / 'evidence')])
    records = []
    for index, command in enumerate(commands):
        started = time.monotonic()
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        stdout, stderr = f'{index}.stdout.txt', f'{index}.stderr.txt'
        (output / stdout).write_text(process.stdout)
        (output / stderr).write_text(process.stderr)
        records.append({'command': command, 'exit_code': process.returncode,
                        'seconds': time.monotonic() - started, 'stdout': stdout, 'stderr': stderr})
        print(index, process.returncode, process.stdout.splitlines()[-1:], flush=True)
    previous = json.loads(before.read_text())
    changed = [name for name, sha in previous.items()
               if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha]
    result = {'created_utc': datetime.now(timezone.utc).isoformat(), 'commands': records,
              'before_manifest': str(before), 'protected_files': len(previous), 'changed_files': changed,
              'passed': not changed and all(r['exit_code'] == 0 for r in records),
              'new_model_calls': 0, 'new_quantum_runs': 0, 'dependency_installations': 0}
    (output / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--before', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.output.resolve(), args.before.resolve()))
