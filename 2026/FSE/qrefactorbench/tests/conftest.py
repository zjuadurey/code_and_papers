"""Synthetic test fixtures are engineering fixtures, never dataset annotations."""

import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOY_IDS = {"toy-search-001", "toy-optimization-001", "toy-negative-001", "toy-hard-negative-001"}


@pytest.fixture
def draft_case(tmp_path):
    directory = tmp_path / "case"
    shutil.copytree(ROOT / "cases/search/toy_search", directory)
    path = directory / "case.json"
    return path, json.loads(path.read_text())


@pytest.fixture
def reviewed_case(draft_case):
    path, case = draft_case
    case["annotation_status"] = "REVIEWED"
    case["annotators"] = ["fixture-a", "fixture-b"]
    case["admissible_migration_contracts"][0]["status"] = "REVIEWED"
    case["review"] = {"independent_annotations": [
        {"annotator_id": "fixture-a", "artifact": "annotations/a.json"},
        {"annotator_id": "fixture-b", "artifact": "annotations/b.json"}],
        "disagreements": "annotations/differences.json"}
    (path.parent / "annotations").mkdir()
    for name in ("a.json", "b.json", "differences.json", "resolution.json"):
        (path.parent / "annotations" / name).write_text('{"engineering_fixture": true}')
    return path, case
