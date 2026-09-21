"""Bounded, isolated first-attempt comparison; authorized 2026-09-22 only."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODELS = ("gpt-5.6-sol", "gpt-6-astra")
CODEX = Path("/home/audrey/.local/bin/codex").resolve()
USER_HOME = Path.home()
AUTH = USER_HOME / ".codex/auth.json"
WRAPPER = (
    "This is a restricted single-turn research baseline. All task information is "
    "in the supplied user message. Do not invoke tools, browse files or the web, "
    "execute code, delegate, request clarification, or produce interim messages. "
    "Return one final response to the supplied prompt. Do not use previous sessions."
)
DISABLED = (
    "shell_tool", "unified_exec", "multi_agent", "multi_agent_v2", "apps", "plugins", "hooks",
    "memories", "shell_snapshot", "skill_search", "skill_mcp_dependency_install", "browser_use",
    "browser_use_external", "computer_use", "in_app_browser", "image_generation", "view_image",
    "code_mode", "code_mode_host", "goals", "sleep_tool", "tool_suggest",
    "unbounded_connection_retries", "workspace_dependencies",
)
CONFIG = [
    'model_provider="openai"', 'forced_login_method="chatgpt"', 'model_reasoning_effort="medium"',
    'approval_policy="never"', 'web_search="disabled"', 'project_doc_max_bytes=0',
    'personality="none"', 'features.skip_host_skill_discovery=true',
    'developer_instructions=' + json.dumps(WRAPPER),
    *[f"features.{name}=false" for name in DISABLED],
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def config_args() -> list[str]:
    return [part for value in CONFIG for part in ("-c", value)]


def isolated(input_dir: Path, output_dir: Path, arguments: list[str]) -> list[str]:
    """Do not mount research data, previous outputs, user config or session history."""
    resolver = str(Path("/etc/resolv.conf").resolve())
    return [
        "/usr/bin/bwrap", "--die-with-parent", "--new-session", "--unshare-pid", "--unshare-ipc",
        "--unshare-uts", "--clearenv", "--ro-bind", "/usr", "/usr", "--symlink", "usr/bin", "/bin",
        "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib64", "/lib64", "--ro-bind", "/etc", "/etc",
        "--dir", "/mnt/wsl", "--ro-bind", resolver, resolver, "--proc", "/proc", "--dev", "/dev",
        "--tmpfs", "/tmp", "--tmpfs", "/home", "--dir", str(USER_HOME / ".codex"),
        "--ro-bind", str(AUTH), str(AUTH), "--ro-bind", str(CODEX), "/codex",
        "--ro-bind", str(input_dir), "/work", "--bind", str(output_dir), "/out",
        "--setenv", "HOME", str(USER_HOME), "--setenv", "PATH", "/usr/bin:/bin",
        "--setenv", "LANG", "C.UTF-8", "--chdir", "/work", "/codex", *arguments,
    ]


def prepare() -> None:
    manifest_path = ROOT / "pilot/reference_completion/v0.1.1/review_inputs/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    entries = [entry for entry in manifest["conditions"] if entry["condition"] == "C"]
    assert len(entries) == 10
    (HERE / "inputs").mkdir()
    for entry in entries:
        source = manifest_path.parent / entry["file"]
        assert digest(source) == entry["sha256"]
        with (HERE / "inputs" / entry["file"]).open("xb") as handle:
            handle.write(source.read_bytes())
    protected = {
        str(path.relative_to(ROOT)): digest(path)
        for folder in ("pilot/reference_completion", "pilot/provisional_labels", "schemas", "qrefactorbench")
        for path in (ROOT / folder).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and ".pytest_cache" not in path.parts
    }
    save(HERE / "protected_before.json", protected)
    save(HERE / "protocol.json", {
        "authorization": "2026-09-22 user: 用当前benchmark跑一下llm测试，给我一个小报告; preceding two-model C-condition plan.",
        "models": MODELS, "condition": "C", "cases_per_model": 10, "attempts_per_case": 1,
        "max_concurrency": 2, "reasoning_effort": "medium", "timeout_seconds": 600,
        "cli_version": subprocess.check_output([str(CODEX), "--version"], text=True).strip(),
        "entries": entries, "input_manifest_sha256": digest(manifest_path),
        "reference_labels_sha256": digest(ROOT / "pilot/provisional_labels/v0.1/labels.json"),
        "reference_provenance_sha256": digest(ROOT / "pilot/provisional_labels/v0.1/provenance.json"),
        "wrapper": WRAPPER, "config": CONFIG, "runner_sha256": digest(Path(__file__)),
        "temperature": None, "seed": None, "max_output_tokens": None,
        "sampling_note": "Unspecified CLI/provider defaults; no deterministic sampling claim.",
        "server_snapshot": None, "created_utc": datetime.now(timezone.utc).isoformat(),
    })


def preflight() -> None:
    folder = HERE / "preflight"
    folder.mkdir()
    with tempfile.TemporaryDirectory(prefix="qrb-compare-preflight-") as temp:
        temp = Path(temp)
        inputs, outputs = temp / "input", temp / "output"
        inputs.mkdir(); outputs.mkdir()
        commands = {"login": [*config_args(), "login", "status"],
                    "features": [*config_args(), "features", "list"]}
        commands.update({model: ["-m", model, *config_args(), "debug", "prompt-input", "PREFLIGHT_ONLY"] for model in MODELS})
        records = []
        for name, args in commands.items():
            result = subprocess.run(isolated(inputs, outputs, args), capture_output=True, timeout=60)
            (folder / f"{name}.stdout").write_bytes(result.stdout)
            (folder / f"{name}.stderr").write_bytes(result.stderr)
            records.append({"check": name, "exit_code": result.returncode})
            if result.returncode:
                save(folder / "failed.json", records)
                raise RuntimeError(f"Preflight failed: {name}")
            if name == "login":
                assert b"Logged in using ChatGPT" in result.stdout + result.stderr
            if name in MODELS:
                text = result.stdout.decode()
                json.loads(text)
                assert "provisional_labels" not in text and "reference_completion" not in text
                assert "FSE 工作区入口" not in text and "QRefactorBench" not in text
        save(folder / "passed.json", {"checks": records, "model_inference_calls": 0,
             "notes": "Generic built-in Codex instructions can remain; repository/private references absent."})


def run_case(model: str, entry: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    target = HERE / "runs" / model / entry["case_id"]
    target.mkdir(parents=True, exist_ok=False)
    source = HERE / "inputs" / entry["file"]
    assert digest(source) == entry["sha256"]
    prompt = source.read_bytes()
    with tempfile.TemporaryDirectory(prefix="qrb-compare-case-") as temp:
        temp = Path(temp)
        inputs, outputs = temp / "input", temp / "output"
        inputs.mkdir(); outputs.mkdir()
        (inputs / "prompt.txt").write_bytes(prompt)
        args = ["exec", "--ignore-user-config", "--ignore-rules", "--strict-config", "--ephemeral",
                "--sandbox", "read-only", "--skip-git-repo-check", "--model", model, *config_args(),
                "--color", "never", "--json", "--output-last-message", "/out/response.txt", "-"]
        command = isolated(inputs, outputs, args)
        record = {"model": model, "mother_case_id": entry["case_id"], "condition": "C",
                  "prediction_case_id": entry["prediction_case_id"], "input_sha256": entry["sha256"],
                  "cli_version": protocol["cli_version"], "reasoning_effort": "medium",
                  "command": command, "operator_retries": 0, "started_utc": datetime.now(timezone.utc).isoformat(),
                  "server_snapshot": None}
        save(target / "started.json", record)
        start = time.monotonic()
        with (target / "events.jsonl").open("xb") as stdout, (target / "stderr.txt").open("xb") as stderr:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, start_new_session=True)
            timed_out = False
            try:
                process.communicate(prompt, timeout=600)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        record.update(exit_code=process.returncode, timeout=timed_out,
                      elapsed_seconds=round(time.monotonic()-start, 3), finished_utc=datetime.now(timezone.utc).isoformat())
        if (outputs / "response.txt").exists():
            with (target / "response.txt").open("xb") as handle:
                handle.write((outputs / "response.txt").read_bytes())
            record["raw_output_sha256"] = digest(target / "response.txt")
        events = []
        for line in (target / "events.jsonl").read_text().splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                record["invalid_event_lines"] = record.get("invalid_event_lines", 0) + 1
        items = [event["item"] for event in events if "item" in event]
        record["tool_items"] = [item for item in items if item.get("type") not in ("agent_message", "reasoning", "error")]
        record["startup_warnings"] = [item for item in items if item.get("type") == "error"]
        record["errors"] = [event for event in events if event.get("type") in ("error", "turn.failed")]
        record["usage"] = [event["usage"] for event in events if "usage" in event]
        record["turn_completed"] = any(event.get("type") == "turn.completed" for event in events)
        record["parse_status"] = "missing"
        if (target / "response.txt").exists():
            try:
                value = json.loads((target / "response.txt").read_bytes())
                record["parse_status"] = "json_object" if isinstance(value, dict) else "json_non_object"
            except (ValueError, UnicodeError):
                record["parse_status"] = "invalid_json"
        save(target / "metadata.json", record)
        print(json.dumps({key: record[key] for key in ("model", "mother_case_id", "exit_code", "elapsed_seconds", "parse_status")}), flush=True)
        return record


def run() -> None:
    assert (HERE / "preflight/passed.json").exists()
    protocol = json.loads((HERE / "protocol.json").read_text())
    assert digest(Path(__file__)) == protocol["runner_sha256"]
    save(HERE / "run.started.json", {"utc": datetime.now(timezone.utc).isoformat(), "authorization_scope": "20 first attempts only"})
    records = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for entry in protocol["entries"]:
            futures = [pool.submit(run_case, model, entry, protocol) for model in MODELS]
            batch = [future.result() for future in futures]
            records.extend(batch)
            # Stop rather than consuming the remaining queue on account/transport failures.
            if any(record["exit_code"] != 0 or record["errors"] or record["tool_items"] for record in batch):
                break
    save(HERE / "run.completed.json", {"utc": datetime.now(timezone.utc).isoformat(),
                                       "attempted": len(records), "planned": 20,
                                       "completed_turns": sum(r["turn_completed"] for r in records)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "preflight", "run"))
    action = parser.parse_args().action
    {"prepare": prepare, "preflight": preflight, "run": run}[action]()
