"""Source pairing, isolated public inputs and additional core-domain checks."""

import ast
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def body(path, name):
    source = path.read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, node)


@pytest.mark.parametrize("source,context,name", [
    ("cases/pilot/pilot-007/program.py", "cases/context-005/lots.py", "has_total"),
    ("cases/pilot/pilot-006/program.py", "cases/context-006/packages.py", "minimum_energy"),
    ("pilot/reference_cases/v0.3/cores/core-007.py", "cases/context-007/archive.py", "select_items"),
    ("cases/pilot/pilot-008/program.py", "cases/context-008/exports.py", "materialize"),
])
def test_core_function_unchanged(source, context, name):
    assert body(ROOT / source, name) == body(HERE / context, name)


def test_reproducible_allowlist_prior_eight_views_and_no_obvious_label_cues(tmp_path):
    exporter = module(HERE / "prepare_inputs.py", "export_v03_test")
    first, second = tmp_path / "first", tmp_path / "second"
    exporter.prepare(first)
    exporter.prepare(second)
    files = lambda root: {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert files(first) == files(second) == files(HERE / "review_inputs")
    assert len(exporter.PACKETS) == 16
    expected = {"manifest.json"} | {f"{case_id}/{name}" for case_id, paths in exporter.PACKETS.items() for name in paths}
    assert set(files(first)) == expected and len(expected) == 41
    old = HERE.parent / "v0.2/review_inputs"
    for path in old.rglob('*'):
        if path.is_file() and path.name != "manifest.json":
            assert path.read_bytes() == (first / path.relative_to(old)).read_bytes()
    cue = re.compile(r"\b(qaoa|grover|qubo|quantum|candidate_region|structural_eligibility)\b|\b(positive|negative)\s+(case|example|label)\b", re.I)
    for case_id in exporter.PACKETS:
        task = json.loads((first / case_id / "public_task.json").read_text())
        assert set(task) == exporter.PUBLIC_KEYS
        assert not cue.search(json.dumps(task))
    before = files(first)
    with pytest.raises(FileExistsError):
        exporter.prepare(first)
    assert files(first) == before


def test_new_exported_contexts_run_without_private_materials(tmp_path):
    public = tmp_path / "inputs"
    module(HERE / "prepare_inputs.py", "export_standalone").prepare(public)
    for number in range(5, 9):
        case_id = f"context-{number:03}"
        request = (HERE / "cases" / case_id / "example_request.json").read_text()
        command = [sys.executable, str(public / case_id / "program.py")]
        result = subprocess.run(command, input=request, text=True, capture_output=True, check=True, cwd=tmp_path)
        expected = json.loads((HERE / "cases" / case_id / "example_report.json").read_text())
        assert json.loads(result.stdout) == expected
        failure = subprocess.run(command, input='{}', text=True, capture_output=True, cwd=tmp_path)
        assert failure.returncode != 0 and not failure.stdout.strip()


def test_index_provenance_hashes_and_unassigned_science():
    index = json.loads((HERE / "PAIR_INDEX.json").read_text())
    assert index["problem_lineages"] == 8 and index["public_views"] == 16
    public_ids = []
    for pair in index["pairs"]:
        for view in pair["views"]:
            public_ids.append(view["public_id"])
            for name, source in view["source_paths"].items():
                assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == view["files_sha256"][name]
    assert len(set(public_ids)) == 16
    for path in (HERE / "cases").glob('*/case.json'):
        case = json.loads(path.read_text())
        assert case["annotation_status"] == "DRAFT" and case["annotators"] == []
        for key in ("structural_eligibility", "practical_suitability", "benchmark_supported", "expected_decision",
                    "computational_intent", "migration_family", "reference_plan"):
            assert case[key] is None


def test_signed_core_total_domain_not_just_positive_context():
    core = module(ROOT / "cases/pilot/pilot-007/program.py", "core_total")
    for n in range(5):
        for values in product((-2, 0, 3), repeat=n):
            sums = {sum(subset) for k in range(n+1) for subset in combinations(values, k)}
            for target in range(-9, 14):
                assert core.has_total(list(values), target) == (target in sums)


def test_core_self_couplings_and_repeated_edges():
    core = module(ROOT / "cases/pilot/pilot-006/program.py", "core_energy")
    biases = [2, -1]
    couplings = [(0, 0, -5), (1, 0, 2), (0, 1, -3), (0, 1, -3)]
    assert core.minimum_energy(biases, couplings) == min(2*a-b-5*a+2*b*a-6*a*b for a, b in product((0, 1), repeat=2))
    assert core.minimum_energy([], []) == 0


def test_core_ragged_rows_and_aliases():
    core = module(ROOT / "cases/pilot/pilot-008/program.py", "core_rows")
    rows = [[], [0], [3, -2, 1]]
    output = core.materialize(rows, 2)
    expected = [[], [], [0.0], [0.0], [float(Fraction(v, 6)) for v in rows[2]], [float(Fraction(v, 6)) for v in rows[2]]]
    assert output == expected and len({id(row) for row in output}) == 6
    output[4][0] = 999
    assert output[5] == expected[5] and rows[2] == [3, -2, 1]
