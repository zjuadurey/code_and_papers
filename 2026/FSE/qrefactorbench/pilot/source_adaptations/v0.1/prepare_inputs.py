"""Export only two public source/spec inputs; no model call or annotation export."""

import argparse
import hashlib
import json
from pathlib import Path

CASE_IDS = ("lit-001", "lit-002")
FILES = ("program.py", "kernel.py", "public_task.json")
PUBLIC_FIELDS = {"case_id", "title", "software_contract", "input_domain", "execution_assumptions"}


def prepare(output: Path) -> None:
    root = Path(__file__).resolve().parent
    contents = {}
    for case_id in CASE_IDS:
        source = root / "cases" / case_id
        task = json.loads((source / "public_task.json").read_text())
        if set(task) != PUBLIC_FIELDS or task["case_id"] != case_id:
            raise ValueError(f"Unexpected public fields or ID: {case_id}")
        for name in FILES:
            contents[f"{case_id}/{name}"] = (source / name).read_bytes()
    output.mkdir(parents=True, exist_ok=False)
    for name, content in contents.items():
        target = output / name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(content)
    (output / "manifest.json").write_text(json.dumps({
        "version": "source-adaptations-0.1.0-review-inputs",
        "case_ids": CASE_IDS,
        "files_sha256": {name: hashlib.sha256(content).hexdigest()
                         for name, content in contents.items()},
    }, indent=2) + "\n")
    print(f"Exported two public inputs to {output}; no predictions generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    prepare(parser.parse_args().output)
