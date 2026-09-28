"""Bounded D/S/A/V/AV campaign. No inference without a protocol-bound receipt."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V2 = HERE.parent / "state-workflow-v0.2"
CASE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-009"
ORIGINAL = ROOT / "pilot/reference_completion/v0.1.1/review_inputs/lit-009-C.txt"
PUBLIC = ("program.py", "kernel.py", "common.py")
sys.path.insert(0, str(ROOT))
from qrefactorbench.loader import load_document, DataError
from qrefactorbench.schema import schema_errors
from qrefactorbench.validator import region_errors


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


claims = module("workflow_claims", V2 / "claims.py")
workflow = module("workflow_inventory", HERE.parent / "state-workflow-v0.1/workflow.py")
transport = module("workflow_transport", ROOT / "pilot/model_comparison/20260922-c-v0.1/run.py")
# Sol's bundled catalog forces code-mode/collaboration despite feature=false.
# Pin the bundled entry, clearing tool overrides and apply_patch. No host config edits.
transport.CONFIG = [*transport.CONFIG, 'model_catalog_json="/model-catalog.json"',
                    'tools.update_plan.enabled=false', 'tools.experimental_request_user_input.enabled=false']
_original_isolated = transport.isolated


def isolated_with_catalog(inputs, outputs, args):
    command = _original_isolated(inputs, outputs, args)
    command[1:1] = ["--ro-bind", str(HERE / "tool-free-sol-catalog.json"), "/model-catalog.json"]
    return command


transport.isolated = isolated_with_catalog


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    """Exclusive, atomic publication; a crash cannot leave half a JSON record."""
    path = Path(path)
    data = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.link(temporary, path)  # Fails if a previous immutable record exists.
    finally:
        temporary.unlink()


@contextmanager
def locked(folder):
    with (folder / ".lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def prepare(folder, simulation=False):
    folder.mkdir(parents=True, exist_ok=False)
    p = load_document(V2 / "protocol.proposed.json")
    p.update(version="state-workflow-0.3", simulation=simulation,
             cli_version=subprocess.check_output([str(transport.CODEX), "--version"], text=True).strip(),
             cli_sha256=sha(transport.CODEX), created_utc=now(),
             transport_config=transport.CONFIG, transport_wrapper=transport.WRAPPER,
             final_binding_policy="Initial binding frozen at development review; revision bindings frozen after all slots terminate.",
             authorization_receipt="Separate authorization.json; absent until explicit new user approval.")
    p["limitations"][-1] = "Offline preflight checks isolation, not subscription availability or server behavior."
    p["catalog_overrides"] = {"tool_mode": None, "multi_agent_version": None, "apply_patch_tool_type": None}
    p["catalog_override_reason"] = "Clear bundled forced code-mode/collaboration and patch tool metadata, keeping original model entry otherwise identical."
    for source in [*HERE.glob("*.py"), HERE / "tool-free-sol-catalog.json", HERE / "bundled-sol-metadata.json", *[CASE / f for f in PUBLIC],
                   *list((ROOT / "schemas").glob("*.json")), *[ROOT / "qrefactorbench" / f for f in
                   ("__init__.py", "loader.py", "schema.py", "validator.py")]]:
        p["source_sha256"][str(source.relative_to(ROOT))] = sha(source)
    save(folder / "protocol.json", p)
    return p


def verify(folder):
    p = load_document(folder / "protocol.json")
    for name, expected in p["source_sha256"].items():
        if sha(ROOT / name) != expected:
            raise ValueError(f"Frozen source changed: {name}")
    if sha(transport.CODEX) != p["cli_sha256"]:
        raise ValueError("CLI changed; prepare a new protocol and preflight")
    if p["maximum_model_calls"] != 25 or len(p["slots"]) != 25:
        raise ValueError("Campaign must retain its 25 fixed slots")
    bundled = load_document(HERE / "bundled-sol-metadata.json")
    catalog = load_document(HERE / "tool-free-sol-catalog.json")["models"]
    expected_catalog = {**bundled, **p["catalog_overrides"]}
    if catalog != [expected_catalog]:
        raise ValueError("Catalog differs beyond the declared tool overrides")
    return p


def raw_path(folder, slot):
    return folder / "runs" / "gpt-5.6-sol" / slot / "response.txt"


def result_path(folder, slot):
    return folder / "results" / f"{slot}.json"


def state(folder):
    p = load_document(folder / "protocol.json")
    records = {s["id"]: load_document(result_path(folder, s["id"]))
               for s in p["slots"] if result_path(folder, s["id"]).exists()}
    if (folder / "STOP.json").exists() or any(r["status"] == "infrastructure_failure" for r in records.values()):
        # Even a crash between publishing the failed result and STOP cannot resume calls.
        for s in p["slots"]:
            records.setdefault(s["id"], {"slot": s["id"], "arm": s["arm"], "replicate": s["replicate"],
                                       "status": "not_run_infrastructure_stop", "task_pass": None})
        return {"state": "stopped", "records": records, "planned": 25}
    for s in p["slots"]:
        sid = s["id"]
        if sid in records:
            continue
        if (folder / "attempts" / f"{sid}.json").exists():
            return {"state": "recover_attempt", "slot": s, "records": records}
        if s["arm"] != "initial":
            parent = records[s["depends_on"][0]]
            if parent["status"] != "valid_response":
                return {"state": "skip_parent_failure", "slot": s, "records": records}
            if not (folder / "reviews" / s["depends_on"][0] / "review.json").exists():
                return {"state": "await_development_review", "slot": s, "records": records}
        return {"state": "ready_call" if (folder / "authorization.json").exists()
                else "await_authorization", "slot": s, "records": records}
    return {"state": "all_slots_terminal", "records": records, "planned": 25}


def check_review(raw, review):
    if review.get("response_sha256") != claims.response_digest(raw):
        raise ValueError("Review belongs to a different response")
    reviewer = review.get("reviewer", {})
    if not reviewer.get("identity") or reviewer.get("status") not in ("AI_REVIEW_PENDING", "HUMAN_REVIEWED"):
        raise ValueError("Explicit reviewer identity and status required")
    duration = review.get("review_seconds")
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0:
        raise ValueError("Record actual review duration separately")
    binding = review.get("binding")
    if binding is None:
        if not review.get("unbound_reason"):
            raise ValueError("An unbound response needs an explicit reason")
    else:
        claims.validate_binding(raw, binding)
        if binding["origin"] != "model_response" or binding["reviewer"] != reviewer:
            raise ValueError("Use a model-response binding with the same reviewer")


def analysis_observation(document):
    entries = []
    for region in document["candidate_regions"]:
        if region["file"] not in PUBLIC:
            raise ValueError("Source is outside the public allowlist")
        try:
            value = workflow.analyze_source((CASE / region["file"]).read_text(),
                                            region.get("function"), region["start_line"])
        except (ValueError, TypeError, SyntaxError) as exc:
            value = {"status": "unknown", "reason": str(exc)}
        entries.append({"declared_region": region, "inventory": value})
    return {"kind": "lexical_dependency_inventory", "regions": entries,
            "limits": "Public source only; lexical inventory, not sound slicing, ranges or reachability proof."}


def stage_review(folder, initial, review):
    with locked(folder):
        verify(folder)
        current = state(folder)
        if current["state"] != "await_development_review" or current["slot"]["depends_on"][0] != initial:
            raise ValueError("Not awaiting this initial review")
        start = time.perf_counter()
        raw = raw_path(folder, initial).read_text()
        check_review(raw, review)
        feedback = claims.development_feedback(raw, review.get("binding"), load_document(V2 / "evidence/development.json"))
        inventory = analysis_observation(load_document(raw_path(folder, initial)))
        prompts = {}
        for arm, (use_a, use_v) in workflow.ARMS.items():
            observations = ([inventory] if use_a else []) + ([feedback] if use_v else [])
            prompts[arm] = workflow.revision_prompt(ORIGINAL.read_text(), raw, observations)
        reviews = folder / "reviews"
        reviews.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".staging-", dir=reviews) as tmp:
            temp = Path(tmp)
            save(temp / "review.json", review)
            save(temp / "observations.json", {"analysis": inventory, "verification": feedback,
                                             "tool_seconds": time.perf_counter() - start})
            save(temp / "prompts.json", prompts)
            save(temp / "manifest.json", {"response_sha256": sha(raw_path(folder, initial)),
                 "files": {p.name: sha(p) for p in temp.iterdir() if p.is_file()}})
            # Rename publishes all four branches together. The temp parent remains for cleanup.
            target = reviews / initial
            if target.exists():
                raise FileExistsError(target)
            os.rename(temp, target)


def prompt_for(folder, s):
    if s["arm"] == "initial":
        return ORIGINAL.read_text()
    reviewdir = folder / "reviews" / s["depends_on"][0]
    manifest = load_document(reviewdir / "manifest.json")
    for name, expected in manifest["files"].items():
        if sha(reviewdir / name) != expected:
            raise ValueError("Frozen review/prompt changed")
    if sha(raw_path(folder, s["depends_on"][0])) != manifest["response_sha256"]:
        raise ValueError("Initial response changed")
    return load_document(reviewdir / "prompts.json")[s["arm"]]


def classify(folder, s, meta):
    response = raw_path(folder, s["id"])
    record = {"slot": s["id"], "replicate": s["replicate"], "arm": s["arm"],
              "mother_case": "lit-009", "usage": meta.get("usage", []),
              "model_seconds": meta.get("elapsed_seconds"), "task_pass": None}
    if (meta.get("exit_code") != 0 or meta.get("timeout") or meta.get("errors")
            or meta.get("tool_items") or meta.get("invalid_event_lines") or not meta.get("turn_completed")):
        record.update(status="infrastructure_failure", reason="Transport, timeout, tool use or incomplete turn; inspect retained metadata")
    elif not response.exists():
        record.update(status="missing_response", reason="No final output; budget cause not inferred")
    else:
        if sha(response) != meta.get("raw_output_sha256"):
            raise ValueError("Response digest mismatch")
        record["response_sha256"] = sha(response)
        try:
            document = load_document(response)
            errors = schema_errors(document, "prediction")
            if not errors:
                if document.get("case_id") != "lit-009" or document.get("schema_version") != "0.2.0":
                    errors.append("Wrong case/schema")
                errors += region_errors(document["candidate_regions"], {"files": list(PUBLIC)}, CASE)
                if document.get("plan") and document["plan"]["migration_family"] != document["migration_family"]:
                    errors.append("Plan family mismatch")
        except DataError as exc:
            errors = [str(exc)]
        record.update(status="invalid_response" if errors else "valid_response", validation_errors=errors)
    return record


def stop_remaining(folder, p, cause):
    save(folder / "STOP.json", {"cause": cause, "utc": now()})
    for s in p["slots"]:
        if not result_path(folder, s["id"]).exists():
            save(result_path(folder, s["id"]), {"slot": s["id"], "arm": s["arm"], "replicate": s["replicate"],
                 "status": "not_run_infrastructure_stop", "task_pass": None})


def finish_attempt(folder, p, s):
    attempt = load_document(folder / "attempts" / f"{s['id']}.json")
    meta_path = raw_path(folder, s["id"]).parent / "metadata.json"
    if not meta_path.exists():
        raise RuntimeError("Attempt was started but completion is unknown. Never reissue; inspect process/retained artifacts.")
    meta = load_document(meta_path)
    if meta.get("input_sha256") != attempt["input_sha256"]:
        raise ValueError("Attempt metadata/input mismatch")
    result = classify(folder, s, meta)
    save(result_path(folder, s["id"]), result)
    if result["status"] == "infrastructure_failure":
        stop_remaining(folder, p, s["id"])
    return result


def authorized(folder, p):
    receipt = load_document(folder / "authorization.json")
    required = {"protocol_sha256": sha(folder / "protocol.json"), "maximum_model_calls": 25,
                "model": "gpt-5.6-sol", "reasoning_effort": "medium", "simulation": p["simulation"]}
    if any(receipt.get(k) != v for k, v in required.items()) or not receipt.get("user_instruction"):
        raise ValueError("Authorization receipt does not cover this exact protocol")
    if not p["simulation"]:
        preflight = load_document(folder / "preflight/passed.json")
        if preflight.get("protocol_sha256") != required["protocol_sha256"] or not preflight.get("passed"):
            raise ValueError("Matching successful offline preflight required")


def run_next(folder, fake_transport=None):
    with locked(folder):
        p = verify(folder)
        current = state(folder)
        if current["state"] == "recover_attempt":
            return finish_attempt(folder, p, current["slot"])
        if current["state"] == "skip_parent_failure":
            s = current["slot"]
            r = {"slot": s["id"], "arm": s["arm"], "replicate": s["replicate"],
                 "status": "not_run_parent_failure", "task_pass": None}
            save(result_path(folder, s["id"]), r)
            return r
        if current["state"] != "ready_call":
            raise ValueError(f"Cannot call model: {current['state']}")
        authorized(folder, p)
        if p["simulation"] != (fake_transport is not None):
            raise ValueError("Simulation must use fake transport; live mode must use the isolated transport")
        s = current["slot"]
        prompt = prompt_for(folder, s)
        input_dir = folder / "inputs"
        input_dir.mkdir(exist_ok=True)
        source = input_dir / f"{s['id']}.txt"
        if source.exists():
            if source.read_text() != prompt:
                raise ValueError("Staged input changed")
        else:
            with source.open("x") as stream:
                stream.write(prompt)
        entry = {"case_id": s["id"], "prediction_case_id": "lit-009", "file": source.name, "sha256": sha(source)}
        if len(list((folder / "attempts").glob("*.json"))) >= 25:
            raise ValueError("Call budget exhausted")
        save(folder / "attempts" / f"{s['id']}.json", {"utc": now(), "input_sha256": sha(source),
             "simulation": p["simulation"], "protocol_sha256": sha(folder / "protocol.json")})
        # The marker is durable BEFORE spawning. Exceptions never remove it.
        if fake_transport:
            fake_transport(folder, entry, p)
        else:
            old_here = transport.HERE
            try:
                transport.HERE = folder
                transport.run_case(p["model"], entry, p)
            finally:
                transport.HERE = old_here
        return finish_attempt(folder, p, s)


def bind_final(folder, slot, review):
    with locked(folder):
        verify(folder)
        current = state(folder)
        if current["state"] not in ("all_slots_terminal", "stopped"):
            raise ValueError("Finish the model queue before final revision binding")
        result = current["records"].get(slot, {})
        if result.get("status") != "valid_response" or result.get("arm") == "initial":
            raise ValueError("Bind a valid revision; initial binding is frozen at development review")
        check_review(raw_path(folder, slot).read_text(), review)
        save(folder / "final-bindings" / f"{slot}.json", review)


def collect_final(folder):
    with locked(folder):
        p = verify(folder)
        current = state(folder)
        if current["state"] not in ("all_slots_terminal", "stopped"):
            raise ValueError("Final evaluation is unavailable while revisions remain")
        reviewed = {}
        # Require all bindings before opening the reserved suite. No iterative test-and-rebind.
        for s in p["slots"]:
            sid = s["id"]
            if current["records"][sid]["status"] == "valid_response":
                path = (folder / "reviews" / sid / "review.json" if s["arm"] == "initial"
                        else folder / "final-bindings" / f"{sid}.json")
                review = load_document(path)
                raw = raw_path(folder, sid).read_text()
                if sha(raw_path(folder, sid)) != current["records"][sid]["response_sha256"]:
                    raise ValueError("Response changed after classification")
                check_review(raw, review)
                reviewed[sid] = (raw, review)
        suite = load_document(V2 / "evidence/evaluator-reserved.json")
        rows = []
        for s in p["slots"]:
            sid = s["id"]
            row = dict(current["records"][sid])
            if sid in reviewed:
                raw, review = reviewed[sid]
                start = time.perf_counter()
                row["evaluation"] = claims.evaluate(raw, review.get("binding"), suite)
                row["evaluation_tool_seconds"] = time.perf_counter() - start
                row["review_seconds"] = review["review_seconds"]
                row["reviewer"] = review["reviewer"]
                if s["arm"] == "initial":
                    row["development_tool_seconds"] = load_document(folder / "reviews" / sid / "observations.json")["tool_seconds"]
            rows.append(row)
        result = {"protocol_sha256": sha(folder / "protocol.json"), "simulation": p["simulation"],
                  "fixed_denominator_per_arm": 5, "planned_slots": 25, "task_pass": None,
                  "attempts": len(list((folder / "attempts").glob("*.json"))), "rows": rows,
                  "limits": p["reporting"]}
        save(folder / "final-results.json", result)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "status", "next", "review", "bind-final", "collect"))
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--slot")
    parser.add_argument("--review-file", type=Path)
    args = parser.parse_args()
    folder = args.campaign.resolve()
    if args.action == "prepare":
        value = prepare(folder)
    elif args.action == "status":
        value = state(folder)
    elif args.action == "next":
        value = run_next(folder)
    elif args.action in ("review", "bind-final"):
        value = (stage_review if args.action == "review" else bind_final)(folder, args.slot, load_document(args.review_file))
    else:
        value = collect_final(folder)
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
