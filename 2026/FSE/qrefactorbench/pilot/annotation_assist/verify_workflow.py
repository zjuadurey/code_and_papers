"""One-off researcher-review audit; all response fixtures are temporary DUMMY data.

Run from the repository with its existing palqo Python. No model calls, scientific
predictions, reference-label changes or evaluator modifications occur here.
"""

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from qrefactorbench.schema import schema_errors  # noqa: E402


def hashes(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def invoke(arguments: list[str], expected_exit: int = 0) -> dict[str, Any]:
    completed = subprocess.run([sys.executable, *arguments], cwd=ROOT, capture_output=True,
                               text=True, timeout=60)
    assert completed.returncode == expected_exit, (arguments, completed.stdout, completed.stderr)
    return json.loads(completed.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets", type=Path, default=ROOT / "pilot/packets-v0.1",
                        help="Current packet snapshot to compare with a fresh export")
    packets = parser.parse_args().packets.resolve()
    expected_ids = [f"pilot-{number:03d}" for number in range(1, 11)]
    checks: dict[str, Any] = {}
    for role in ("annotator_a", "annotator_b", "adjudication", "baseline"):
        directory = packets / role
        manifest = json.loads((directory / "packet_manifest.json").read_text())
        assert manifest["case_ids"] == expected_ids
        actual = hashes(directory)
        assert set(actual) == set(manifest["files_sha256"]) | {"packet_manifest.json"}
        for name, digest in manifest["files_sha256"].items():
            assert actual[name] == digest
    checks["packet_manifests_and_ids"] = "PASS: all four roles; exact file inventory and hashes"
    for role in ("annotator_a", "annotator_b"):
        directory = packets / role
        for case_id in expected_ids:
            case_dir = directory / case_id
            form = json.loads((case_dir / "annotation.json").read_text())
            for key in ("candidate_regions", "structural_eligibility", "practical_suitability",
                        "benchmark_supported", "computational_intent", "migration_family",
                        "expected_decision", "contract_applicability", "annotator_id"):
                assert form[key] is None
            assert form["completion_status"] == "UNFILLED"
            task = json.loads((case_dir / "public_task.json").read_text())
            assert set(task) == {"case_id", "title", "software_contract", "input_domain", "execution_assumptions"}
            assert task["case_id"] == case_id
            assert not {"case.json", "CURATOR_NOTES.md", "test_program.py", "seed_manifest.json"} & {p.name for p in case_dir.iterdir()}
    for path in (packets / "baseline/prompts").glob("*.md"):
        text = path.read_text()
        assert not any(marker in text for marker in (
            '"expected_decision":', '"case_type":', '"reference_plan":',
            '"annotation_rationale":', '"admissible_migration_contracts":'))
    checks["case_specific_reference_fields"] = "PASS: absent from prompts; A/B forms blank; no private case artifacts"
    checks["blinding_limit"] = "Public prose can cue intent/localization; schemas/menu contain generic field definitions, not per-case answers. Human review required."
    fixture = {"schema_version": "0.2.0", "case_id": expected_ids[0],
               "decision": "REMAIN_CLASSICAL", "candidate_regions": [],
               "structural_eligibility": None, "practical_suitability": None,
               "benchmark_supported": None, "computational_intent": None,
               "migration_family": None, "contract_applicability": [], "assumptions": [],
               "risks": [], "rationale": "DUMMY WORKFLOW FIXTURE, NOT ANALYSIS OR A MODEL RESPONSE", "plan": None}
    for label in ("structural_eligibility", "practical_suitability", "benchmark_supported"):
        for value in (True, False, None):
            assert not schema_errors(dict(fixture, **{label: value}), "prediction")
        assert schema_errors(dict(fixture, **{label: "UNCERTAIN"}), "prediction")
    checks["yes_no_uncertain_labels"] = "PASS: JSON true/false/null, not literal YES/NO/UNCERTAIN strings"
    assert schema_errors(dict(fixture, decision="UNCERTAIN"), "prediction")
    assert schema_errors(dict(fixture, candidate_regions=None), "prediction")
    checks["expressivity_limits"] = ["No third UNCERTAIN decision; labels may still be null when abstaining.",
                                     "Prediction candidate_regions cannot be null; unknown localization needs narrative, unlike blank human forms."]
    with tempfile.TemporaryDirectory(prefix="qrb-review-audit-") as temporary:
        directory = Path(temporary)
        fresh = directory / "packets"
        prepared = invoke(["scripts/prepare_pilot.py", "prepare", "--output", str(fresh)])
        assert prepared["case_count"] == 10 and prepared["model_calls"] == 0
        assert hashes(fresh) == hashes(packets)
        checks["fresh_packet_export"] = "PASS: byte-identical to existing packets; existing material untouched"
        responses = directory / "responses"
        responses.mkdir()
        fixtures = []
        for i, case_id in enumerate(expected_ids):
            value = copy.deepcopy(fixture)
            value["case_id"] = case_id
            value["structural_eligibility"] = (None, True, False)[i % 3]
            value["practical_suitability"] = (False, None, True)[i % 3]
            if i == 0:
                value.update(decision="QUANTUMIZE", candidate_regions=[{
                    "file": "program.py", "start_line": 1, "end_line": 1}],
                    migration_family="unstructured_search", plan={
                        "schema_version": "0.1.0", "contract_id": "grover-predicate-v0",
                        "computational_intent_id": "dummy_not_a_reference_id",
                        "migration_family": "unstructured_search", "formulation": "DUMMY",
                        "input_encoding": "DUMMY", "quantum_algorithm_family": "grover_style",
                        "output_decoding": "DUMMY", "assumptions": [], "risks": [],
                        "expected_resource_characteristics": {"status": "DUMMY"}})
            assert not schema_errors(value, "prediction")
            fixtures.append(value)
            (responses / f"{case_id}.json").write_text(json.dumps(value))
        output = directory / "predictions.json"
        collected = invoke(["scripts/prepare_pilot.py", "collect", "--responses", str(responses), "--output", str(output)])
        assert collected["prediction_count"] == 10 and collected["repairs"] == 0
        assert json.loads(output.read_text()) == fixtures
        command = ["-m", "qrefactorbench", "evaluate", "cases/pilot", str(output), "--json"]
        assert "error" in invoke(command, expected_exit=2)
        evaluated = invoke([*command, "--allow-draft"])
        assert evaluated["selected_case_ids"] == expected_ids
        assert evaluated["demonstration_only"] is True
        assert [r["prediction"] for r in evaluated["results"]] == fixtures
        checks["collect_schema_evaluate_cli"] = "PASS: ten IDs and both decisions, no value repairs, default DRAFT exclusion, explicit demo gate"
        # Scores are deliberately not exported: these records have no scientific meaning.
        (responses / f"{expected_ids[0]}.json").write_text("```json\n{}\n```")
        invalid_output = directory / "invalid.json"
        rejected = invoke(["scripts/prepare_pilot.py", "collect", "--responses", str(responses), "--output", str(invalid_output)], expected_exit=2)
        assert "error" in rejected and not invalid_output.exists()
        checks["malformed_response"] = "PASS: rejected without repair or output artifact"
        comparison = invoke(["-m", "qrefactorbench", "compare-annotations",
                             str(packets / "annotator_a/pilot-001/annotation.json"),
                             str(packets / "annotator_b/pilot-001/annotation.json"), "--json"])
        assert comparison["differences"] == {}
        checks["comparison_cli"] = "PASS mechanically; empty blank-form diff is NOT annotator agreement"
    evidence = json.loads((Path(__file__).parent / "evidence_manifest.json").read_text())
    for name, digest in evidence["proposal_sha256_before_audit"].items():
        assert hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest() == digest
    checks["proposals_not_revised_using_audit"] = "PASS: all ten pre-audit proposal hashes unchanged"
    print(json.dumps({"date": "2026-09-20", "packets": str(packets.relative_to(ROOT)),
                      "scope": "MECHANICAL AUDIT ONLY; no baseline",
                      "model_calls": 0, "case_ids": expected_ids, "checks": checks,
                      "dummy_responses_retained": False, "scores_reported": False}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
