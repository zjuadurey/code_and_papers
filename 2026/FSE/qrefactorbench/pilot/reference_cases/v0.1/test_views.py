"""Pair identity and fixed allowlist checks, not a claim of localization difficulty."""

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def function_source(path, name):
    source = path.read_text()
    node = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == name)
    return ast.get_source_segment(source, node)


@pytest.mark.parametrize("source,context,function", [
    ("pilot/source_adaptations/v0.1/cases/lit-001/kernel.py", "pilot/context_adaptations/v0.1/cases/context-001/maintenance.py", "maxcut_bruteforce"),
    ("pilot/source_adaptations/v0.1/cases/lit-002/kernel.py", "pilot/reference_cases/v0.1/cases/context-002/inspection.py", "min_vertex_cover_bruteforce"),
])
def test_core_body_is_unchanged_in_context(source, context, function):
    assert function_source(ROOT / source, function) == function_source(ROOT / context, function)


def test_public_export_identity_and_overwrite_refusal(tmp_path):
    command = [sys.executable, str(HERE / "prepare_inputs.py")]
    first, second = tmp_path / "first", tmp_path / "second"
    subprocess.run(command + ["--output", str(first)], check=True, capture_output=True)
    subprocess.run(command + ["--output", str(second)], check=True, capture_output=True)
    entries = {str(p.relative_to(first)): p.read_bytes() for p in first.rglob('*') if p.is_file()}
    assert entries == {str(p.relative_to(second)): p.read_bytes() for p in second.rglob('*') if p.is_file()}
    assert set(entries) == {"manifest.json", "core-001/program.py", "core-001/public_task.json",
                            "core-002/program.py", "core-002/public_task.json", "context-001/program.py",
                            "context-001/maintenance.py", "context-001/public_task.json", "context-002/program.py",
                            "context-002/inspection.py", "context-002/public_task.json"}
    for case_id in ["core-001", "core-002", "context-001", "context-002"]:
        task = json.loads((first / case_id / "public_task.json").read_text())
        assert set(task) == {"case_id", "title", "software_contract", "input_domain", "execution_assumptions"}
        assert task["case_id"] == case_id
    failure = subprocess.run(command + ["--output", str(first)], capture_output=True)
    assert failure.returncode != 0
    assert entries == {str(p.relative_to(first)): p.read_bytes() for p in first.rglob('*') if p.is_file()}


@pytest.mark.parametrize("case_id,function,args,expected", [
    ("lit-001", "maxcut_bruteforce", ([],), (0, ([], []))),
    ("lit-001", "maxcut_bruteforce", ([[0, 2**70], [2**70, 0]],), (2**70, ([0], [1]))),
    ("lit-002", "min_vertex_cover_bruteforce", ([], 0), set()),
    ("lit-002", "min_vertex_cover_bruteforce", ([(0, 1)], 2), {0}),
])
def test_core_public_boundary_examples(case_id, function, args, expected):
    path = ROOT / "pilot/source_adaptations/v0.1/cases" / case_id / "kernel.py"
    spec = importlib.util.spec_from_file_location(case_id.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert getattr(module, function)(*args) == expected
