import copy
import json

import pytest

from qrefactorbench.cli import evaluate, main
from qrefactorbench.evaluator import Check
from qrefactorbench.evaluator.candidate import evaluate_candidates
from qrefactorbench.evaluator.decision import evaluate_decisions
from qrefactorbench.evaluator.pipeline import end_to_end_quantumization_success, prediction_errors
from qrefactorbench.evaluator.planning import evaluate_plan
from qrefactorbench.loader import DataError
from qrefactorbench.validator import validate_dataset

from conftest import ROOT, TOY_IDS


def region(a, b, file="a.py"):
    return {"file": file, "start_line": a, "end_line": b}


def test_exact_and_overlap_are_distinct():
    result = evaluate_candidates([region(2, 5)], [region(3, 6)])
    assert result["candidate_correct"] is False
    assert result["exact"]["f1"] == 0
    assert result["line_overlap"]["iou"] == 3 / 5
    assert result["line_overlap"]["correctness_threshold"] is None


def test_union_overlap_has_no_double_counting():
    result = evaluate_candidates([region(1, 10)], [region(1, 8), region(3, 10), region(1, 8)])
    assert result["line_overlap"]["predicted_lines"] == 10
    assert result["line_overlap"]["iou"] == 1
    assert result["exact"]["predicted"] == 2
    assert evaluate_candidates([region(1, 10)], [region(1, 10, "b.py")])["line_overlap"]["iou"] == 0


def test_empty_candidate_sets():
    result = evaluate_candidates([], [])
    assert result["candidate_correct"] is True
    assert result["exact"]["precision"] is None
    assert evaluate_candidates([], [region(1, 1)])["candidate_correct"] is False


def test_decision_denominators():
    q, r = "QUANTUMIZE", "REMAIN_CLASSICAL"
    result = evaluate_decisions([(q, q), (q, r), (r, q), (r, r), (r, r), (None, q)])
    assert result["false_quantumization_rate"] == 1 / 3
    assert result["remain_classical_accuracy"] == 2 / 3
    assert result["overall_decision_accuracy"] == 3 / 5
    assert result["quantumize_recall"] == 1 / 2
    assert result["counts"]["unscored"] == 1
    assert evaluate_decisions([(q, q)])["false_quantumization_rate"] is None


def test_contract_membership_never_proves_conformity(draft_case):
    _, case = draft_case
    prediction = {"decision": "QUANTUMIZE", "plan": copy.deepcopy(case["reference_plan"])}
    result = evaluate_plan(case, prediction)
    assert result["contract_membership"] is True
    assert result["admissible_plan"] is None
    assert evaluate_plan(case, prediction, lambda c, p: Check(True, "fixture evidence"))["admissible_plan"] is True
    prediction["plan"]["quantum_algorithm_family"] = "unlisted"
    assert evaluate_plan(case, prediction)["admissible_plan"] is False


def test_end_to_end_does_not_hide_unknown_components():
    names = ["candidate_correct", "decision_correct", "admissible_plan", "syntax_valid", "imports_valid",
             "execution_success", "interface_preserved", "semantic_oracle_pass", "quantum_constraints_pass", "resource_limits_pass"]
    evidence = dict.fromkeys(names, True)
    assert end_to_end_quantumization_success("QUANTUMIZE", evidence) is True
    evidence.pop("semantic_oracle_pass")
    assert end_to_end_quantumization_success("QUANTUMIZE", evidence) is None
    evidence["execution_success"] = False
    assert end_to_end_quantumization_success("QUANTUMIZE", evidence) is False
    assert end_to_end_quantumization_success("REMAIN_CLASSICAL", evidence) is None


def test_default_draft_exclusion_and_reproducibility():
    report = validate_dataset(ROOT / "cases")
    predictions = ROOT / "examples/draft_predictions.json"
    with pytest.raises(DataError, match="No eligible cases"):
        evaluate(report, predictions, False)
    first = evaluate(report, predictions, True, TOY_IDS)
    assert first == evaluate(report, predictions, True, TOY_IDS)
    assert first["demonstration_only"] is True
    assert first["aggregate"]["end_to_end_quantumization_success"] == {"passed": 0, "failed": 1, "unknown": 1, "applicable": 2}
    assert first["reproducibility"]["cases"]["toy-hard-negative-001"]["artifacts_sha256"]["main.py"]


@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate"])
def test_prediction_coverage_is_explicit(tmp_path, mutation):
    predictions = json.loads((ROOT / "examples/draft_predictions.json").read_text())
    if mutation == "missing":
        predictions.pop()
    elif mutation == "extra":
        predictions.append(dict(predictions[0], case_id="unknown-case"))
    else:
        predictions.append(predictions[0])
    path = tmp_path / "predictions.json"
    path.write_text(json.dumps(predictions))
    with pytest.raises(DataError):
        evaluate(validate_dataset(ROOT / "cases"), path, True, TOY_IDS)


def test_generated_path_and_plan_consistency(draft_case):
    path, case = draft_case
    p = {"schema_version": "0.1.0", "case_id": case["case_id"], "decision": "QUANTUMIZE",
         "candidate_regions": case["candidate_regions"], "plan": case["reference_plan"],
         "migration_family": "combinatorial_optimization", "generated_files": [{"path": "../escape.py", "content": "pass"}]}
    assert prediction_errors(p, case, path.parent)


def test_cli_json_and_failure_exit_codes(capsys, tmp_path):
    assert main(["summarize", str(ROOT / "cases"), "--json"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["counts"]["annotation_status"] == {"DRAFT": 14}
    assert output["counts"]["practical_suitability"] == {"false": 5, "true": 2, "unknown": 7}
    assert main(["validate", str(tmp_path), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["valid"] is False
    assert main(["evaluate", str(ROOT / "cases"), str(ROOT / "examples/draft_predictions.json"), "--json"]) == 2
    assert "error" in json.loads(capsys.readouterr().out)


def test_annotation_comparison_reports_but_does_not_adjudicate(draft_case, tmp_path, capsys):
    path, case = draft_case
    other = tmp_path / "annotation.json"
    case["practical_suitability"] = False
    other.write_text(json.dumps(case))
    assert main(["compare-annotations", str(path), str(other), "--json"]) == 0
    diff = json.loads(capsys.readouterr().out)["differences"]
    assert diff["practical_suitability"] == {"left": True, "right": False, "left_present": True, "right_present": True}
