import json
import shutil

import pytest
from jsonschema import Draft202012Validator

from qrefactorbench.schema import documents, schema_errors
from qrefactorbench.validator import validate_case, validate_dataset

from conftest import ROOT


def errors(path, case):
    return [i.message for i in validate_case(path, case) if i.severity == "error"]


def test_schema_documents_and_seed_dataset():
    for schema in documents().values():
        Draft202012Validator.check_schema(schema)
    report = validate_dataset(ROOT / "cases")
    assert report.valid
    assert len(report.cases) == 14
    assert {c["annotation_status"] for _, c in report.cases} == {"DRAFT"}
    assert len(report.issues) == 14


def test_templates_are_valid_drafts():
    report = validate_dataset(ROOT / "templates")
    assert report.valid
    assert len(report.cases) == 3


@pytest.mark.parametrize("field,value", [
    ("migration_family", "unknown_family"), ("context_level", "repository"),
    ("structural_eligibility", "true"), ("candidate_regions", []),
    ("practical_suitability", False), ("schema_version", "99.0.0"),
    ("expected_decision", "REMAIN_CLASSICAL"), ("quantumizable", True),
])
def test_invalid_labels_and_contradictions(draft_case, field, value):
    path, case = draft_case
    case[field] = value
    assert errors(path, case)


def test_unknown_draft_labels_are_distinct_from_false(draft_case):
    path, case = draft_case
    for field in ("structural_eligibility", "practical_suitability", "benchmark_supported", "expected_decision"):
        case[field] = None
    assert not errors(path, case)


@pytest.mark.parametrize("relative", ["../outside.py", "/tmp/outside.py", "C:\\outside.py", "x/../../z.py", "./program.py"])
def test_invalid_paths(draft_case, relative):
    path, case = draft_case
    case["classical_program"] = relative
    assert errors(path, case)


def test_symlink_escape(draft_case, tmp_path):
    path, case = draft_case
    target = tmp_path / "outside.py"
    target.write_text("pass\n")
    (path.parent / "escape.py").symlink_to(target)
    case["classical_program"] = "escape.py"
    case["candidate_regions"][0]["file"] = "escape.py"
    assert any("escapes" in e for e in errors(path, case))


@pytest.mark.parametrize("patch", [
    {"start_line": 0}, {"end_line": 999}, {"start_line": 3, "end_line": 1},
    {"file": "missing.py"}, {"function": "wrong"},
])
def test_invalid_regions(draft_case, patch):
    path, case = draft_case
    case["candidate_regions"][0].update(patch)
    assert errors(path, case)


def test_duplicate_case_ids(draft_case, tmp_path):
    path, _ = draft_case
    shutil.copytree(path.parent, tmp_path / "duplicate")
    report = validate_dataset(tmp_path)
    assert not report.valid
    assert any("Duplicate case_id" in i.message for i in report.issues)


@pytest.mark.parametrize("status", ["REVIEWED", "ADJUDICATED", "FROZEN"])
def test_maturity_requires_evidence(draft_case, status):
    path, case = draft_case
    case["annotation_status"] = status
    assert errors(path, case)


def test_reviewed_to_frozen_evidence(reviewed_case):
    path, case = reviewed_case
    assert not errors(path, case)
    case["annotation_status"] = "ADJUDICATED"
    assert errors(path, case)
    case["review"].update(adjudicator_id="fixture-a", resolution="annotations/resolution.json")
    assert not errors(path, case)
    case["annotation_status"] = "FROZEN"
    assert errors(path, case)
    case["benchmark_release"] = "fixture-release-only"
    assert errors(path, case)  # unresolved licensing
    case["license"] = "fixture-license-only"
    assert not errors(path, case)


@pytest.mark.parametrize("field", ["semantic_oracle", "resource_expectations", "annotation_rationale", "computational_intent"])
def test_reviewed_cannot_omit_required_annotations(reviewed_case, field):
    path, case = reviewed_case
    case[field] = None
    assert errors(path, case)


def test_independent_annotation_records(reviewed_case):
    path, case = reviewed_case
    case["review"]["independent_annotations"][1]["annotator_id"] = "fixture-a"
    assert any("distinct annotators" in e for e in errors(path, case))


@pytest.mark.parametrize("oracle", [
    {"kind": "deterministic_equality", "description": "fixture", "config": {}},
    {"kind": "optimization_objective", "description": "fixture", "config": {"direction": "maximize"}},
    {"kind": "property", "description": "fixture", "config": {}},
])
def test_reviewed_oracles_require_explicit_configuration(reviewed_case, oracle):
    path, case = reviewed_case
    case["semantic_oracle"] = oracle
    assert errors(path, case)


def test_null_byte_artifact_is_an_error_not_a_crash(draft_case):
    path, case = draft_case
    case["classical_program"] = "bad\x00.py"
    case["candidate_regions"][0]["file"] = "bad\x00.py"
    assert errors(path, case)


def test_multiple_contracts_and_bad_reference(draft_case):
    path, case = draft_case
    alternative = dict(case["admissible_migration_contracts"][0], contract_id="fixture-alternative")
    case["admissible_migration_contracts"].append(alternative)
    assert not errors(path, case)
    case["reference_plan"]["contract_id"] = "absent"
    assert any("undeclared contract" in e for e in errors(path, case))


def test_missing_artifact_and_syntax(draft_case):
    path, case = draft_case
    (path.parent / "program.py").write_text("def broken(:\n")
    assert errors(path, case)
    (path.parent / "program.py").unlink()
    assert errors(path, case)


def test_empty_and_malformed_dataset(tmp_path):
    assert not validate_dataset(tmp_path).valid
    (tmp_path / "case.json").write_text('{"case_id":')
    assert not validate_dataset(tmp_path).valid
    (tmp_path / "case.json").write_text('[]')
    assert not validate_dataset(tmp_path).valid


def test_prediction_schema_has_abstention_and_multiple_contract_plan(draft_case):
    _, case = draft_case
    p = {"schema_version": "0.1.0", "case_id": case["case_id"], "decision": "REMAIN_CLASSICAL", "candidate_regions": []}
    assert schema_errors(p, "prediction") == []
    p["decision"] = "QUANTUMIZE"
    assert schema_errors(p, "prediction")
    p.update(candidate_regions=case["candidate_regions"], plan=case["reference_plan"])
    assert schema_errors(p, "prediction") == []
