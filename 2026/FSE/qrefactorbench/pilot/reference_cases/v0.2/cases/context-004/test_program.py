"""Check all observable checkpoints, canonical bytes, validation and failure ordering."""

from collections import Counter
from copy import deepcopy
import hashlib
from itertools import accumulate, product
import json
from pathlib import Path
import subprocess
import sys

import pytest
import program


def oracle(request):
    encoded = [json.dumps(event, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode('ascii')
               for event in request["events"]]
    states = list(accumulate(encoded, lambda previous, payload: hashlib.sha256(previous + payload).digest(),
                             initial=bytes(32)))
    counts = Counter(event["component"] for event in request["events"])
    return ({"batch_id": request["batch_id"], "event_count": len(encoded),
             "components": [{"component": name, "event_count": count} for name, count in counts.items()],
             "final_digest": states[-1].hex()}, list(enumerate(state.hex() for state in states[1:])))


def test_bounded_event_sequences_and_full_audit():
    checked = 0
    for n in range(5):
        for variants in product(range(3), repeat=n):
            request = {"batch_id": "batch", "events": [
                {"event_id": f"e{i}", "component": ["z", "a", "z"][variant],
                 "message": ["", "line\nbreak", "更新"][variant]} for i, variant in enumerate(variants)]}
            audit, before = [], deepcopy(request)
            receipt = program.seal_batch(request, lambda i, value: audit.append((i, value)))
            assert (receipt, audit) == oracle(request)
            assert request == before
            checked += 1
    assert checked == 121


def test_canonical_bytes_checked_independently_of_json_encoder():
    request = {"batch_id": "b", "events": [{"message": "x\n\"", "event_id": "e", "component": "中"}]}
    payload = b'{"component":"\\u4e2d","event_id":"e","message":"x\\n\\\""}'
    expected = hashlib.sha256(bytes(32) + payload).hexdigest()
    audit = []
    assert program.seal_batch(request, lambda i, value: audit.append((i, value)))["final_digest"] == expected
    assert audit == [(0, expected)]


@pytest.mark.parametrize("failure_index", range(3))
def test_callback_error_identity_prefix_and_no_later_calls(failure_index):
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    failure, audit = RuntimeError("sink failed"), []

    def sink(i, value):
        audit.append((i, value))
        if i == failure_index:
            raise failure

    with pytest.raises(RuntimeError) as raised:
        program.seal_batch(request, sink)
    assert raised.value is failure
    assert audit == oracle(request)[1][:failure_index + 1]


def invalid_requests():
    event = {"event_id": "e1", "component": "api", "message": "ok"}
    yield None
    yield {}
    yield {"batch_id": "b", "events": [], "extra": True}
    for batch in [None, "", False]:
        yield {"batch_id": batch, "events": []}
    for events in [None, "events", [None], [event, event], [event, {}], [dict(event, event_id="")],
                   [dict(event, component="")], [dict(event, component=[])], [dict(event, message=None)],
                   [dict(event, event_id=True)], [dict(event, extra=1)]]:
        yield {"batch_id": "b", "events": events}


@pytest.mark.parametrize("payload", list(invalid_requests()))
def test_all_validation_before_any_effect(payload):
    audit, before = [], deepcopy(payload)
    with pytest.raises(ValueError):
        program.seal_batch(payload, lambda *args: audit.append(args))
    assert not audit and payload == before


def test_noncallable_sink_and_empty_receipt():
    request = {"batch_id": "b", "events": []}
    with pytest.raises(ValueError):
        program.seal_batch(request, None)
    assert program.seal_batch(request, lambda *_: pytest.fail("No events")) == oracle(request)[0]


def test_final_digest_only_is_insufficient(monkeypatch):
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    real = program.ledger_digest
    monkeypatch.setattr(program, "ledger_digest", lambda payloads, _audit: real(payloads, lambda *_: None))
    audit = []
    receipt = program.seal_batch(request, lambda *args: audit.append(args))
    assert receipt == oracle(request)[0]  # Same final output, but side effects missing.
    assert audit != oracle(request)[1]


def test_event_order_is_observable_and_summary_is_not_enough():
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    changed = deepcopy(request)
    changed["events"] = list(reversed(changed["events"]))
    first = program.seal_batch(request, lambda *_: None)
    second = program.seal_batch(changed, lambda *_: None)
    assert first["components"] == second["components"]
    assert first["final_digest"] != second["final_digest"]


def test_cli():
    request = json.loads(Path(__file__).with_name("example_request.json").read_text())
    command = [sys.executable, str(Path(__file__).with_name("program.py"))]
    result = subprocess.run(command, input=json.dumps(request), text=True, capture_output=True, check=True)
    expected, checkpoints = oracle(request)
    assert json.loads(result.stdout) == {"receipt": expected,
                                       "checkpoints": [{"index": i, "digest": d} for i, d in checkpoints]}
    failure = subprocess.run(command, input='{}', text=True, capture_output=True)
    assert failure.returncode != 0 and not failure.stdout.strip()
