import subprocess
import sys

import pytest

from qrefactorbench.evaluator.execution import check_imports, check_interface, check_syntax, run_trusted_python
from qrefactorbench.evaluator.resources import check_resource_limits
from qrefactorbench.evaluator.semantics import SemanticOracles

from conftest import ROOT


def test_syntax_does_not_execute(tmp_path):
    marker = tmp_path / "must_not_exist"
    source = f"open({str(marker)!r}, 'w').write('bad')\n"
    assert check_syntax({"a.py": source}).passed is True
    assert not marker.exists()
    assert check_syntax({"a.py": "def broken(:"}).passed is False
    assert check_syntax({"a.py": "return 1"}).passed is False
    assert check_syntax({}).passed is None


def test_trusted_execution_import_failure_and_timeout(tmp_path):
    assert run_trusted_python(["-c", "raise RuntimeError"], cwd=tmp_path).passed is None
    assert run_trusted_python(["-c", "pass"], cwd=tmp_path, trusted=True).passed is True
    assert run_trusted_python(["-c", "raise RuntimeError"], cwd=tmp_path, trusted=True).passed is False
    assert run_trusted_python(["-c", "import time; time.sleep(2)"], cwd=tmp_path, trusted=True, timeout=0.05).passed is False
    (tmp_path / "module.py").write_text("import missing_fixture_module\n")
    assert check_imports("module", cwd=tmp_path, trusted=True).passed is False


def test_static_interfaces():
    reference = "def solve(a, *, mode=1):\n    return a\n"
    assert check_interface(reference, reference.replace("return a", "return None"), ["solve"]).passed is True
    assert check_interface(reference, "def solve(a): pass", ["solve"]).passed is False
    assert check_interface(reference, reference, []).passed is None
    assert check_interface(reference, reference, ["missing"]).passed is None


def test_semantic_hooks_and_objective_thresholds():
    oracles = SemanticOracles()
    assert oracles.evaluate(None, 1).passed is None
    assert oracles.evaluate({"kind": "deterministic_equality", "config": {"expected": [1, 2]}}, [1, 2]).passed is True
    assert oracles.evaluate({"kind": "deterministic_equality", "config": {"expected": 2}}, 3).passed is False
    assert oracles.evaluate({"kind": "deterministic_equality", "config": {}}, 1).passed is None
    quality = {"kind": "optimization_objective", "config": {"direction": "minimize"}}
    assert oracles.evaluate(quality, 1).passed is None
    quality["config"]["threshold"] = 2
    assert oracles.evaluate(quality, 1).passed is True
    assert oracles.evaluate(quality, 3).passed is False
    assert oracles.evaluate(quality, float("nan")).passed is False
    for kind in ("property", "optimization_feasibility", "probabilistic"):
        assert oracles.evaluate({"kind": kind, "config": {}}, 1).passed is None
    oracles.register("feasible", lambda output, config: all(bit in {0, 1} for bit in output))
    assert oracles.evaluate({"kind": "optimization_feasibility", "hook_id": "feasible", "config": {}}, [1, 2]).passed is False
    with pytest.raises(ValueError):
        oracles.register("feasible", lambda output, config: True)
    oracles.register("broken", lambda output, config: 1 / 0)
    result = oracles.evaluate({"kind": "property", "hook_id": "broken", "config": {}}, 1)
    assert result.passed is None
    assert "infrastructure error" in result.reason


def test_resource_checks_require_measured_and_annotated_values():
    assert check_resource_limits(None, {"limits": {"depth": 5}}).passed is None
    assert check_resource_limits({"depth": 3}, {"limits": {}}).passed is None
    assert check_resource_limits({"depth": 3}, {"limits": {"depth": 5}}).passed is True
    assert check_resource_limits({"depth": 6}, {"limits": {"depth": 5, "shots": 100}}).passed is False
    assert check_resource_limits({"depth": 3}, {"limits": {"depth": 5, "shots": 100}}).passed is None


@pytest.mark.parametrize("directory", ["search/toy_search", "optimization/toy_max_cut", "negatives/toy_normalize", "negatives/toy_audit"])
def test_classical_toy_tests_in_separate_processes(directory):
    # These are repository-owned toy tests, not arbitrary benchmark submissions.
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_program.py"],
                            cwd=ROOT / "cases" / directory, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
