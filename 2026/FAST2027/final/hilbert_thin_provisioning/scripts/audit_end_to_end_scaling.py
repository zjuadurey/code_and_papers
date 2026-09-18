"""Final idle-system audit after representative scaling measurements."""
import _e2e_common
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path('results/end_to_end_scaling')
lock = open('build/e2e-performance.lock', 'a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
audit = {}
manifests = [Path('results/qdao_end_to_end/phase_a_hashes.json'),
             Path('results/qdao_end_to_end/previous_results_hashes.json'),
             root / 'core_phase_b_hashes.json']
if (root / 'frozen_26_raw_hashes.json').exists():
    manifests.append(root / 'frozen_26_raw_hashes.json')
for manifest in manifests:
    files = json.loads(manifest.read_text())
    for path, expected in files.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path
    audit[manifest.name] = dict(files=len(files), unchanged=True)
match = re.search(r'(\d+) passed', (root / 'final_tests.log').read_text())
assert match and int(match[1]) >= 243
audit['tests_passed'] = int(match[1])
leftovers = [p for p in (root / 'workdir').rglob('*') if p.is_file()]
assert not leftovers
audit['benchmark_state_files_remaining'] = 0
audit.update(json.loads((root / 'analysis_audit.json').read_text()))
tex = Path('results/end_to_end_tables.tex').read_text()
assert tex.count('\\begin{table*}') == 6
build = Path('build/e2e_scaling_tables_check')
build.mkdir(parents=True, exist_ok=True)
(build / 'tables.tex').write_text('\\documentclass{article}\n\\usepackage[margin=1cm]{geometry}\n'
                                '\\begin{document}\n' + tex + '\n\\end{document}\n')
with (build / 'compile.log').open('w') as log:
    subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'tables.tex'],
                   cwd=build, stdout=log, stderr=subprocess.STDOUT, check=True)
assert not subprocess.check_output(['git', '-C', 'external/qdao', 'status', '--porcelain'], text=True)
audit.update(latex_tables=6, latex_compilation_passed=True, qdao_reference_clean=True,
             timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat())
(root / 'final_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
print(json.dumps(audit, indent=2))
