"""Run the positive case and the boundary case in separate Python processes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--qdk-python', default=sys.executable)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    statuses = []
    for case in ('lit001-v0.1', 'lit005-v0.1'):
        proc = subprocess.run([sys.executable, '-B', str(HERE / case / 'run.py'),
            '--output', str(output / case), '--qdk-python', args.qdk_python],
            capture_output=True, text=True, check=False)
        (output / f'{case}.stdout.txt').write_text(proc.stdout)
        (output / f'{case}.stderr.txt').write_text(proc.stderr)
        statuses.append({'case': case, 'exit_code': proc.returncode})
        print(f'{case}: {"passed" if proc.returncode == 0 else "failed; inspect saved stderr"}', flush=True)
    (output / 'run-status.json').write_text(json.dumps(statuses, indent=2) + '\n')
    return int(any(item['exit_code'] != 0 for item in statuses))


if __name__ == '__main__':
    raise SystemExit(main())
