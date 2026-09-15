import _common
import datetime
import importlib
import json
import shutil
import subprocess
import sys
import yaml
from pathlib import Path
from htp.loaders import backend
from htp.workload_discovery import write_csv

for module in ['qiskit', 'qiskit_aer', 'qiskit_qasm3_import', 'numpy', 'scipy', 'pandas', 'matplotlib', 'networkx', 'psutil', 'tqdm', 'yaml', 'pytest']:
    m = importlib.import_module(module)
    print(module, getattr(m, '__version__', 'import ok'))
assert sys.version_info[:2] == (3, 11)

commands = [['date', '-Is'], ['uname', '-a'], ['lscpu'], ['free', '-h'], [sys.executable, '--version'],
            ['conda', 'info'], [sys.executable, '-m', 'pip', 'freeze'], [sys.executable, '-m', 'pytest', '--version']]
if shutil.which('nvidia-smi'):
    commands.append(['nvidia-smi'])
with Path('results/manifests/environment.txt').open('w') as f:
    for command in commands:
        r = subprocess.run(command, text=True, capture_output=True)
        f.write('$ ' + ' '.join(command) + '\n' + r.stdout + r.stderr + '\n')
        assert r.returncode == 0, command
Path('requirements.lock.txt').write_text(subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True))
history=subprocess.check_output(['conda', 'env', 'export', '-n', 'htp-static', '--from-history'], text=True)
Path('results/manifests/environment.from-history.yml').write_text(history)
portable=yaml.safe_load(history)
portable.pop('prefix',None)
portable['channels']=['conda-forge','nodefaults']
Path('environment.yml').write_text(yaml.safe_dump(portable,sort_keys=False))
repos = []
for name in ['qdao', 'QASMBench', 'veriq-benchmark', 'qcs']:
    path = Path('external')/name
    def git(*args):
        return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()
    dirty = bool(git('status', '--porcelain'))
    assert not dirty, f'External repository is dirty: {name}'
    reflog=(path/'.git/logs/HEAD').read_text().splitlines()[0]
    clone_epoch=int(reflog.split('\t',1)[0].rsplit(' ',2)[-2])
    repos.append(dict(name=name, local_path=str(path), repository=git('remote', 'get-url', 'origin'),
                      git_commit=git('rev-parse', 'HEAD'), git_branch=git('branch', '--show-current'), dirty=dirty,
                      clone_date=datetime.datetime.fromtimestamp(clone_epoch, datetime.timezone.utc).isoformat()))
write_csv('results/manifests/external_repositories.csv', repos)
qdao = Path('external/qdao')
branches = subprocess.check_output(['git','-C',str(qdao),'branch','-a'],text=True)
tags = subprocess.check_output(['git','-C',str(qdao),'tag'],text=True)
note = '# Read-only external sources\n\n' + '\n'.join(f"- {r['repository']} | branch={r['git_branch']} | SHA={r['git_commit']} | clone_date={r['clone_date']} | dirty={r['dirty']}" for r in repos)
note += '\n\nQDAO branches:\n```\n'+branches+'```\nTags:\n```\n'+tags+'```\n'
Path('external/EXTERNAL_SOURCES.md').write_text(note)
Path('results/manifests/external_sources.md').write_text(note)
b = backend()
Path('results/manifests/backend.json').write_text(json.dumps(dict(name=b.name, device='CPU', method='statevector',
    basis_gates=b.configuration().basis_gates, operation_names=sorted(b.operation_names), optimization_level=0,
    physical_backend_qubit_limit=b.num_qubits,static_compiler_target_num_qubits=None,
    static_target_policy='Copy all Aer target operations into Target(num_qubits=None); no simulation at this width'), indent=2))
print('bootstrap checks passed')
