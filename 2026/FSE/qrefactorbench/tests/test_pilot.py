"""Pilot workflow tests use synthetic predictions, never reported model results."""

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter

import pytest

from qrefactorbench.cli import compare_annotations, evaluate, main
from qrefactorbench.evaluator.pipeline import evaluate_static, prediction_errors
from qrefactorbench.loader import DataError, load_document
from qrefactorbench.pilot import collect_predictions, prepare_packets
from qrefactorbench.schema import schema_errors
from qrefactorbench.validator import validate_dataset

from conftest import ROOT


def response(case_id):
    return {"schema_version": "0.2.0", "case_id": case_id, "decision": "REMAIN_CLASSICAL",
            "candidate_regions": [], "structural_eligibility": None, "practical_suitability": None,
            "benchmark_supported": None, "computational_intent": None, "migration_family": None,
            "contract_applicability": [], "assumptions": [], "risks": [],
            "rationale": "Engineering fixture only; not a model response", "plan": None}


def test_pilot_composition_and_unknown_evidence():
    manifest = load_document(ROOT / "pilot/seed_manifest.json")
    assert Counter(c["proposed_category"] for c in manifest["cases"]) == {
        "search_positive": 2, "optimization_positive": 2, "context_positive": 2,
        "hard_negative": 2, "unsuitable_structural": 2}
    report = validate_dataset(ROOT / "cases/pilot")
    assert report.valid and len(report.cases) == 10
    assert {c["case_id"] for _, c in report.cases} == {c["case_id"] for c in manifest["cases"]}
    for _, case in report.cases:
        assert case["annotation_status"] == "DRAFT" and case["annotators"] == []
        assert "Codex" in case["source"] and case["source_url"] is None
        assert case["license"] == "NOASSERTION"
        if case["case_type"] == "positive":
            assert case["practical_suitability"] is None
            assert case["benchmark_supported"] is None
            assert case["expected_decision"] is None


@pytest.mark.parametrize("number", range(1, 11))
def test_pilot_classical_regressions(number):
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_program.py"],
                            cwd=ROOT / f"cases/pilot/pilot-{number:03d}", capture_output=True,
                            text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr


def test_phase1_schema_requires_separate_scientific_labels():
    p = response("pilot-001")
    assert schema_errors(p, "prediction") == []
    del p["practical_suitability"]
    assert schema_errors(p, "prediction")
    p["practical_suitability"] = "unknown"
    assert schema_errors(p, "prediction")
    p["practical_suitability"] = None
    p["migration_family"] = "unsupported_family"
    assert schema_errors(p, "prediction")


def test_phase1_quantumize_requires_plan_and_region():
    case = load_document(ROOT / "cases/pilot/pilot-001/case.json")
    p = response(case["case_id"])
    p["decision"] = "QUANTUMIZE"
    assert schema_errors(p, "prediction")
    p.update(candidate_regions=case["candidate_regions"], plan=case["reference_plan"], migration_family=case["migration_family"])
    assert not schema_errors(p, "prediction")


def test_recognition_on_abstention_preserves_unknown_and_free_text():
    case = load_document(ROOT / "cases/pilot/pilot-004/case.json")
    p = response(case["case_id"])
    p.update(structural_eligibility=True, practical_suitability=False, computational_intent="Membership among up to eight codes",
             migration_family="unstructured_search", plan=copy.deepcopy(case["reference_plan"]))
    p["plan"]["computational_intent_id"] = "model_chosen_label_not_the_private_id"
    result = evaluate_static(case, p)
    assert result["recognition"]["structural_eligibility"]["correct"] is True
    assert result["recognition"]["practical_suitability"]["correct"] is True
    assert result["recognition"]["benchmark_supported"]["correct"] is None
    assert result["recognition"]["intent"]["correct"] is None
    assert result["planning"]["computational_intent_correct"] is None
    assert result["planning"]["contract_membership"] is True
    assert result["planning"]["admissible_plan"] is None
    assert result["prediction"] == p and result["abstention_correct"] is True


def test_packet_exports_do_not_leak_private_annotation(tmp_path):
    repository = tmp_path / "repo"
    shutil.copytree(ROOT / "cases/pilot", repository / "cases/pilot")
    shutil.copytree(ROOT / "pilot/annotation", repository / "pilot/annotation")
    shutil.copytree(ROOT / "pilot/baseline", repository / "pilot/baseline")
    shutil.copy(ROOT / "pilot/public_contracts.json", repository / "pilot/public_contracts.json")
    private_path = repository / "cases/pilot/pilot-001/case.json"
    case = load_document(private_path)
    secret = "PRIVATE_SENTINEL_NOT_FOR_ANNOTATORS"
    case["annotation_rationale"] = secret
    case["title"] = secret
    case["reference_plan"]["rationale"] = secret
    private_path.write_text(json.dumps(case))
    public_path = private_path.parent / "public_task.json"
    task = load_document(public_path)
    task["draft_reference"] = secret
    public_path.write_text(json.dumps(task))
    output = tmp_path / "packet"
    assert prepare_packets(repository, output)["case_count"] == 10
    for role in ("annotator_a", "annotator_b", "baseline"):
        for path in (output / role).rglob("*"):
            if path.is_file():
                assert secret not in path.read_text()
                assert path.name not in {"case.json", "CURATOR_NOTES.md", "test_program.py"}
    for role in ("annotator_a", "annotator_b"):
        form = load_document(output / role / "pilot-001/annotation.json")
        assert form["candidate_regions"] is None and form["annotator_id"] is None
        assert form["completion_status"] == "UNFILLED"
        assert form["structural_eligibility"] is None and form["expected_decision"] is None
    assert (output / "annotator_a/pilot-005/program.py").read_bytes() == (ROOT / "cases/pilot/pilot-005/program.py").read_bytes()
    assert (output / "annotator_a/contracts.json").read_bytes() == (output / "annotator_b/contracts.json").read_bytes()
    assert "{{" not in (output / "baseline/prompts/pilot-001.md").read_text()
    with pytest.raises(DataError, match="already exists"):
        prepare_packets(repository, output)


def test_committed_packet_hashes_and_source_coordinates():
    for role in ("annotator_a", "annotator_b", "adjudication", "baseline"):
        directory = ROOT / "pilot/packets" / role
        manifest = load_document(directory / "packet_manifest.json")
        assert len(manifest["case_ids"]) == 10
        for name, digest in manifest["files_sha256"].items():
            assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    for path, case in validate_dataset(ROOT / "cases/pilot").cases:
        for file in case.get("files", ["program.py"]):
            assert (path.parent / file).read_bytes() == (ROOT / "pilot/packets/annotator_a" / case["case_id"] / file).read_bytes()


def test_collector_preserves_responses_and_evaluation_coverage(tmp_path):
    responses = tmp_path / "responses"
    responses.mkdir()
    originals = []
    for n in range(1, 11):
        p = response(f"pilot-{n:03d}")
        originals.append(p)
        (responses / f"pilot-{n:03d}.json").write_text(json.dumps(p))
    output = tmp_path / "predictions.json"
    assert collect_predictions(ROOT, responses, output)["prediction_count"] == 10
    assert load_document(output) == originals
    result = evaluate(validate_dataset(ROOT / "cases/pilot"), output, True)
    assert result["aggregate"]["recognition"]["structural_eligibility"]["unresolved"] == 10
    assert result["aggregate"]["recognition"]["structural_eligibility"]["accuracy_on_resolved_pairs"] is None
    assert result["aggregate"]["recognition"]["practical_suitability"]["reference_known"] == 4
    assert len(result["results"]) == 10
    with pytest.raises(DataError, match="already exists"):
        collect_predictions(ROOT, responses, output)
    (responses / "pilot-001.json").write_text("```json\n{}\n```")
    invalid_output = tmp_path / "must_not_exist.json"
    with pytest.raises(DataError, match="invalid_responses"):
        collect_predictions(ROOT, responses, invalid_output)
    assert not invalid_output.exists()
    (responses / "pilot-001.json").unlink()
    with pytest.raises(DataError, match="filenames mismatch"):
        collect_predictions(ROOT, responses, invalid_output)


def test_comparison_includes_assumptions_and_uncertainty():
    a = {"case_id": "pilot-001", "candidate_regions": None, "assumptions": ["a"], "uncertainty": None}
    b = dict(a, candidate_regions=[], assumptions=["b"], uncertainty="Unknown oracle cost")
    differences = compare_annotations(a, b)["differences"]
    assert set(differences) == {"candidate_regions", "assumptions", "uncertainty"}


def test_explicit_subset_selection_is_recorded(tmp_path, capsys):
    output = tmp_path / "prediction.json"
    output.write_text(json.dumps([response("pilot-001")]))
    assert main(["evaluate", str(ROOT / "cases/pilot"), str(output), "--allow-draft", "--case-id", "pilot-001", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["selected_case_ids"] == ["pilot-001"]
    with pytest.raises(DataError):
        evaluate(validate_dataset(ROOT / "cases/pilot"), output, True, {"absent"})


def test_duplicate_contract_assessment_is_invalid():
    path = ROOT / "cases/pilot/pilot-001"
    case = load_document(path / "case.json")
    p = response(case["case_id"])
    assessment = {"contract_id": "grover-predicate-v0", "applicable": None, "rationale": "fixture"}
    p["contract_applicability"] = [assessment, assessment]
    assert "Duplicate contract applicability ID" in prediction_errors(p, case, path)
