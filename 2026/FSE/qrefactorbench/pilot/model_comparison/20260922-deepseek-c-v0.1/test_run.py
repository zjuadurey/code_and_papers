"""Offline transport/collector checks; no live requests, no real credentials."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
import urllib.error
import io

import pytest

SPEC = importlib.util.spec_from_file_location("deepseek_runner", Path(__file__).with_name("run.py"))
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    old = r.load_document(r.OLD / "protocol.json")
    (tmp_path / "inputs").mkdir()
    for entry in old["entries"]:
        (tmp_path / "inputs" / entry["file"]).write_bytes((r.OLD / "inputs" / entry["file"]).read_bytes())
    protocol = {**old, "models": r.MODELS, "thinking": {"type": "enabled"},
                "reasoning_effort": "high", "max_tokens": 16384, "socket_timeout_seconds": 600,
                "comparison_limits": ["SYNTHETIC TEST ONLY"]}
    monkeypatch.setattr(r, "HERE", tmp_path)
    return tmp_path, protocol


def test_payload_is_only_public_input_and_wrapper(setup):
    folder, protocol = setup
    payload = r.payload(protocol, r.MODELS[0], protocol["entries"][0])
    assert set(payload) == {"model", "messages", "thinking", "reasoning_effort", "max_tokens", "stream"}
    assert payload["messages"] == [{"role": "system", "content": protocol["wrapper"]},
                                   {"role": "user", "content": (folder / "inputs/lit-001-C.txt").read_text()}]
    (folder / "inputs/lit-001-C.txt").write_text("changed")
    with pytest.raises(r.DataError):
        r.payload(protocol, r.MODELS[0], protocol["entries"][0])


@pytest.mark.parametrize("finish,tools,complete", [("stop", False, True), ("length", False, False), ("tool_calls", True, False)])
def test_transport_completion_and_no_repair(setup, finish, tools, complete):
    folder, protocol = setup
    key = "sk-" + "x" * 40
    body = {"model": "returned-test-id", "choices": [{"finish_reason": finish,
            "message": {"content": "```json\n{}\n```", "tool_calls": [{}] if tools else []}}],
            "usage": {"total_tokens": 3}}
    with patch.object(r.urllib.request, "build_opener") as factory:
        response = factory.return_value.open.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = json.dumps(body).encode()
        result = r.call(protocol, r.MODELS[0], protocol["entries"][0], key)
        assert factory.return_value.open.call_count == 1
    assert result["response_complete"] == complete
    output = folder / "runs" / r.MODELS[0] / "lit-001"
    assert (output / "response.txt").read_text() == body["choices"][0]["message"]["content"]
    assert all(key not in p.read_text() for p in output.iterdir())


def test_http_error_no_retry_and_credential_echo_redacted(setup):
    folder, protocol = setup
    key = "sk-" + "z" * 40
    with patch.object(r.urllib.request, "build_opener") as factory:
        factory.return_value.open.side_effect = urllib.error.HTTPError(r.ENDPOINT, 429, "test", {}, io.BytesIO(key.encode()))
        record = r.call(protocol, r.MODELS[0], protocol["entries"][0], key)
        assert factory.return_value.open.call_count == 1
    assert record["http_status"] == 429 and not record["response_complete"]
    assert record["credential_echo_redacted"]
    assert key not in (folder / "runs" / r.MODELS[0] / "lit-001/api_response.json").read_text()


def test_redirect_rejected():
    assert r.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.invalid") is None


@pytest.mark.parametrize("invalid", [False, True])
def test_collector_full_population_or_no_score(setup, invalid):
    folder, protocol = setup
    r.save(folder / "protocol.json", protocol)
    r.save(folder / "protected_before.json", {})
    for model in r.MODELS:
        for entry in protocol["entries"]:
            d = folder / "runs" / model / entry["case_id"]
            d.mkdir(parents=True)
            # Historical answers used only as offline shape fixtures, never in payloads.
            raw = (r.OLD / "runs/gpt-6-astra" / entry["case_id"] / "response.txt").read_text()
            if invalid and entry["case_id"] == "lit-001":
                raw = "```json\n" + raw + "\n```"
            (d / "response.txt").write_text(raw)
            r.save(d / "metadata.json", {"response_complete": True, "response_sha256": r.digest(d / "response.txt")})
    with patch.object(r, "verify"):
        r.collect()
    summary = r.load_document(folder / "SUMMARY.json")
    for model in r.MODELS:
        assert summary["models"][model]["valid_responses"] == (9 if invalid else 10)
        assert (folder / f"evaluation.{model}.json").exists() == (not invalid)


def test_run_stops_pair_on_transport_failure_and_cannot_restart(setup):
    folder, protocol = setup
    r.save(folder / "protocol.json", protocol)
    record = {"http_status": 401, "transport_error": None, "unexpected_tool_calls": False, "response_complete": False}
    with patch.object(r, "verify"), patch.object(r, "credential", return_value="offline-key"), patch.object(r, "call", return_value=record) as call:
        r.run(Path("not-read"))
        assert call.call_count == 2
        with pytest.raises(FileExistsError):
            r.run(Path("not-read"))
        assert call.call_count == 2
