"""Verify reused source identities and the public/private boundary."""

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def body(path, name):
    source = path.read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, node)


@pytest.mark.parametrize("source,context,name", [
    ("cases/pilot/pilot-001/program.py", "cases/context-003/configurations.py", "satisfies"),
    ("cases/pilot/pilot-001/program.py", "cases/context-003/configurations.py", "has_assignment"),
    ("cases/pilot/pilot-002/program.py", "cases/context-004/records.py", "ledger_digest"),
])
def test_source_functions_unchanged(source, context, name):
    assert body(ROOT / source, name) == body(HERE / context, name)


def test_export_is_allowlisted_reproducible_and_previous_views_unchanged(tmp_path):
    spec = importlib.util.spec_from_file_location("export_v02_test", HERE / "prepare_inputs.py")
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    first, second = tmp_path / "one", tmp_path / "two"
    exporter.prepare(first)
    exporter.prepare(second)
    actual = {str(p.relative_to(first)): p.read_bytes() for p in first.rglob('*') if p.is_file()}
    assert actual == {str(p.relative_to(second)): p.read_bytes() for p in second.rglob('*') if p.is_file()}
    expected = {"manifest.json"} | {f"{case_id}/{name}" for case_id, files in exporter.PACKETS.items() for name in files}
    assert set(actual) == expected and len(actual) == 21
    for case_id in ["core-001", "core-002", "context-001", "context-002"]:
        for path in (HERE.parent / "v0.1/review_inputs" / case_id).iterdir():
            assert path.read_bytes() == (first / case_id / path.name).read_bytes()
    for case_id in exporter.PACKETS:
        task = json.loads((first / case_id / "public_task.json").read_text())
        assert set(task) == exporter.previous.PUBLIC_KEYS
    with pytest.raises(FileExistsError):
        exporter.prepare(first)
    assert actual == {str(p.relative_to(first)): p.read_bytes() for p in first.rglob('*') if p.is_file()}


def test_exported_programs_are_standalone(tmp_path):
    public = tmp_path / "public"
    subprocess.run([sys.executable, str(HERE / "prepare_inputs.py"), "--output", str(public)], check=True, capture_output=True)
    for case_id in ["context-003", "context-004"]:
        request = (HERE / "cases" / case_id / "example_request.json").read_text()
        command = [sys.executable, str(public / case_id / "program.py")]
        output = subprocess.run(command, input=request, text=True, capture_output=True, check=True, cwd=tmp_path)
        expected = json.loads((HERE / "cases" / case_id / "example_report.json").read_text())
        assert json.loads(output.stdout) == expected
