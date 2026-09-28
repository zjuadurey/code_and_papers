"""Source selection is behavior-reviewed; imported code is not treated as gold."""

import ast
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source(number):
    return load(HERE / f"sources/row-{number}.kernel.py", f"source_{number}")


def capture(function, *args):
    try:
        return function(*args)
    except ValueError:
        return "ValueError"


def test_agenda_adaptations_agree_with_pinned_sources_on_all_small_graphs():
    adapted = load(HERE / "cases/lit-003/agenda.py", "adapted_agenda")
    quick = source(97).greedy_kcolor_adj_matrix
    complete = source(98).kcolor_backtracking
    for n in range(5):
        pairs = list(combinations(range(n), 2))
        for flags in product((False, True), repeat=len(pairs)):
            edges = {p for p, flag in zip(pairs, flags) if flag}
            matrix = [[int(tuple(sorted((u, v))) in edges) for v in range(n)] for u in range(n)]
            neighbors = {i: [j for j, v in enumerate(row) if v] for i, row in enumerate(matrix)}
            for k in range(4):
                assert capture(adapted.preview, matrix, k) == capture(quick, matrix, k)
                assert capture(adapted.complete, neighbors, k) == capture(complete, neighbors, k)


def test_release_preview_and_inline_selection_match_pinned_sources():
    quick, exact = source(88).clique_greedy, source(93).clique_bitmask
    versions, checks, requests, expected = [], [], [], []
    for n in range(5):
        pairs = list(combinations(range(n), 2))
        for flags in product((False, True), repeat=len(pairs)):
            edges = [pair for pair, flag in zip(pairs, flags) if flag]
            prefix = str(len(requests))
            names = [f"{prefix}-{i}" for i in range(n)]
            versions.extend({"version_id": name, "active": True} for name in names)
            checks.extend({"left": names[u], "right": names[v], "passed": True} for u, v in edges)
            requests.append({"request_id": prefix, "members": names, "current": [], "mode": "select"})
            expected.append(([names[i] for i in sorted(quick(n, edges))], [names[i] for i in exact(n, edges)]))
    run = subprocess.run([sys.executable, str(HERE / "cases/lit-004/program.py")],
                         input=json.dumps({"versions": versions, "checks": checks, "requests": requests}),
                         text=True, capture_output=True, check=True)
    for report, (preview, proposed) in zip(json.loads(run.stdout)["requests"], expected):
        assert report["preview"]["selected"] == preview
        assert report["proposed"]["selected"] == proposed


def test_source_selection_counterexamples_are_preserved_not_repaired():
    # These snippets do not satisfy the desired total-domain maximum/minimum contract.
    assert source(87).clique_brute_force(1, []) == []  # Singleton is omitted.
    assert source(388).min_vertex_cover_bruteforce(1, []) == {0}  # Empty is smaller.
    assert source(431).min_vertex_cover_bnb([], 1) == {0}  # Starts at cardinality one.
    assert source(431).min_vertex_cover_bnb([], 0) is None


def test_alternative_reviewed_sources_have_different_success_policies():
    edges = [(0, 2), (2, 3), (1, 3)]
    neighbors = {i: [v if u == i else u for u, v in edges if i in (u, v)] for i in range(4)}
    assert source(101).kcolor_backtrack_partial(neighbors, 2) == {0: 0, 1: 1, 2: 1, 3: 0}
    with pytest.raises(ValueError):
        source(103).kcolor_with_color_sets(neighbors, 2)
    assert source(94).clique_backtracking(4, [(1, 2), (1, 3), (2, 3)]) == [1, 2, 3]


def test_source_evidence_and_core_view_functions_are_byte_identical():
    manifest = json.loads((HERE / "sources/manifest.json").read_text())
    assert manifest["row_count"] == 434
    assert len(manifest["selection"]) == 10
    for path, expected in manifest["files_sha256"].items():
        assert hashlib.sha256((HERE / "sources" / path).read_bytes()).hexdigest() == expected
    for case_id, numbers in (("source-core-003", (97, 98)), ("source-core-004", (88, 93))):
        exported = (HERE / "cores" / case_id / "program.py").read_text()
        bodies = {node.name: ast.get_source_segment(exported, node) for node in ast.parse(exported).body if isinstance(node, ast.FunctionDef)}
        for number in numbers:
            original = (HERE / f"sources/row-{number}.kernel.py").read_text()
            for node in ast.parse(original).body:
                if isinstance(node, ast.FunctionDef):
                    assert bodies[node.name] == ast.get_source_segment(original, node)


def test_allowlist_regeneration_and_standalone_execution(tmp_path):
    exporter = load(HERE / "prepare_inputs.py", "source_where_exporter")
    out = tmp_path / "public"
    exporter.prepare(out)
    def files(root):
        return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert files(out) == files(HERE / "review_inputs")
    expected = {"manifest.json"} | {f"{case_id}/{name}" for case_id, paths in exporter.PACKETS.items() for name in paths}
    assert set(files(out)) == expected and len(expected) == 17
    for case_id in exporter.PACKETS:
        task = json.loads((out / case_id / "public_task.json").read_text())
        assert set(task) == exporter.PUBLIC_KEYS
        for forbidden in ("candidate_regions", "reference_plan", "structural_eligibility", "practical_suitability", "annotation_status"):
            assert forbidden not in task
    for case_id in ("lit-003", "lit-004"):
        data = (HERE / "cases" / case_id / "example_request.json").read_text()
        run = subprocess.run([sys.executable, "-B", str(out / case_id / "program.py")], input=data,
                             text=True, capture_output=True, check=True, cwd=tmp_path)
        assert json.loads(run.stdout) == json.loads((HERE / "cases" / case_id / "example_report.json").read_text())
        bad = subprocess.run([sys.executable, "-B", str(out / case_id / "program.py")], input='{}', text=True,
                             capture_output=True, cwd=tmp_path)
        assert bad.returncode != 0 and not bad.stdout.strip()
    with pytest.raises(FileExistsError):
        exporter.prepare(out)
    assert files(out) == files(HERE / "review_inputs")
