"""Bounded DeepSeek first-attempt experiment; preparation/evaluation are offline."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import time
from typing import Any
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = HERE.parent / "20260922-c-v0.1"
MODELS = ["deepseek-v4-pro", "deepseek-flash"]
ENDPOINT = "https://api.deepseek.com/chat/completions"
sys.path.insert(0, str(ROOT))
from qrefactorbench.loader import DataError, load_document
from qrefactorbench.schema import schema_errors

SPEC = importlib.util.spec_from_file_location("pending_evaluation", ROOT / "pilot/provisional_labels/v0.1/evaluate.py")
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def prepare() -> None:
    old = load_document(OLD / "protocol.json")
    evaluation.references("C")
    entries = old["entries"]
    (HERE / "inputs").mkdir()
    for entry in entries:
        source = OLD / "inputs" / entry["file"]
        if digest(source) != entry["sha256"]:
            raise DataError("Original input fingerprint mismatch")
        with (HERE / "inputs" / entry["file"]).open("xb") as handle:
            handle.write(source.read_bytes())
    protected = dict(load_document(OLD / "protected_before.json"))
    protected.update({str(p.relative_to(ROOT)): digest(p) for p in OLD.rglob("*")
                      if p.is_file() and "__pycache__" not in p.parts})
    save(HERE / "protected_before.json", protected)
    save(HERE / "protocol.json", {
        "authorization": "User requested current benchmark LLM comparison, then explicitly added DeepSeek pro and flash and supplied a credential-file path; 10 C cases/model, one attempt each.",
        "models": MODELS, "endpoint": ENDPOINT, "condition": "C", "entries": entries,
        "thinking": {"type": "enabled"}, "reasoning_effort": "high", "max_tokens": 16384,
        "stream": False, "temperature": None, "seed": None, "response_format": None,
        "tools": [], "operator_retries": 0, "concurrency": 2, "socket_timeout_seconds": 600,
        "planned_calls": 20, "wrapper": old["wrapper"], "wrapper_role": "system",
        "runner_sha256": digest(Path(__file__)), "created_utc": now(),
        "reference_labels_sha256": old["reference_labels_sha256"],
        "reference_provenance_sha256": old["reference_provenance_sha256"],
        "documentation": ["https://api-docs.deepseek.com/", "https://api-docs.deepseek.com/quick_start/pricing/",
                          "https://api-docs.deepseek.com/api/create-chat-completion/"],
        "documented_versions_at_preparation": {"deepseek-v4-pro": "DeepSeek-V4-Pro-0813", "deepseek-flash": "DeepSeek-V4.1-Flash"},
        "comparison_limits": ["Same public task bytes and reference; API has no Codex system scaffolding.",
                              "DeepSeek high and GPT medium are not matched reasoning budgets.",
                              "API aliases can move; preserve returned model/fingerprint without claiming pinned weights.",
                              "Output cap differs from unspecified GPT CLI cap; truncation is a failure, never repaired.",
                              "Pending labels, single sample; no stable ranking or whole-task accuracy."]})


def verify(protocol: dict[str, Any]) -> None:
    if protocol["models"] != MODELS or protocol["endpoint"] != ENDPOINT:
        raise DataError("Unexpected provider or experiment models")
    if digest(Path(__file__)) != protocol["runner_sha256"]:
        raise DataError("Runner differs from frozen protocol")
    for entry in protocol["entries"]:
        if digest(HERE / "inputs" / entry["file"]) != entry["sha256"]:
            raise DataError("Public input differs from frozen protocol")
    for name, value in load_document(HERE / "protected_before.json").items():
        if not (ROOT / name).is_file() or digest(ROOT / name) != value:
            raise DataError(f"Protected artifact changed: {name}")
    evaluation.references("C")


def credential(path: Path) -> str:
    # Read only the user-designated file; never log contents or put it in a request body.
    keys = set(re.findall(r"(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{16,}", path.read_text()))
    if len(keys) != 1:
        raise DataError("Credential file must contain exactly one recognizable key; values are not logged")
    return keys.pop()


def payload(protocol: dict[str, Any], model: str, entry: dict[str, Any]) -> dict[str, Any]:
    source = HERE / "inputs" / entry["file"]
    if model not in MODELS or digest(source) != entry["sha256"]:
        raise DataError("Invalid model or changed input")
    return {"model": model, "messages": [{"role": "system", "content": protocol["wrapper"]},
                                          {"role": "user", "content": source.read_text()}],
            "thinking": protocol["thinking"], "reasoning_effort": protocol["reasoning_effort"],
            "max_tokens": protocol["max_tokens"], "stream": False}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def call(protocol: dict[str, Any], model: str, entry: dict[str, Any], key: str) -> dict[str, Any]:
    folder = HERE / "runs" / model / entry["case_id"]
    folder.mkdir(parents=True, exist_ok=False)
    request_body = payload(protocol, model, entry)
    save(folder / "request.json", request_body)  # Public messages/config only.
    record = {"requested_model": model, "mother_case_id": entry["case_id"], "started_utc": now(),
              "input_sha256": entry["sha256"], "request_sha256": digest(folder / "request.json"),
              "operator_retries": 0, "http_status": None, "transport_error": None,
              "response_complete": False, "unexpected_tool_calls": False}
    save(folder / "started.json", record)
    request = urllib.request.Request(ENDPOINT, data=json.dumps(request_body).encode(),
                                    headers={"Content-Type": "application/json", "Authorization": "Bearer " + key}, method="POST")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    start = time.monotonic()
    raw = None
    try:
        with opener.open(request, timeout=protocol["socket_timeout_seconds"]) as response:
            record["http_status"] = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        record["http_status"] = exc.code
        raw = exc.read()
    except (OSError, TimeoutError) as exc:
        record["transport_error"] = type(exc).__name__  # Never serialize request/credentials.
    record.update(elapsed_seconds=round(time.monotonic() - start, 3), finished_utc=now())
    if raw is not None:
        record["credential_echo_redacted"] = key.encode() in raw
        raw = raw.replace(key.encode(), b"[CREDENTIAL_REDACTED]")
        with (folder / "api_response.json").open("xb") as handle:
            handle.write(raw)
        record["api_response_sha256"] = digest(folder / "api_response.json")
        try:
            body = load_document(folder / "api_response.json")
            record.update(returned_model=body.get("model"), system_fingerprint=body.get("system_fingerprint"),
                          response_id=body.get("id"), usage=body.get("usage"))
            choices = body.get("choices", [])
            if len(choices) != 1:
                raise DataError("Expected exactly one completion")
            choice = choices[0]
            message = choice["message"]
            record["finish_reason"] = choice.get("finish_reason")
            record["unexpected_tool_calls"] = bool(message.get("tool_calls") or message.get("function_call"))
            content = message.get("content")
            if isinstance(content, str):
                with (folder / "response.txt").open("x", encoding="utf-8") as handle:
                    handle.write(content)
                record["response_sha256"] = digest(folder / "response.txt")
            record["response_complete"] = (record["http_status"] == 200 and choice.get("finish_reason") == "stop"
                                            and isinstance(content, str) and bool(content.strip())
                                            and not record["unexpected_tool_calls"])
        except (DataError, ValueError, KeyError, TypeError, AttributeError):
            record["envelope_error"] = True
    save(folder / "metadata.json", record)
    print(json.dumps({k: record[k] for k in ("requested_model", "mother_case_id", "http_status", "elapsed_seconds", "response_complete")}), flush=True)
    return record


def run(key_file: Path) -> None:
    protocol = load_document(HERE / "protocol.json")
    verify(protocol)
    key = credential(key_file)
    save(HERE / "run.started.json", {"utc": now(), "planned": 20})
    records = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for entry in protocol["entries"]:
            futures = [pool.submit(call, protocol, model, entry, key) for model in MODELS]
            batch = [future.result() for future in futures]
            records.extend(batch)
            if any(r["http_status"] != 200 or r["transport_error"] or r["unexpected_tool_calls"] or r.get("envelope_error") for r in batch):
                break
    save(HERE / "run.completed.json", {"utc": now(), "attempted": len(records), "planned": 20,
                                       "completed_responses": sum(r["response_complete"] for r in records)})


def collect() -> None:
    protocol = load_document(HERE / "protocol.json")
    verify(protocol)
    _, refs = evaluation.references("C")
    refs = {r["mother_case_id"]: r for r in refs}
    summary = {"review_status": "PENDING", "condition": "C", "models": {}, "planned_calls": 20,
               "comparison_limits": protocol["comparison_limits"],
               "protected_files_unchanged": len(load_document(HERE / "protected_before.json"))}
    for model in MODELS:
        predictions, rows = [], []
        usage = Counter()
        for entry in protocol["entries"]:
            folder = HERE / "runs" / model / entry["case_id"]
            meta = load_document(folder / "metadata.json") if (folder / "metadata.json").exists() else {}
            errors = [] if meta.get("response_complete") else ["API response missing/incomplete/failed"]
            if (folder / "response.txt").exists() and digest(folder / "response.txt") != meta.get("response_sha256"):
                errors.append("Raw response hash mismatch")
            response = None
            try:
                response = load_document(folder / "response.txt")
                shape = schema_errors(response, "prediction")
                errors.extend(shape)
                if not shape:
                    ref = refs[entry["case_id"]]
                    if response.get("schema_version") != "0.2.0" or response["case_id"] != ref["case_id"]:
                        errors.append("Incorrect schema version or case ID")
                    errors.extend(evaluation.region_errors(response["candidate_regions"], ref["sources"]))
                    if response["plan"] and response["migration_family"] is not None and response["plan"]["migration_family"] != response["migration_family"]:
                        errors.append("Top-level and plan families differ")
            except DataError as exc:
                errors.append(str(exc))
            if not errors:
                predictions.append(response)
            usage.update({k: v for k, v in (meta.get("usage") or {}).items() if type(v) is int})
            rows.append({"mother_case_id": entry["case_id"], "valid": not errors, "errors": errors,
                         "elapsed_seconds": meta.get("elapsed_seconds"), "returned_model": meta.get("returned_model"),
                         "finish_reason": meta.get("finish_reason"),
                         **{k: response.get(k) if not errors else None for k in
                            ("structural_eligibility", "practical_suitability", "benchmark_supported", "migration_family", "decision")}})
        save(HERE / f"validation.{model}.json", rows)
        data = {"valid_responses": len(predictions), "population": 10, "rows": rows, "usage": dict(usage),
                "elapsed_seconds_sum": round(sum(r["elapsed_seconds"] or 0 for r in rows), 3),
                "full_population_evaluation_available": len(predictions) == 10}
        if len(predictions) == 10:
            save(HERE / f"predictions.{model}.json", predictions)
            report = evaluation.evaluate(predictions, "C", model + "/high/direct-api")
            save(HERE / f"evaluation.{model}.json", report)
            positive = [r for r in report["results"] if r["plan_required_by_reference"]]
            data.update(aggregate=report["aggregate"], plan_coverage=report["plan_coverage"],
                        decision_agreement=report["decision_agreement"],
                        where_reference_positive={"population": 7,
                          "exact_region_set_matches": sum(r["where_diagnostic"]["candidate_correct"] for r in positive),
                          "mean_line_iou": sum(r["where_diagnostic"]["line_overlap"]["iou"] or 0 for r in positive)/7})
        summary["models"][model] = data
    save(HERE / "SUMMARY.json", summary)
    print(json.dumps({m: {k: v for k, v in d.items() if k not in ("rows", "aggregate")} for m, d in summary["models"].items()}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "collect"))
    parser.add_argument("--key-file", type=Path)
    args = parser.parse_args()
    if args.action == "run":
        if args.key_file is None:
            parser.error("--key-file must name the user-designated credential file")
        run(args.key_file)
    else:
        {"prepare": prepare, "collect": collect}[args.action]()
