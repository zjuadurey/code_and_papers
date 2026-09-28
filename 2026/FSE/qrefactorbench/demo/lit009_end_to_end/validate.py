"""One-shot delivery validation; preserve raw results and protected old files."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from demo.lit009_end_to_end import hybrid as h


def main():
    output = h.HERE / "validation"
    if (output / "validation.json").exists():
        raise FileExistsError("Validation already recorded; use a separate package/output for new evidence")
    commands = [
        ("new_tests", [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                       "demo/lit009_end_to_end/test_demo.py"], {}),
        ("original_tests", [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                            str(h.SOURCE / "test_program.py")], {"PYTHONPATH": str(h.SOURCE)}),
        ("replay", [sys.executable, "-B", "-m", "demo.lit009_end_to_end.run",
                    "--output", str(output / "replay")], {})]
    records = []
    for name, command, overrides in commands:
        result = subprocess.run(command, cwd=h.ROOT, env={**os.environ, **overrides},
                                text=True, capture_output=True, timeout=120)
        (output / f"{name}.stdout.txt").write_text(result.stdout)
        (output / f"{name}.stderr.txt").write_text(result.stderr)
        records.append(dict(name=name, command=command, environment_overrides=overrides,
                            exit_code=result.returncode))
        if result.returncode:
            raise RuntimeError(f"{name} failed; see preserved stdout/stderr")
    first = json.loads((h.HERE / "results-20260928/results.json").read_text())
    replay = json.loads((output / "replay/results.json").read_text())
    fields = ("semantics", "resources", "source_sha256", "protocol", "versions")
    equal = {field: first[field] == replay[field] for field in fields}
    circuits = {str(p.relative_to(h.HERE / "results-20260928")): p.read_bytes() ==
                (output / "replay" / p.name).read_bytes()
                for p in (h.HERE / "results-20260928").glob("search-*")}
    protected = json.loads((output / "protected_before.json").read_text())
    changed = [path for path, digest in protected.items()
               if not (h.ROOT/path).is_file() or hashlib.sha256((h.ROOT/path).read_bytes()).hexdigest() != digest]
    if not all(equal.values()) or not all(circuits.values()) or changed:
        raise AssertionError(dict(replay=equal, circuits=circuits, changed=changed))
    record = dict(commands=records, deterministic_replay=equal, circuits_identical=circuits,
                  protected_count=len(protected), changed_protected_files=changed,
                  timing_replay="new raw timings retained; not expected byte-identical",
                  scope="finite local implementation validation, not independent scientific adjudication",
                  qpu_calls=0, new_model_calls=0, dependencies_installed=0,
                  global_status_modified=False)
    (output / "validation.json").write_text(json.dumps(record, indent=2)+"\n")
    manifest = {str(p.relative_to(h.HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(h.HERE.rglob("*")) if p.is_file() and p.name != "manifest.json"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"commands_passed": len(records), "protected_unchanged": len(protected),
                      "semantic_comparisons": first["semantics"]["comparisons"],
                      "replay_equal": all(equal.values()), "artifact_files": len(manifest)}))


if __name__ == "__main__":
    main()
