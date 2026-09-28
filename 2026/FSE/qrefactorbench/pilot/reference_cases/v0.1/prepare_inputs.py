"""Export four fixed source/spec views; never copy private review or test artifacts."""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "pilot/source_adaptations/v0.1/cases"
CONTEXT = ROOT / "pilot/context_adaptations/v0.1/cases/context-001"
PACKETS = {
    "core-001": {"program.py": SOURCE / "lit-001/kernel.py", "public_task.json": HERE / "core_specs/core-001.json"},
    "core-002": {"program.py": SOURCE / "lit-002/kernel.py", "public_task.json": HERE / "core_specs/core-002.json"},
    "context-001": {"program.py": CONTEXT / "program.py", "maintenance.py": CONTEXT / "maintenance.py",
                    "public_task.json": CONTEXT / "public_task.json"},
    "context-002": {name: HERE / "cases/context-002" / name
                    for name in ("program.py", "inspection.py", "public_task.json")},
}
PUBLIC_KEYS = {"case_id", "title", "software_contract", "input_domain", "execution_assumptions"}


def prepare(output: Path) -> None:
    prepared = {}
    for case_id, files in PACKETS.items():
        task = json.loads(files["public_task.json"].read_text())
        if set(task) != PUBLIC_KEYS or task["case_id"] != case_id:
            raise ValueError(f"Unexpected public spec for {case_id}")
        prepared[case_id] = {name: path.read_bytes() for name, path in files.items()}
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"version": "reference-views-0.1.0", "files_sha256": {}}
    for case_id, files in prepared.items():
        (output / case_id).mkdir()
        for name, data in files.items():
            (output / case_id / name).write_bytes(data)
            manifest["files_sha256"][f"{case_id}/{name}"] = hashlib.sha256(data).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Exported four source/spec views to {output}; no predictions or reference answers.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    prepare(parser.parse_args().output)
