"""Local visual demonstration. No API credentials, model call or code execution API."""

import argparse
from collections import Counter
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from demo.hybrid_search import ROOT, ORIGINAL, load_original, run_hybrid


def run_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Run only a bounded, validated CNF input, never submitted source code."""
    n, clauses = payload.get("n"), payload.get("clauses")
    if (type(n) is not int or not 0 <= n <= 6 or type(clauses) is not list
            or len(clauses) > 8 or any(type(c) is not list or len(c) > 12
                                     for c in clauses)):
        raise ValueError("n 必须为 0–6 的整数；最多 8 个子句，每个最多 12 个文字")
    if any(type(x) is not int or not 1 <= abs(x) <= n for c in clauses for x in c):
        raise ValueError("文字必须是非零整数，绝对值不超过 n")
    result = run_hybrid(n, clauses)
    expected = ORIGINAL.has_assignment(n, clauses)
    result.update(n=n, clauses=clauses, classical_output=expected,
                  semantic_check=type(result["output"]) is bool and result["output"] == expected,
                  counts=dict(sorted(Counter(result["sampled_candidates"]).items())),
                  model_called=False)
    return result


def source_data() -> dict[str, Any]:
    """Provide explicitly labelled saved predictions, source, and real retained execution."""
    cases = {}
    for case_id in ("pilot-001", "pilot-002"):
        prediction = ROOT / "pilot/baseline-v0.1/conditional-plan-diagnostic/parsed" / f"{case_id}.json"
        cases[case_id] = {
            "source": (ROOT / "cases/pilot" / case_id / "program.py").read_text(),
            "prediction": json.loads(prediction.read_text()),
            "prediction_mode": "historical_replay_not_ground_truth",
        }
    seen = []
    digest = load_original("pilot-002").ledger_digest(
        [b"created", b"approved", b"closed"], lambda i, d: seen.append([i, d]))
    previous = bytes(32)
    expected = []
    for index, event in enumerate([b"created", b"approved", b"closed"]):
        previous = hashlib.sha256(previous + event).digest()
        expected.append([index, previous.hex()])
    cases["pilot-002"]["retained_execution"] = {
        "callbacks": seen, "digest": digest,
        "passed": seen == expected and digest == previous.hex(), "transformed": False,
    }
    return cases


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, value: Any) -> None:
        self.send_body(status, json.dumps(value, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def send_body(self, status: int, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/":
            self.send_body(200, (Path(__file__).parent / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/cases":
            self.send_json(200, source_data())
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/api/run":
            self.send_json(404, {"error": "not found"})
            return
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).netloc != self.headers.get("Host"):
            self.send_json(403, {"error": "local same-origin requests only"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 8192 or self.headers.get_content_type() != "application/json":
                raise ValueError("请求必须是最多 8192 字节的 JSON")
            payload = json.loads(self.rfile.read(length))
            if type(payload) is not dict:
                raise ValueError("JSON 必须为对象")
            result = run_request(payload)
        except (ValueError, TypeError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        except Exception as exc:
            self.send_json(500, {"error": f"运行失败：{type(exc).__name__}: {exc}"})
            return
        self.send_json(200, result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"课程演示已启动：http://127.0.0.1:{args.port}  | Ctrl+C 停止", flush=True)
    print("AI 分析为历史回放；按钮触发真实本地模拟；无新模型调用。", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
