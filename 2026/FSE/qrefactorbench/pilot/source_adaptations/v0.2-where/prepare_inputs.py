"""Export two paired source/context inputs using explicit public allowlists."""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC_KEYS = {"case_id", "title", "software_contract", "input_domain", "execution_assumptions"}
PACKETS = {
    "source-core-003": {name: HERE / "cores/source-core-003" / name for name in ("program.py", "public_task.json")},
    "source-core-004": {name: HERE / "cores/source-core-004" / name for name in ("program.py", "public_task.json")},
    "lit-003": {name: HERE / "cases/lit-003" / name for name in ("program.py", "agenda.py", "catalog.py", "public_task.json")},
    "lit-004": {name: HERE / "cases/lit-004" / name for name in ("program.py", "reports.py", "catalog.py", "public_task.json")},
}
for files in PACKETS.values():
    files["NOTICE.txt"] = HERE / "NOTICE.txt"


def prepare(output: Path) -> None:
    payloads = {}
    for case_id, paths in PACKETS.items():
        task = json.loads(paths["public_task.json"].read_text())
        if set(task) != PUBLIC_KEYS or task["case_id"] != case_id:
            raise ValueError(f"unexpected public fields: {case_id}")
        payloads[case_id] = {name: path.read_bytes() for name, path in paths.items()}
    output.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for case_id, files in payloads.items():
        (output / case_id).mkdir()
        for name, data in files.items():
            (output / case_id / name).write_bytes(data)
            hashes[f"{case_id}/{name}"] = hashlib.sha256(data).hexdigest()
    (output / "manifest.json").write_text(json.dumps({"version": "source-where-0.2.0", "files_sha256": hashes}, indent=2) + "\n")
    print(f"Exported {len(payloads)} source/context views; no reference annotations or model invocation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    prepare(parser.parse_args().output)
