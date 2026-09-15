#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -c "import qiskit, numpy, pandas, scipy; print('env ok')"
pytest -q
python scripts/run_materialization_model.py
python scripts/validate_product_virtualization.py
python scripts/benchmark_fused_materialization.py
python scripts/analyze_materialization_results.py
python scripts/plot_materialization_results.py
python scripts/audit_materialization_results.py
