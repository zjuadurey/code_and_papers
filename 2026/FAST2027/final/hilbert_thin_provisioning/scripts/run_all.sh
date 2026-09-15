#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/bootstrap_check.py
pytest -q
python scripts/discover_workloads.py "$@"
python scripts/run_characterization.py
python scripts/validate_small_exact.py
python scripts/analyze_results.py
python scripts/plot_results.py
python scripts/audit_artifacts.py
