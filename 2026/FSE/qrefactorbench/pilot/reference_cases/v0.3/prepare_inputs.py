"""Export sixteen allowlisted views without overwriting any existing directory."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("reference_views_v02", HERE.parent / "v0.2/prepare_inputs.py")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
PUBLIC_KEYS = previous.previous.PUBLIC_KEYS
PACKETS = dict(previous.PACKETS)
for suffix, parent, module in [("005", "007", "lots"), ("006", "006", "packages"),
                                ("007", None, "archive"), ("008", "008", "exports")]:
    PACKETS[f"core-{suffix}"] = {
        "program.py": ROOT / f"cases/pilot/pilot-{parent}/program.py" if parent else HERE / "cores/core-007.py",
        "public_task.json": HERE / f"core_specs/core-{suffix}.json"}
    PACKETS[f"context-{suffix}"] = {name: HERE / f"cases/context-{suffix}" / name
                                     for name in ("program.py", f"{module}.py", "public_task.json")}


def prepare(output: Path) -> None:
    contents = {}
    for case_id, files in PACKETS.items():
        task = json.loads(files["public_task.json"].read_text())
        if set(task) != PUBLIC_KEYS or task["case_id"] != case_id:
            raise ValueError(f"Unexpected public specification: {case_id}")
        contents[case_id] = {name: path.read_bytes() for name, path in files.items()}
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"version": "reference-views-0.3.0", "files_sha256": {}}
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
