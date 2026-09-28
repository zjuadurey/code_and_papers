"""Freeze source-catalog/routing controls from all five original drafts."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROUTING = HERE.parent / "candidate-routing-v0.1"
WORKFLOW = HERE.parent / "state-workflow-v0.1/workflow.py"
spec = importlib.util.spec_from_file_location("n056_revision_format", WORKFLOW)
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def catalog_packet(routed: dict) -> dict:
    result = deepcopy(routed)
    result["status"] = "source_catalog_only"
    result["routes"] = []
    return result


def build() -> None:
    folder = HERE / "design"
    folder.mkdir(exist_ok=False)
    sources = json.loads((ROUTING / "audit/source-manifest.json").read_text())
    for path, digest in sources.items():
        if sha(ROOT / path) != digest:
            raise ValueError(f"N-055 source changed: {path}")
    task = ROOT / "pilot/reference_completion/v0.1.1/review_inputs/lit-009-C.txt"
    slots = []
    for n in range(1, 6):
        initial = f"{n:02d}-initial"
        draft = HERE.parent / "state-workflow-v0.3/campaign/runs/gpt-5.6-sol" / initial / "response.txt"
        packet_path = ROUTING / "audit" / f"{initial}.json"
        routed = json.loads(packet_path.read_text())
        sources[str(packet_path.relative_to(ROOT))] = sha(packet_path)
        arms = ["self_review", "catalog_only", "routed_analysis"]
        shift = (n - 1) % 3
        arms = arms[shift:] + arms[:shift]
        for arm in arms:
            sid = f"{n:02d}-{arm}"
            observations = [] if arm == "self_review" else [catalog_packet(routed) if arm == "catalog_only" else routed]
            text = workflow.revision_prompt(task.read_text(), draft.read_text(), observations)
            path = folder / f"{sid}.txt"
            path.write_text(text)
            slots.append({"id": sid, "initial": initial, "arm": arm,
                          "initial_sha256": sha(draft), "prompt_sha256": sha(path)})
    for path in [Path(__file__).resolve(), WORKFLOW, ROUTING / "audit/source-manifest.json"]:
        sources[str(path.relative_to(ROOT))] = sha(path)
    (folder / "prompt-design.json").write_text(json.dumps({"slots": slots}, indent=2) + "\n")
    (folder / "source-manifest.json").write_text(json.dumps(sources, indent=2) + "\n")


if __name__ == "__main__":
    build()
