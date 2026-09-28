"""Run INSIDE the network namespace; capture CLI serialization, no model server."""
import http.server
import json
from pathlib import Path
import subprocess
import sys
import threading


class Sink(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        # Compression is disabled solely for this local wire inspection.
        request = json.loads(body)
        Path("/out/captured-request.json").write_text(json.dumps(request, indent=2))
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":{"message":"OFFLINE_CAPTURE_ONLY_NO_MODEL","type":"invalid_request_error"}}')


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Sink)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}/v1"
config = json.loads(sys.argv[1])
args = ["/codex", "exec", "--ignore-user-config", "--ignore-rules", "--strict-config", "--ephemeral",
        "--sandbox", "read-only", "--skip-git-repo-check", "--model", "gpt-5.6-sol",
        *[part for value in config for part in ("-c", value)],
        "-c", 'model_provider="offline_capture"',
        "-c", 'features.enable_request_compression=false',
        "-c", 'model_providers.offline_capture={name="offline_capture",base_url=' + json.dumps(base)
        + ',wire_api="responses",requires_openai_auth=false,request_max_retries=0,stream_max_retries=0}',
        "--color", "never", "--json", "--output-last-message", "/out/response.txt", "-"]
try:
    result = subprocess.run(args, input=Path("/work/prompt.txt").read_bytes(), capture_output=True, timeout=35)
    stdout, stderr, exit_code = result.stdout, result.stderr, result.returncode
except subprocess.TimeoutExpired as exc:
    stdout, stderr, exit_code = exc.stdout or b"", exc.stderr or b"", 124
Path("/out/capture-cli.stdout").write_bytes(stdout)
Path("/out/capture-cli.stderr").write_bytes(stderr)
server.shutdown()
request_path = Path("/out/captured-request.json")
if not request_path.exists():
    print(json.dumps({"captured": False, "exit_code": exit_code}))
    sys.exit(1)
request = json.loads(request_path.read_text())
specifications = list(request.get("tools", []))
for item in request.get("input", []):
    if item.get("type") == "additional_tools":
        specifications.extend(item.get("tools", []))
print(json.dumps({"captured": True, "exit_code": exit_code, "tools": specifications,
                  "model": request.get("model"), "reasoning": request.get("reasoning"),
                  "model_inference_calls": 0, "endpoint": "local rejecting HTTP sink in unshared network namespace"}))
