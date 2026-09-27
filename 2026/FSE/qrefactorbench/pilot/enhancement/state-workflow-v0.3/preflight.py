"""Offline isolation probe: dummy credentials, unshared network, zero inference."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import campaign as c


def validate_wire(request, prompt):
    specifications = list(request.get("tools", []))
    for item in request.get("input", []):
        if item.get("type") == "additional_tools":
            specifications.extend(item.get("tools", []))
    if specifications:
        raise ValueError("Serialized request includes tools (including additional_tools)")
    if request.get("model") != "gpt-5.6-sol" or request.get("reasoning", {}).get("effort") != "medium":
        raise ValueError("Wire model/effort differs from protocol")
    messages = request.get("input", [])
    texts = [part.get("text", "") for m in messages for part in m.get("content", []) if isinstance(part, dict)]
    if prompt not in texts or c.transport.WRAPPER not in texts:
        raise ValueError("Exact public task or restricted wrapper missing from serialized request")
    if any(m.get("role") == "assistant" for m in messages):
        raise ValueError("Unexpected response history")
    if any(marker in json.dumps(request, ensure_ascii=False) for marker in
           ("MUST_NOT_BE_VISIBLE_N047", "evaluator-reserved", "FSE 工作区入口", "Audrey 的全局")):
        raise ValueError("Private content in request")


def run(folder):
    with c.locked(folder):
        p = c.verify(folder)
        target = folder / "preflight"
        target.mkdir()
        checks = []
        with tempfile.TemporaryDirectory(prefix="qrb-offline-preflight-") as tmp:
            temp = Path(tmp)
            inputs, outputs = temp / "input", temp / "output"
            inputs.mkdir()
            outputs.mkdir()
            prompt = c.ORIGINAL.read_text()
            (inputs / "prompt.txt").write_text(prompt)
            dummy = temp / "dummy-auth.json"
            dummy.write_text("{}\n")
            canary = temp / "PRIVATE-CANARY.txt"
            canary.write_text("MUST_NOT_BE_VISIBLE_N047")

            def command(args, executable="/codex"):
                cmd = c.transport.isolated(inputs, outputs, args)
                # Same mounts as live transport, except dummy auth and no network.
                index = cmd.index(str(c.transport.AUTH))
                cmd[index] = str(dummy)
                cmd.insert(1, "--unshare-net")
                if executable != "/codex":
                    cmd[len(cmd) - len(args) - 1] = executable
                return cmd

            def check(name, args, executable="/codex"):
                result = subprocess.run(command(args, executable), capture_output=True, timeout=45)
                (target / f"{name}.stdout").write_bytes(result.stdout)
                (target / f"{name}.stderr").write_bytes(result.stderr)
                for source in outputs.glob("capture*"):
                    (target / source.name).write_bytes(source.read_bytes())
                checks.append({"check": name, "exit_code": result.returncode})
                if result.returncode:
                    c.save(target / "failed.json", {"checks": checks, "model_inference_calls": 0})
                    raise RuntimeError(f"Offline preflight failed: {name}; inspect retained stderr")
                return result.stdout.decode()

            probe = "import json,os; from pathlib import Path; " + \
                "print(json.dumps({'work_files':sorted(p.name for p in Path('/work').iterdir())," + \
                "'forbidden_visible':[p for p in " + repr([str(c.ROOT), str(c.ROOT.parent / 'paper'), str(canary),
                str(c.transport.USER_HOME / '.codex/config.toml')]) + \
                " if Path(p).exists()], 'environment_keys':sorted(os.environ), 'pwd':os.environ.get('PWD')," + \
                "'network_interfaces':sorted(p.name for p in Path('/sys/class/net').iterdir()) if Path('/sys/class/net').exists() else []}))"
            filesystem = json.loads(check("filesystem", ["-c", probe], "/usr/bin/python3"))
            if filesystem["work_files"] != ["prompt.txt"] or filesystem["forbidden_visible"]:
                raise ValueError("Private filesystem visible")
            if set(filesystem["environment_keys"]) - {"HOME", "PATH", "LANG", "LC_CTYPE", "PWD"} or filesystem["pwd"] != "/work":
                raise ValueError("Unexpected inherited environment")
            # 0.156.1 rejects --strict-config on features/debug, so only exec uses it.
            features = check("features", [*c.transport.config_args(), "features", "list"])
            rendered = check("prompt-input", ["-m", p["model"], *c.transport.config_args(),
                             "debug", "prompt-input", prompt])
            messages = json.loads(rendered)
            if not isinstance(messages, list):
                raise ValueError("Unexpected prompt-input format")
            # Inspect all model-visible messages, not just our user payload.
            serialized = json.dumps(messages, ensure_ascii=False)
            for forbidden in ("MUST_NOT_BE_VISIBLE_N047", "evaluator-reserved", "FSE 工作区入口", "Audrey 的全局"):
                if forbidden in serialized:
                    raise ValueError(f"Unexpected prompt content: {forbidden}")
            if prompt not in [part.get("text") for m in messages for part in m.get("content", []) if isinstance(part, dict)]:
                raise ValueError("The exact public prompt is absent")
            if c.transport.WRAPPER not in serialized:
                raise ValueError("Restricted developer wrapper absent")
            enabled = []
            for line in features.splitlines():
                parts = line.split()
                if parts and parts[0] in c.transport.DISABLED and parts[-1] != "false":
                    enabled.append(parts[0])
            # A feature flag is not a tool schema. Inspect the actual serialized tools.
            capture = json.loads(check("request-capture", ["-c", (c.HERE / "capture_request.py").read_text(),
                                                           json.dumps(c.transport.CONFIG)], "/usr/bin/python3"))
            for source in outputs.glob("capture*"):
                (target / source.name).write_bytes(source.read_bytes())
            if capture.get("tools") != []:
                raise ValueError(f"Serialized tools are not empty: {capture.get('tools')}")
            validate_wire(json.loads((outputs / "captured-request.json").read_text()), prompt)
            help_text = check("exec-help", ["exec", "--ignore-user-config", "--ignore-rules", "--strict-config", "--help"])
            for flag in ("--ignore-user-config", "--ignore-rules", "--ephemeral", "--output-last-message"):
                if flag not in help_text:
                    raise ValueError(f"Required exec option missing: {flag}")
        result = {"passed": True, "protocol_sha256": c.sha(folder / "protocol.json"),
                  "cli_version": p["cli_version"], "cli_sha256": p["cli_sha256"], "checks": checks,
                  "model_inference_calls": 0, "real_credentials_read": False,
                  "network": "unshare-net; no external interfaces mounted", "filesystem": filesystem,
                  "prompt_sha256": c.sha(c.ORIGINAL), "model_visible_messages": len(messages),
                  "feature_overrides_not_reflected": enabled, "request_capture": capture,
                  "limits": "Local sink replaces provider/auth routing and disables wire compression; no inference. Built-in instructions may remain. No account/service availability tested; live events still checked for tool use."}
        c.save(target / "passed.json", result)
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    print(json.dumps(run(parser.parse_args().campaign.resolve()), indent=2))
