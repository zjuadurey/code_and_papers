"""Public-text revision checks; fixtures are not scientific annotations."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ROOT
from qrefactorbench.loader import load_document
from qrefactorbench.pilot import prepare_packets


PACKETS = ROOT / "pilot/packets-v0.1"
ARCHIVE = ROOT / "pilot/revisions/pilot-v0.1/original_public_tasks"


def file_hashes(directory: Path) -> dict[str, str]:
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


def test_v01_public_snapshot_and_original_preservation():
    for number in range(1, 11):
        case_id = f"pilot-{number:03d}"
        original = load_document(ARCHIVE / case_id / "public_task.json")
        current = load_document(ROOT / "cases/pilot" / case_id / "public_task.json")
        for role in ("annotator_a", "annotator_b"):
            assert original == load_document(ROOT / "pilot/packets" / role / case_id / "public_task.json")
            assert current == load_document(PACKETS / role / case_id / "public_task.json")
            for source in (ROOT / "cases/pilot" / case_id).glob("*.py"):
                if source.name != "test_program.py":
                    assert source.read_bytes() == (PACKETS / role / case_id / source.name).read_bytes()
        # Functional contracts/domains are unchanged except the two documented edits.
        if number != 6:
            assert current["software_contract"] == original["software_contract"]
        if number != 9:
            assert current["input_domain"] == original["input_domain"]
    for role in ("annotator_a", "annotator_b", "adjudication", "baseline"):
        directory = PACKETS / role
        manifest = load_document(directory / "packet_manifest.json")
        actual = file_hashes(directory)
        assert set(actual) == set(manifest["files_sha256"]) | {"packet_manifest.json"}
        for name, digest in manifest["files_sha256"].items():
            assert actual[name] == digest


def test_v01_regeneration_is_byte_identical(tmp_path):
    output = tmp_path / "fresh"
    result = prepare_packets(ROOT, output)
    assert result["case_count"] == 10 and result["model_calls"] == 0
    assert file_hashes(output) == file_hashes(PACKETS)


@pytest.mark.parametrize("readme_present", [True, False])
def test_v01_export_is_independent_of_project_readme(tmp_path, readme_present):
    repository = tmp_path / "repo"
    shutil.copytree(ROOT / "cases/pilot", repository / "cases/pilot")
    shutil.copytree(ROOT / "pilot/annotation", repository / "pilot/annotation")
    shutil.copytree(ROOT / "pilot/baseline", repository / "pilot/baseline")
    shutil.copy(ROOT / "pilot/public_contracts.json", repository / "pilot/public_contracts.json")
    # Only export sources are present: no frozen packets or experiment results.
    readme = repository / "pilot/baseline/README.md"
    private_note = "PRIVATE_EXPERIMENT_FINDINGS_NOT_FOR_PACKET"
    if readme_present:
        readme.write_text(private_note, encoding="utf-8")
    else:
        readme.unlink()
    output = tmp_path / "fresh"
    assert prepare_packets(repository, output)["model_calls"] == 0
    assert file_hashes(output) == file_hashes(PACKETS)
    assert private_note not in (output / "baseline/INSTRUCTIONS.md").read_text()


def test_pilot009_public_types_match_executable_validation():
    task = load_document(ROOT / "cases/pilot/pilot-009/public_task.json")
    assert "string name" in task["input_domain"]
    assert "integer left_cost/right_cost" in task["input_domain"]
    result = subprocess.run(
        [sys.executable, "-c", '''
import json
from program import placement_report
valid = [{"name": "a", "left_cost": 1, "right_cost": 2}]
result = placement_report(valid, [])
assert result == {"cost": 1, "names": ["a"], "count": 1}
for jobs, links in [([dict(valid[0], name=7)], []), (valid, [(0, 1, 0)]),
                    (valid, [(-1, 0, 0)]), (valid, [(0, 0, -1)])]:
    try:
        placement_report(jobs, links)
    except ValueError:
        continue
    raise AssertionError("Invalid input was accepted")
print(json.dumps(result))
'''], cwd=ROOT / "cases/pilot/pilot-009", capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["names"] == ["a"]
