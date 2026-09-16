"""Post-performance evidence audit and standalone table compilation."""
import _e2e_common
import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path('results/gbsa_comparison')
audit = {}
for name in ['phase_a_hashes.json', 'previous_results_hashes.json']:
    hashes = json.loads((Path('results/qdao_end_to_end') / name).read_text())
    for path, expected in hashes.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path
    audit[name] = dict(files=len(hashes), unchanged=True)
tests = (root / 'final_tests.log').read_text()
match = re.search(r'(\d+) passed', tests)
assert match and not re.search(r'\d+ failed|ERROR collecting', tests)
audit['tests_passed'] = int(match[1])
for label, directory in [('phase_a', Path('results/qdao_end_to_end')), ('gbsa', root)]:
    verification = json.loads((directory / 'correctness.json').read_text())
    assert verification['failures'] == 0
    audit[label + '_exact_cases'] = verification['cases']
    audit[label + '_correctness_failures'] = 0
    leftovers = [p for p in (directory / 'workdir').rglob('*') if p.is_file()]
    assert not leftovers, leftovers[:3]
    audit[label + '_benchmark_state_files_remaining'] = len(leftovers)
    records = [json.loads(p.read_text()) for p in (directory / 'raw').glob('*.json')]
    assert len(records) == (144 if label == 'phase_a' else 72)
    audit[label + '_measured_runs'] = len(records)
assert not subprocess.check_output(['git', '-C', 'external/qdao', 'status', '--porcelain'], text=True)
audit['qdao_reference_clean'] = True
tex = Path('results/end_to_end_tables.tex').read_text()
assert tex.count('\\begin{table*}') == 4
build = Path('build/e2e_tables_check')
build.mkdir(parents=True, exist_ok=True)
(build / 'tables.tex').write_text('\\documentclass{article}\n\\usepackage[margin=1cm]{geometry}\n'
    '\\begin{document}\n' + tex + '\n\\end{document}\n')
with (build / 'compile.log').open('w') as log:
    subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'tables.tex'],
                   cwd=build, stdout=log, stderr=subprocess.STDOUT, check=True)
audit.update(latex_tables=4, latex_compilation_passed=True,
    gbsa_status='MEASURED_REPRODUCTION_COMMON_SUBSTRATE',
    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat())
(root / 'final_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
with (root / 'reproducibility.txt').open('a') as handle:
    handle.write('\nFinal audit: ' + audit['timestamp'] + '\nPython: ' + sys.version + '\n')
    for package in ['qiskit', 'qiskit-aer', 'numpy', 'pandas', 'scipy', 'pytest', 'psutil']:
        handle.write(package + '==' + importlib.metadata.version(package) + '\n')
    handle.write('Commands: python -m pytest -q; python scripts/analyze_end_to_end.py; '
                 'python scripts/audit_end_to_end.py\n')
    for command in [['git', 'rev-parse', 'HEAD'], ['git', 'branch', '--show-current'],
                    ['g++', '--version'], ['uname', '-a']]:
        handle.write('$ ' + ' '.join(command) + '\n' + subprocess.check_output(command, text=True))
print(json.dumps(audit, indent=2))
