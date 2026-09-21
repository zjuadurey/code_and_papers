"""Export this context case's public spec and source; no labels or model calls."""

import argparse
import hashlib
import json
from pathlib import Path


def prepare(output: Path) -> None:
    root = Path(__file__).resolve().parent
    case = root / "cases" / "context-001"
    task = json.loads((case / "public_task.json").read_text())
    expected = {"case_id", "title", "software_contract", "input_domain", "execution_assumptions"}
    if set(task) != expected or task["case_id"] != "context-001":
        raise ValueError("Unexpected public fields or case ID")
    contents = {name: (case / name).read_bytes() for name in
                ("program.py", "maintenance.py", "public_task.json")}
    output.mkdir(parents=True, exist_ok=False)
    for name, content in contents.items():
        (output / name).write_bytes(content)
    (output / "manifest.json").write_text(json.dumps({
        "version": "context-adaptation-0.1.0-review-input",
        "case_id": "context-001",
        "files_sha256": {name: hashlib.sha256(content).hexdigest()
                         for name, content in contents.items()},
    }, indent=2) + "\n")
    print(f"Exported one public input to {output}; no prediction generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    prepare(parser.parse_args().output)
