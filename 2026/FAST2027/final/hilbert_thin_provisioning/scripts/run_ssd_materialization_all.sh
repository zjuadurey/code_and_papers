#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v conda >/dev/null 2>&1; then
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
else
  source "$(conda info --base)/etc/profile.d/conda.sh"
fi
conda activate htp-static
python scripts/probe_storage_environment.py
python scripts/build_ssd_materialization.py
pytest -q --junitxml=results/ssd_materialization/logs/pytest.xml
python scripts/validate_ssd_materialization.py
python scripts/run_ssd_materialization.py
python scripts/analyze_ssd_materialization.py
