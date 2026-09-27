"""Package manual, quote-bound coordinator reviews after the fixed model queue ends."""
import argparse
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import campaign as c


def inspect(slot: str) -> None:
    folder = c.HERE / "campaign"
    state = c.state(folder)
    if state["state"] not in ("all_slots_terminal", "stopped"):
        raise ValueError("Review only after the model queue terminates")
    if state["records"][slot]["status"] != "valid_response":
        raise ValueError("Not a valid response")
    c.save(HERE / f"{slot}.review-start.json", {"utc": c.now(), "epoch_seconds": time.time(),
           "response_sha256": c.sha(c.raw_path(folder, slot))})
    print(c.raw_path(folder, slot).read_text())


def submit(slot: str, spec_path: Path) -> None:
    folder = c.HERE / "campaign"
    spec = c.load_document(spec_path)
    start = c.load_document(HERE / f"{slot}.review-start.json")
    raw = c.raw_path(folder, slot).read_text()
    document = c.load_document(c.raw_path(folder, slot))
    if start["response_sha256"] != c.claims.response_digest(raw):
        raise ValueError("Response changed during review")
    reviewer = {"identity": "Codex coordinator", "status": "AI_REVIEW_PENDING"}
    binding = {"version": "0.2", "response_sha256": start["response_sha256"],
               "scope": "lit009_pivot_selection", "origin": "model_response", "reviewer": reviewer,
               "anchors": [{"pointer": path, "quote": c.claims.pointer(document, path)}
                           for path in spec["anchor_pointers"]],
               "resolution": spec["resolution"], "rationale": spec["rationale"],
               "interpretations": spec.get("interpretations", [])}
    review = {"response_sha256": start["response_sha256"], "reviewer": reviewer,
              "review_seconds": round(time.time() - start["epoch_seconds"], 3),
              "review_time_definition": "Wall-clock from first detailed inspection to submission; includes coordination/tool delays, not independent human labor.",
              "review_started_utc": start["utc"], "review_submitted_utc": c.now(),
              "binding": binding, "unbound_reason": None}
    c.bind_final(folder, slot, review)
    print(json.dumps({"slot": slot, "resolution": spec["resolution"], "frozen": True}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["inspect", "submit"])
    parser.add_argument("slot")
    parser.add_argument("--spec", type=Path)
    args = parser.parse_args()
    inspect(args.slot) if args.action == "inspect" else submit(args.slot, args.spec)
