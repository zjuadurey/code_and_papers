"""Prepare a detached, patchable worktree; never change the reference checkout."""
import _common
from pathlib import Path
import subprocess
root = Path(__file__).resolve().parents[1]
target = root/'build/qdao-qthin-src'
sha = 'fb360e6670b9818a3d4e106fb21cf605838be0a4'
if not target.exists():
    subprocess.run(['git','-C',str(root/'external/qdao'),'worktree','add','--detach',str(target),sha],check=True)
    subprocess.run(['git','-C',str(target),'apply',str(root/'patches/qdao_current_qiskit.patch')],check=True)
assert subprocess.check_output(['git','-C',str(target),'rev-parse','HEAD'],text=True).strip() == sha
actual = subprocess.check_output(['git','-C',str(target),'diff'],text=True)
assert actual == (root/'patches/qdao_current_qiskit.patch').read_text(), 'Unexpected integration-worktree changes'
print('QDAO compatibility worktree verified:',sha)
