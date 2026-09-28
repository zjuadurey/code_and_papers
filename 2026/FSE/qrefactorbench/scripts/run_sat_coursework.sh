#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
study_python="${CA6000_PYTHON:-$HOME/miniconda3/envs/palqo/bin/python}"
if [[ ! -x "$study_python" ]]; then study_python="${CA6000_PYTHON:-python}"; fi
export PYTHONDONTWRITEBYTECODE=1
exec "$study_python" -m coursework.sat_case_study.train "$@"
