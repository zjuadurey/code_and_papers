"""Archive a bounded third batch of public evidence; execute no upstream code."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "qpipe-paper.html": "https://arxiv.org/html/2607.00939v1",
    "offloading-paper.pdf": "https://tuhat.helsinki.fi/ws/portalfiles/portal/159680541/Jon_Speer_Quantum_Offloading.pdf",
}
for name in ("README.md", "algorithm_selection_framework.py", "main.py", "runtime_fit.py", "csvs/classical_approximation_benchmark.py"):
    SOURCES["predict/" + name] = "https://raw.githubusercontent.com/lfd/qce2025-design-automation/4b4490a6abfdebfe8a8801becad343dd733fa326/" + name

if __name__ == "__main__":
    target = ROOT / "source-manifest-3.json"
    if target.exists():
        raise RuntimeError("Batch already recorded; do not overwrite")
    rows = []
    for name, url in SOURCES.items():
        row = {"url": url, "file": "sources/" + name}
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = response.read()
            path = ROOT / row["file"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        except Exception as error:
            row["error"] = str(error)
        rows.append(row)
        print(name, row.get("bytes", row.get("error")), flush=True)
    target.write_text(json.dumps(rows, indent=2) + "\n")
