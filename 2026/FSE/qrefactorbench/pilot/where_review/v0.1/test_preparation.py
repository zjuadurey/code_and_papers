"""Isolation, condition comparability, evidence and existing-format regressions."""

import ast
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("where_preparation", HERE / "prepare.py")
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)


@pytest.fixture(scope="module")
def prepared(tmp_path_factory):
    output = tmp_path_factory.mktemp("where") / "derived"
    prep.build(output)
    return output


def test_only_location_cue_differs_between_b_and_c(prepared):
    manifest = json.loads((prepared / "manifest.json").read_text())
    assert manifest["model_calls"] == 0
    assert len(manifest["conditions"]) == 6
    for case in prep.VIEWS:
        b = (prepared / "inputs" / f"{case}-B.txt").read_text()
        c = (prepared / "inputs" / f"{case}-C.txt").read_text()
        prefix, hint = b.split(prep.HINT_MARKER)
        assert prefix == c
        assert json.loads(hint) == prep.HINTS[case]
        assert prep.HINT_MARKER not in c
        assert (prepared / "inputs" / f"{case}-A.txt").read_text().startswith((HERE / "TASK.md").read_text())
    assert {row["prediction_case_id"] for row in manifest["conditions"]} == {
        "source-core-003", "source-core-004", "lit-003", "lit-004"}


def test_public_files_are_explicit_and_unchanged(prepared):
    allowed_keys = {"case_id", "title", "software_contract", "input_domain", "execution_assumptions"}
    for row in json.loads((prepared / "manifest.json").read_text())["conditions"]:
        data = (prepared / row["path"]).read_bytes()
        assert prep.digest(data) == row["sha256"]
        message = data.decode()
        for forbidden in ("FILE case.json", "FILE test_program.py", "AI-ASSISTED PROPOSAL", "WHERE_REVIEW", "annotation_assist", "example_report", "PRIVATE_REVIEW"):
            assert forbidden not in message
        view = row["prediction_case_id"]
        public = json.loads((prep.PUBLIC / view / "public_task.json").read_text())
        assert set(public) == allowed_keys
        assert (prep.PUBLIC / view / "public_task.json").read_text() in message
        assert (prep.PUBLIC / view / "NOTICE.txt").read_text() in message
        for source in (prep.PUBLIC / view).glob("*.py"):
            numbered = "\n".join(f"{i}: {line}" for i, line in enumerate(source.read_text().splitlines(), 1))
            assert numbered in message
        for name in prep.SCHEMAS:
            assert (prep.ROOT / f"schemas/{name}.schema.json").read_text() in message


def test_hint_anchors_are_actual_syntactic_regions():
    hint = prep.HINTS["lit-003"]
    tree = ast.parse((prep.PUBLIC / "lit-003" / hint["file"]).read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "complete")
    assert (node.lineno, node.end_lineno) == (hint["start_line"], hint["end_line"])
    hint = prep.HINTS["lit-004"]
    tree = ast.parse((prep.PUBLIC / "lit-004" / hint["file"]).read_text())
    loop = next(n for n in ast.walk(tree) if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == "mask")
    assert (loop.lineno - 1, loop.end_lineno) == (hint["start_line"], hint["end_line"])


def test_classical_witnesses_separate_paths_and_output_obligations(prepared):
    agenda = {r["id"]: r for r in json.loads((prepared / "evidence/lit-003.json").read_text())}
    cohort = {r["id"]: r for r in json.loads((prepared / "evidence/lit-004.json").read_text())}
    assert len(agenda) + len(cohort) == 13
    assert agenda["completion_after_blocked_preview"]["calls"] == {"preview": 1, "complete": 1}
    for name in ("inspection", "retain_valid_current"):
        assert agenda[name]["calls"] == {"preview": 0, "complete": 0}
    assert agenda["ready_preview"]["calls"]["complete"] == 0
    assert agenda["no_arrangement"]["report"]["status"] == "unavailable"
    assert cohort["inspection_only"]["calls"]["compatible"] == 0
    assert cohort["selection_only"]["calls"]["compatible"] == 16
    assert cohort["numeric_mask_tie"]["report"]["requests"][0]["proposed"]["selected"] == ["b", "c"]
    for record in (agenda["replace_preview_with_completion"], cohort["replace_preview_with_largest_group"]):
        assert record["same_final_proposal"]
        assert record["changed_fields"]
        assert all("proposed" not in field for field in record["changed_fields"])


def test_existing_output_is_not_overwritten(prepared):
    before = (prepared / "manifest.json").read_bytes()
    with pytest.raises(FileExistsError):
        prep.build(prepared)
    assert (prepared / "manifest.json").read_bytes() == before


def test_existing_prediction_format_can_retain_review_evidence():
    from qrefactorbench.schema import schema_errors
    # Mechanical dummy, not a model output, scientific prediction or case annotation.
    dummy = {"schema_version": "0.2.0", "case_id": "lit-003", "decision": "REMAIN_CLASSICAL",
             "candidate_regions": [dict(prep.HINTS["lit-003"], function="complete")],
             "migration_family": None, "plan": None, "rationale": "DUMMY boundary evidence, not scored",
             "structural_eligibility": None, "practical_suitability": None, "benchmark_supported": None,
             "computational_intent": None, "assumptions": [], "risks": [], "contract_applicability": []}
    assert not schema_errors(dummy, "prediction")
