"""Offline claim-review entry points. Never calls a model or executes its code."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claims import development_feedback, evaluate, pointer, response_digest


def run(args: argparse.Namespace) -> None:
    if args.output.exists():
        raise FileExistsError(args.output)
    raw = args.response.read_text()
    if args.action == "template":
        quote = pointer(json.loads(raw), args.pointer)
        if not isinstance(quote, str) or not quote:
            raise ValueError("Choose a nonempty response string as the review anchor")
        result = {"version": "0.2", "response_sha256": response_digest(raw),
                  "scope": "lit009_pivot_selection", "origin": "model_response",
                  "reviewer": {"identity": None, "status": "UNREVIEWED"},
                  "anchors": [{"pointer": args.pointer, "quote": quote}],
                  "resolution": None, "rationale": None, "interpretations": []}
    else:
        if args.suite is None:
            raise ValueError("A suite is required")
        suite = json.loads(args.suite.read_text())
        binding = json.loads(args.binding.read_text()) if args.binding else None
        result = (development_feedback(raw, binding, suite) if args.action == "feedback"
                  else evaluate(raw, binding, suite))
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("template", "evaluate", "feedback"))
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--suite", type=Path)
    parser.add_argument("--pointer", default="/plan/formulation")
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args())
