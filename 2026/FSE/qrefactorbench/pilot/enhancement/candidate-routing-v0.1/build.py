"""Offline N-055 public-input inventory and historical nomination audit."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import routing

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-009"
TASK = ROOT / "pilot/reference_completion/v0.1.1/review_inputs/lit-009-C.txt"
INITIALS = HERE.parent / "state-workflow-v0.3/campaign/runs/gpt-5.6-sol"
PUBLIC_FILES = ("program.py", "kernel.py", "common.py")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value) -> None:
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def build(folder: Path) -> dict:
    folder.mkdir(parents=True, exist_ok=False)
    sources = {name: (CASE / name).read_text() for name in PUBLIC_FILES}
    task = TASK.read_text()
    # Assert exact source bytes (minus line-number presentation) already occur in the public task.
    for name, source in sources.items():
        numbered = "\n".join(f"{i}: {line}" for i, line in enumerate(source.splitlines(), 1))
        if f"FILE {name}\n{numbered}" not in task:
            raise ValueError(f"Source differs from public task: {name}")
    manifest = {str(f.relative_to(ROOT)): sha(f) for f in
                [TASK, routing.LEGACY, HERE / "routing.py", HERE / "build.py", HERE / "test_routing.py",
                 *(CASE / name for name in PUBLIC_FILES)]}
    rows = []
    for n in range(1, 6):
        sid = f"{n:02d}-initial"
        path = INITIALS / sid / "response.txt"
        raw = path.read_text()
        regions = json.loads(raw)["candidate_regions"]
        start = time.perf_counter()
        analysis = routing.analyze(sources, regions)
        elapsed = time.perf_counter() - start
        save(folder / f"{sid}.json", analysis)
        manifest[str(path.relative_to(ROOT))] = sha(path)
        rows.append({"initial": sid, "initial_sha256": sha(path), "declared_regions": regions,
                     "status": analysis["status"], "route_statuses": [r["status"] for r in analysis["routes"]],
                     "packet_sha256": sha(folder / f"{sid}.json"), "analysis_seconds": elapsed})
    protected = json.loads((HERE / "protected_before.json").read_text())
    assert all((ROOT / p).is_file() and sha(ROOT / p) == h for p, h in protected.items())
    save(folder / "source-manifest.json", manifest)
    summary = {"status": "offline_interface_audited", "rows": rows, "new_model_calls": 0,
               "new_qpu_calls": 0, "effect_on_model_quality": None, "public_source_files": list(PUBLIC_FILES),
               "source_exactly_matches_public_task": True, "protected_files_unchanged": len(protected),
               "limits": routing.LIMITS}
    save(folder / "summary.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(build(parser.parse_args().output), indent=2))
