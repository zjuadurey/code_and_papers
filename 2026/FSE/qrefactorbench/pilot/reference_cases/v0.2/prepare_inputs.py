"""Export eight fixed views, retaining the four earlier public inputs byte-for-byte."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("reference_views_v01", HERE.parent / "v0.1/prepare_inputs.py")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
PACKETS = dict(previous.PACKETS)
PACKETS.update({
    "core-003": {"program.py": ROOT / "cases/pilot/pilot-001/program.py", "public_task.json": HERE / "core_specs/core-003.json"},
    "core-004": {"program.py": ROOT / "cases/pilot/pilot-002/program.py", "public_task.json": HERE / "core_specs/core-004.json"},
    "context-003": {name: HERE / "cases/context-003" / name for name in ("program.py", "configurations.py", "public_task.json")},
    "context-004": {name: HERE / "cases/context-004" / name for name in ("program.py", "records.py", "public_task.json")},
})


def prepare(output: Path) -> None:
    contents = {}
    for case_id, files in PACKETS.items():
        task = json.loads(files["public_task.json"].read_text())
        if set(task) != previous.PUBLIC_KEYS or task["case_id"] != case_id:
            raise ValueError(f"Unexpected public specification: {case_id}")
        contents[case_id] = {name: path.read_bytes() for name, path in files.items()}
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"version": "reference-views-0.2.0", "files_sha256": {}}
    for case_id, files in contents.items():
        (output / case_id).mkdir()
        for name, data in files.items():
            (output / case_id / name).write_bytes(data)
            manifest["files_sha256"][f"{case_id}/{name}"] = hashlib.sha256(data).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Exported {len(contents)} public views to {output}; no model run or reference labels.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    prepare(parser.parse_args().output)
