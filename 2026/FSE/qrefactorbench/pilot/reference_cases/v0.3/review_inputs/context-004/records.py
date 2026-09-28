"""Validate change-record batches, encode events and derive component summaries."""

import hashlib
import json
from collections.abc import Callable
from typing import Any


def prepare_request(request: Any) -> tuple[str, list[bytes], list[dict]]:
    if not isinstance(request, dict) or set(request) != {"batch_id", "events"}:
        raise ValueError("Expected batch_id and events")
    batch = request["batch_id"]
    if not isinstance(batch, str) or not batch:
        raise ValueError("batch_id must be a nonempty string")
    if not isinstance(request["events"], list):
        raise ValueError("events must be a list")
    seen, payloads, counts = set(), [], {}
    for event in request["events"]:
        if not isinstance(event, dict) or set(event) != {"event_id", "component", "message"}:
            raise ValueError("Events need event_id, component and message")
        identifier, component, message = event["event_id"], event["component"], event["message"]
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("Event IDs must be unique nonempty strings")
        if not isinstance(component, str) or not component or not isinstance(message, str):
            raise ValueError("component must be nonempty text; message must be text")
        seen.add(identifier)
        counts[component] = counts.get(component, 0) + 1
        payloads.append(json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii"))
    return batch, payloads, [{"component": name, "event_count": count} for name, count in counts.items()]


def ledger_digest(events: list[bytes], audit: Callable[[int, str], None]) -> str:
    digest = bytes(32)
    for index, event in enumerate(events):
        digest = hashlib.sha256(digest + event).digest()
        audit(index, digest.hex())
    return digest.hex()
