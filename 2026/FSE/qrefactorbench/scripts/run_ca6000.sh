#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ca_python="${CA6000_PYTHON:-$HOME/miniconda3/envs/palqo/bin/python}"
if [[ ! -x "$ca_python" ]]; then ca_python="${CA6000_PYTHON:-python}"; fi
export PYTHONDONTWRITEBYTECODE=1
exec "$ca_python" -m coursework.ca6000.train "$@"
