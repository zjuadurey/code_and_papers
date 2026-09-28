"""Seal a change-record batch with ordered checkpoints and a component receipt."""

from collections.abc import Callable
import json
import sys
from typing import Any

from records import ledger_digest, prepare_request


def seal_batch(request: Any, audit: Callable[[int, str], None]) -> dict:
    batch, payloads, components = prepare_request(request)
    if not callable(audit):
        raise ValueError("audit must be callable")
    final_digest = ledger_digest(payloads, audit)
    return {"batch_id": batch, "event_count": len(payloads), "components": components,
            "final_digest": final_digest}


if __name__ == "__main__":
    checkpoints = []
    receipt = seal_batch(json.load(sys.stdin), lambda index, digest: checkpoints.append({"index": index, "digest": digest}))
    print(json.dumps({"receipt": receipt, "checkpoints": checkpoints}, indent=2))
