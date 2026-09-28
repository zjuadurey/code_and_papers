"""One-off subscription connectivity probes; no benchmark inputs or API keys."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone

root = Path(tempfile.mkdtemp(prefix="qrb-subscription-smoke-20260922-"))
print(json.dumps({"artifact_directory": str(root)}), flush=True)
environment = os.environ.copy()
for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN", "OPENAI_FEDERATION_RULE_ID",
            "OPENAI_IDENTITY_TOKEN_FILE", "OPENAI_WORKLOAD_IDENTITY_CONTEXT", "OPENAI_BASE_URL"):
    environment.pop(key, None)
prompt = "Return exactly SUBSCRIPTION_SMOKE_OK and nothing else. Do not use tools.\n"
(root / "prompt.txt").write_text(prompt)
disabled = ("shell_tool", "unified_exec", "multi_agent", "multi_agent_v2", "apps", "plugins", "hooks",
            "memories", "shell_snapshot", "skill_search", "skill_mcp_dependency_install", "browser_use",
            "browser_use_external", "computer_use", "in_app_browser", "image_generation", "view_image",
            "code_mode", "code_mode_host", "goals", "sleep_tool", "tool_suggest",
            "unbounded_connection_retries", "workspace_dependencies")
config = ['model_provider="openai"', 'forced_login_method="chatgpt"', 'model_reasoning_effort="medium"',
          'approval_policy="never"', 'web_search="disabled"', 'project_doc_max_bytes=0',
          'features.skip_host_skill_discovery=true',
          'developer_instructions="This is a connectivity check. Do not use tools, inspect files, delegate, or send intermediate messages. Return only the requested final text."']
config += [f"features.{name}=false" for name in disabled]
options = [part for value in config for part in ("-c", value)]
login = subprocess.run(["codex", *options, "login", "status"],
                       env=environment, capture_output=True, text=True, timeout=20)
login_text = login.stdout + login.stderr
(root / "login-status.txt").write_text(login_text)
if login.returncode or "Logged in using ChatGPT" not in login_text:
    raise SystemExit("ChatGPT subscription login not confirmed; no inference requested")
version = subprocess.check_output(["codex", "--version"], text=True).strip()
for model in ("gpt-5.6-sol", "gpt-6-astra"):
    folder = root / model
    folder.mkdir()
    cwd = folder / "empty-workdir"
    cwd.mkdir()
    command = ["codex", "exec", "--ignore-user-config", "--ignore-rules", "--strict-config",
               "--ephemeral", "--sandbox", "read-only", "--skip-git-repo-check", "--model", model,
               *options, "--color", "never", "--json", "--output-last-message", str(folder / "response.txt"), "-"]
    metadata = {"requested_model": model, "cli_version": version, "reasoning_effort": "medium",
                "authentication": "saved ChatGPT login; API key and token override variables removed",
                "started_utc": datetime.now(timezone.utc).isoformat(), "command": command,
                "operator_retries": 0, "timeout_seconds": 120,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "benchmark_case_calls": 0, "server_snapshot": None,
                "isolation": "empty cwd, project docs disabled, user config ignored, tools disabled; not a filesystem namespace"}
    (folder / "started.json").write_text(json.dumps(metadata, indent=2) + "\n")
    start = time.monotonic()
    with (folder / "events.jsonl").open("wb") as stdout, (folder / "stderr.txt").open("wb") as stderr:
        process = subprocess.Popen(command, cwd=cwd, env=environment, stdin=subprocess.PIPE,
                                   stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            process.communicate(prompt.encode(), timeout=120)
            timed_out = False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            timed_out = True
    events, invalid_lines = [], 0
    for line in (folder / "events.jsonl").read_text().splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            invalid_lines += 1
    items = [event.get("item", {}) for event in events if event.get("type", "").startswith("item.")]
    non_message_items = [item for item in items if item.get("type") not in ("agent_message", "reasoning")]
    response = (folder / "response.txt").read_text() if (folder / "response.txt").exists() else None
    metadata.update(exit_code=process.returncode, timed_out=timed_out,
                    elapsed_seconds=round(time.monotonic()-start, 3),
                    response=response, event_types=[e.get("type") for e in events],
                    non_message_items=non_message_items, invalid_event_lines=invalid_lines,
                    usage=[e.get("usage") for e in events if e.get("type") == "turn.completed"],
                    errors=[e for e in events if e.get("type") in ("error", "turn.failed")],
                    passed=process.returncode == 0 and response is not None and response.strip() == "SUBSCRIPTION_SMOKE_OK" and not non_message_items)
    (folder / "result.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({k: metadata[k] for k in ("requested_model", "exit_code", "elapsed_seconds", "passed", "response", "errors")}), flush=True)
(root / "runner.py").write_bytes(Path(__file__).read_bytes())
print(json.dumps({"complete": True, "artifact_directory": str(root)}), flush=True)
