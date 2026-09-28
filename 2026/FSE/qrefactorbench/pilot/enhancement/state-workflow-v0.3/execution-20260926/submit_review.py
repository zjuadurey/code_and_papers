"""Package explicit coordinator review; never infer claims from model text."""
import argparse
import time
from run_frozen import campaign as c


def submit(slot, spec_path, phase):
    folder = c.HERE / "campaign"
    out = c.HERE / "execution-20260926"
    spec = c.load_document(spec_path)
    raw = c.raw_path(folder, slot).read_text()
    document = c.load_document(c.raw_path(folder, slot))
    start = c.load_document(out / f"{slot}.review-start.json")
    reviewer = {"identity": "Codex coordinator", "status": "AI_REVIEW_PENDING"}
    binding = {"version": "0.2", "response_sha256": c.claims.response_digest(raw),
               "scope": "lit009_pivot_selection", "origin": "model_response", "reviewer": reviewer,
               "anchors": [{"pointer": pointer, "quote": c.claims.pointer(document, pointer)}
                           for pointer in spec["anchor_pointers"]],
               "resolution": spec["resolution"], "rationale": spec["rationale"],
               "interpretations": spec.get("interpretations", [])}
    review = {"response_sha256": c.claims.response_digest(raw), "reviewer": reviewer,
              "review_seconds": round(time.time() - start["epoch_seconds"], 3),
              "review_time_definition": "Wall-clock from first detailed response inspection to submission; includes coordinator/tool latency, not isolated human labor.",
              "review_started_utc": start["utc"], "review_submitted_utc": c.now(),
              "binding": binding, "unbound_reason": None}
    c.check_review(raw, review)
    if phase == "initial":
        c.stage_review(folder, slot, review)
    else:
        c.bind_final(folder, slot, review)
    print(f"Frozen {phase} review for {slot}: {spec['resolution']}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["initial", "final"])
    parser.add_argument("slot")
    parser.add_argument("spec", type=c.Path)
    args = parser.parse_args()
    submit(args.slot, args.spec, args.phase)
