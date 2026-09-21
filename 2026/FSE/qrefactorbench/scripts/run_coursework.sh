#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
demo_python="${QREFACTOR_DEMO_PYTHON:-$HOME/miniconda3/envs/htp-static/bin/python}"
if [[ ! -x "$demo_python" ]]; then demo_python="${QREFACTOR_DEMO_PYTHON:-python}"; fi
export PYTHONDONTWRITEBYTECODE=1
exec "$demo_python" -m coursework.app "$@"
