"""N-052: ten paired claim-elicitation revisions under delegated subscription budget."""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent / "state-workflow-v0.3"
DESIGN = HERE / "design"
spec = importlib.util.spec_from_file_location("n052_retained_campaign", BASE / "campaign.py")
assert spec and spec.loader
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
transport = base.transport
transport.CODEX = Path("/home/audrey/.codex/packages/standalone/releases/0.156.1-x86_64-unknown-linux-musl/bin/codex")
load_document, save, sha, now = base.load_document, base.save, base.sha, base.now
locked, raw_path, result_path = base.locked, base.raw_path, base.result_path
claims = base.claims
DENOMINATORS = {"self_review": 5, "formalization": 5}
REGRESSION_ROLE = "known_regression_previously_inspected_not_unseen"


def design_slots() -> list[dict[str, Any]]:
    rows = load_document(DESIGN / "prompt-design.json")["slots"]
    return [{"id": r["id"], "replicate": int(r["initial"][:2]), "arm": r["arm"],
             "historical_initial": r["initial"], "initial_sha256": r["initial_sha256"],
             "prompt_sha256": r["prompt_sha256"], "attempt_limit": 1} for r in rows]


def prepare(folder: Path, simulation: bool = False) -> dict[str, Any]:
    old = load_document(BASE / "campaign/protocol.json")
    if sha(transport.CODEX) != old["cli_sha256"]:
        raise ValueError("Pinned installed CLI differs from previously inspected binary")
    sources = dict(old["source_sha256"])
    sources.update(load_document(DESIGN / "source-manifest.json"))
    for source in [BASE / "campaign/protocol.json", DESIGN / "prompt-design.json",
                   *HERE.glob("*.py")]:
        sources[str(source.relative_to(ROOT))] = sha(source)
    for name, digest in sources.items():
        if sha(ROOT / name) != digest:
            raise ValueError(f"Historical dependency changed: {name}")
    slots = design_slots()
    if Counter(s["arm"] for s in slots) != DENOMINATORS:
        raise ValueError("Design must retain all10 planned positions")
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "frozen-inputs").mkdir()
    for s in slots:
        data = (DESIGN / f"{s['id']}.txt").read_bytes()
        if base.hashlib.sha256(data).hexdigest() != s["prompt_sha256"]:
            raise ValueError("Design prompt changed")
        with (folder / "frozen-inputs" / f"{s['id']}.txt").open("xb") as stream:
            stream.write(data)
    protocol = {"version": "claim-elicitation-0.1", "created_utc": now(),
                "run_authorization": None, "simulation": simulation,
                "model": "gpt-5.6-sol", "reasoning_effort": "medium",
                "access": "existing ChatGPT subscription", "maximum_model_calls": 10,
                "maximum_concurrency": 1, "timeout_seconds_per_call": 600,
                "operator_retries": 0, "model_tools": [], "mother_cases": 1,
                "model_seed": None, "temperature": None, "server_snapshot": None,
                "historical_initials": 5, "new_initial_calls": 0,
                "denominators_by_arm": DENOMINATORS, "slots": slots,
                "source_sha256": sources, "cli_sha256": sha(transport.CODEX),
                "cli_version": subprocess.check_output([str(transport.CODEX), "--version"], text=True).strip(),
                "transport_config": transport.CONFIG, "transport_wrapper": transport.WRAPPER,
                "evaluation_role": REGRESSION_ROLE,
                "evaluation_suite": str((base.V2 / "evidence/evaluator-reserved.json").relative_to(ROOT)),
                "final_binding_policy": "All new valid responses bound after queue termination, before regression collection.",
                "reporting": ["S/F each5, all historical drafts retained; paired elicitation diagnostic, equal calls not equal tokens.",
                              "One known failure, one mother case; no independent generalization evidence.",
                              "Insufficient, ambiguous, guarded and contradicted claims remain separate.",
                              "Reviewer transcription is not independent human review or full-task correctness.",
                              "Offline preflight is not account availability or an effect measurement."]}
    save(folder / "protocol.json", protocol)
    return protocol


def verify(folder: Path) -> dict[str, Any]:
    p = load_document(folder / "protocol.json")
    for name, digest in p["source_sha256"].items():
        if sha(ROOT / name) != digest:
            raise ValueError(f"Frozen source changed: {name}")
    fixed = {"version": "claim-elicitation-0.1", "model": "gpt-5.6-sol", "reasoning_effort": "medium",
             "maximum_model_calls": 10, "maximum_concurrency": 1, "timeout_seconds_per_call": 600,
             "operator_retries": 0, "model_tools": [], "new_initial_calls": 0,
             "denominators_by_arm": DENOMINATORS, "slots": design_slots(),
             "evaluation_role": REGRESSION_ROLE,
             "evaluation_suite": str((base.V2 / "evidence/evaluator-reserved.json").relative_to(ROOT)),
             "transport_config": transport.CONFIG, "transport_wrapper": transport.WRAPPER}
    if any(p.get(k) != v for k, v in fixed.items()) or type(p.get("simulation")) is not bool:
        raise ValueError("Frozen protocol layout or execution settings differ")
    if sha(transport.CODEX) != p["cli_sha256"]:
        raise ValueError("Pinned CLI changed")
    for s in p["slots"]:
        if sha(folder / "frozen-inputs" / f"{s['id']}.txt") != s["prompt_sha256"]:
            raise ValueError("Frozen prompt changed")
    return p


def state(folder: Path) -> dict[str, Any]:
    p = load_document(folder / "protocol.json")
    records = {s["id"]: load_document(result_path(folder, s["id"]))
               for s in p["slots"] if result_path(folder, s["id"]).exists()}
    if (folder / "STOP.json").exists() or any(r["status"] == "infrastructure_failure" for r in records.values()):
        for s in p["slots"]:
            records.setdefault(s["id"], {"slot": s["id"], "replicate": s["replicate"], "arm": s["arm"],
                                        "status": "not_run_infrastructure_stop", "task_pass": None})
        return {"state": "stopped", "records": records, "planned": 10}
    for s in p["slots"]:
        if s["id"] not in records:
            status = ("recover_attempt" if (folder / "attempts" / f"{s['id']}.json").exists()
                      else "ready_call" if (folder / "authorization.json").exists() else "await_authorization")
            return {"state": status, "slot": s, "records": records, "planned": 10}
    return {"state": "all_slots_terminal", "records": records, "planned": 10}


def authorized(folder: Path, p: dict[str, Any]) -> None:
    receipt = load_document(folder / "authorization.json")
    required = {"protocol_sha256": sha(folder / "protocol.json"), "maximum_model_calls": 10,
                "model": p["model"], "reasoning_effort": p["reasoning_effort"], "simulation": p["simulation"]}
    if any(receipt.get(k) != v for k, v in required.items()) or not receipt.get("user_instruction"):
        raise ValueError("Authorization does not cover this exact10-call protocol")
    if not p["simulation"]:
        check = load_document(folder / "preflight/passed.json")
        if check.get("protocol_sha256") != required["protocol_sha256"] or check.get("passed") is not True:
            raise ValueError("Matching successful offline preflight required")


def finish_attempt(folder: Path, p: dict[str, Any], s: dict[str, Any]) -> dict[str, Any]:
    attempt = load_document(folder / "attempts" / f"{s['id']}.json")
    if (attempt.get("protocol_sha256") != sha(folder / "protocol.json")
            or attempt.get("input_sha256") != s["prompt_sha256"]
            or sha(folder / "inputs" / f"{s['id']}.txt") != s["prompt_sha256"]):
        raise ValueError("Recovered attempt does not match frozen input/protocol")
    return base.finish_attempt(folder, p, s)


def run_next(folder: Path, fake_transport: Callable[..., Any] | None = None) -> dict[str, Any]:
    with locked(folder):
        p = verify(folder)
        current = state(folder)
        if current["state"] == "recover_attempt":
            return finish_attempt(folder, p, current["slot"])
        if current["state"] != "ready_call":
            raise ValueError(f"Cannot call model: {current['state']}")
        authorized(folder, p)
        if p["simulation"] != (fake_transport is not None):
            raise ValueError("Simulation requires fake transport; live mode requires isolated transport")
        if len(list((folder / "attempts").glob("*.json"))) >= 10:
            raise ValueError("Call budget exhausted")
        s = current["slot"]
        source = folder / "inputs" / f"{s['id']}.txt"
        source.parent.mkdir(exist_ok=True)
        prompt = (folder / "frozen-inputs" / source.name).read_bytes()
        if source.exists():
            if source.read_bytes() != prompt:
                raise ValueError("Staged input changed")
        else:
            with source.open("xb") as stream:
                stream.write(prompt)
        entry = {"case_id": s["id"], "prediction_case_id": "lit-009", "file": source.name,
                 "sha256": s["prompt_sha256"]}
        save(folder / "attempts" / f"{s['id']}.json", {"utc": now(), "input_sha256": sha(source),
             "simulation": p["simulation"], "protocol_sha256": sha(folder / "protocol.json")})
        if fake_transport is not None:
            fake_transport(folder, entry, p)
        else:
            old_here = transport.HERE
            try:
                transport.HERE = folder
                transport.run_case(p["model"], entry, p)
            finally:
                transport.HERE = old_here
        return finish_attempt(folder, p, s)


def bind_final(folder: Path, slot: str, review: dict[str, Any]) -> None:
    with locked(folder):
        verify(folder)
        current = state(folder)
        if current["state"] not in ("all_slots_terminal", "stopped"):
            raise ValueError("Finish the model queue before final binding")
        result = current["records"].get(slot, {})
        if result.get("status") != "valid_response":
            raise ValueError("Bind only a valid new response")
        if sha(raw_path(folder, slot)) != result["response_sha256"]:
            raise ValueError("Response changed after classification")
        base.check_review(raw_path(folder, slot).read_text(), review)
        save(folder / "final-bindings" / f"{slot}.json", review)


def collect_final(folder: Path) -> dict[str, Any]:
    with locked(folder):
        p = verify(folder)
        current = state(folder)
        if current["state"] not in ("all_slots_terminal", "stopped"):
            raise ValueError("Final regression unavailable while revisions remain")
        reviewed = {}
        for s in p["slots"]:
            sid = s["id"]
            if current["records"][sid]["status"] == "valid_response":
                review = load_document(folder / "final-bindings" / f"{sid}.json")
                raw = raw_path(folder, sid).read_text()
                if sha(raw_path(folder, sid)) != current["records"][sid]["response_sha256"]:
                    raise ValueError("Response changed after classification")
                base.check_review(raw, review)
                reviewed[sid] = (raw, review)
        # Reuse immutable data; role is explicitly regression in this prospective protocol.
        suite = load_document(ROOT / p["evaluation_suite"])
        rows = []
        for s in p["slots"]:
            sid = s["id"]
            row = dict(current["records"][sid])
            row["evaluation_role"] = REGRESSION_ROLE
            if sid in reviewed:
                raw, review = reviewed[sid]
                start = time.perf_counter()
                row["evaluation"] = claims.evaluate(raw, review.get("binding"), suite)
                row["evaluation"]["source_suite_role"] = row["evaluation"]["split"]
                row["evaluation"]["split"] = "known_regression"
                row["evaluation_tool_seconds"] = time.perf_counter() - start
                row["review_seconds"] = review["review_seconds"]
                row["reviewer"] = review["reviewer"]
            rows.append(row)
        result = {"protocol_sha256": sha(folder / "protocol.json"), "simulation": p["simulation"],
                  "planned_slots": 10, "denominators_by_arm": DENOMINATORS,
                  "attempts": len(list((folder / "attempts").glob("*.json"))), "task_pass": None,
                  "evaluation_role": REGRESSION_ROLE, "rows": rows,
                  "paired_comparisons": {"formalization_minus_self": [1, 2, 3, 4, 5]},
                  "limits": p["reporting"]}
        save(folder / "final-results.json", result)
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "status", "next", "bind-final", "collect"])
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--slot")
    parser.add_argument("--review-file", type=Path)
    args = parser.parse_args()
    folder = args.campaign.resolve()
    if args.action == "bind-final":
        value = bind_final(folder, args.slot, load_document(args.review_file))
    else:
        value = {"prepare": prepare, "status": state, "next": run_next, "collect": collect_final}[args.action](folder)
    print(json.dumps(value, ensure_ascii=False, indent=2))
