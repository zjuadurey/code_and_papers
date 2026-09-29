#!/usr/bin/env bash
# Run from this window's checkout or a verified frozen qrefactorbench snapshot.
set -euo pipefail
window_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ ! -f "$window_root/window-env.sh" ]]; then
    echo "Open the A/B/C worktree first; this source directory is not a task window." >&2
    exit 2
fi
source "$window_root/window-env.sh"
code_root="$window_root/qrefactorbench"
snapshot_path=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --snapshot)
            [[ $# -ge 2 ]] || exit 2
            snapshot_path="$(cd "$2" && pwd)"
            code_root="$snapshot_path/files"
            shift 2 ;;
        --model-lock)
            if [[ "$FSE_WINDOW" != B ]]; then
                echo "Only window B dispatches model experiments." >&2
                exit 2
            fi
            exec 9>"$FSE_LOCKS/model.lock"
            flock -n 9 || { echo "Another model experiment holds the lock." >&2; exit 3; }
            shift ;;
        --compute-lock)
            exec 8>"$FSE_LOCKS/compute.lock"
            flock -n 8 || { echo "Another heavy compute task holds the lock." >&2; exit 3; }
            shift ;;
        --) shift; break ;;
        *) break ;;
    esac
done
[[ $# -gt 0 ]] || { echo "Usage: parallel_run.sh [--snapshot DIR] [--model-lock] [--compute-lock] -- COMMAND ..." >&2; exit 2; }
[[ -f "$code_root/pyproject.toml" && -f "$code_root/qrefactorbench/__init__.py" ]] || exit 2
if [[ -n "$snapshot_path" ]]; then
    "$FSE_PYTHON" -B "$window_root/qrefactorbench/scripts/parallel_snapshot.py" verify "$snapshot_path" >&2
fi
export FSE_CODE_ROOT="$code_root"
export PYTHONPATH="$code_root"
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PATH="$(dirname "$FSE_PYTHON"):$PATH"
export FSE_RUN_DIR
FSE_RUN_DIR="$(mktemp -d "$FSE_RUNTIME/runs/run.XXXXXXXX")"
export TMPDIR="$FSE_RUN_DIR/tmp" XDG_CACHE_HOME="$FSE_RUN_DIR/cache"
mkdir -p "$TMPDIR" "$XDG_CACHE_HOME"
cd "$code_root"
"$FSE_PYTHON" -B - "$snapshot_path" <<'PY'
import hashlib, importlib.metadata, json, os, pathlib, sys
from datetime import datetime, timezone
import qrefactorbench, schemas
root = pathlib.Path(os.environ['FSE_CODE_ROOT']).resolve()
for module in (qrefactorbench, schemas):
    if not pathlib.Path(module.__file__).resolve().is_relative_to(root):
        raise SystemExit(f'Import escaped the selected code root: {module.__name__}')
versions = {}
for name in ('jsonschema', 'referencing', 'pytest', 'qdk', 'qiskit'):
    try:
        versions[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        versions[name] = None
manifest = pathlib.Path(sys.argv[1]) / 'manifest.json' if sys.argv[1] else None
record = {'window': os.environ['FSE_WINDOW'], 'code_root': str(root),
          'python': sys.executable, 'python_version': sys.version,
          'dependency_versions': versions, 'started_at': datetime.now(timezone.utc).isoformat(),
          'snapshot_manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest else None,
          'mode': 'frozen' if manifest else 'development'}
pathlib.Path(os.environ['FSE_RUN_DIR'], 'environment.json').write_text(json.dumps(record, indent=2) + '\n')
PY
echo "Run record: $FSE_RUN_DIR" >&2
exec "$@"
