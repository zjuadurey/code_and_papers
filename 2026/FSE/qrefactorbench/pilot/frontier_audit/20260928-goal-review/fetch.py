"""Download public research sources without executing upstream code."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "road.pdf": "https://arxiv.org/pdf/2503.11450v1",
    "yamato.pdf": "https://jxiv.jst.go.jp/index.php/jxiv/preprint/download/2811/6858/6255",
    "cork.pdf": "https://tuhat.helsinki.fi/ws/portalfiles/portal/159680541/Jon_Speer_Quantum_Offloading.pdf",
    "quast-project.json": "https://gitlab.cc-asp.fraunhofer.de/api/v4/projects/iks-quantum-computing-public%2Fquast-decisiontree",
}


def fetch(item: tuple[str, str]) -> dict:
    name, url = item
    row = {"file": "sources/" + name, "url": url}
    try:
        with urllib.request.urlopen(url, timeout=25) as response:
            data = response.read()
        path = ROOT / row["file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as error:
        row["error"] = str(error)
    print(name, row.get("bytes", row.get("error")), flush=True)
    return row


if __name__ == "__main__":
    target = ROOT / "source-manifest.json"
    if target.exists():
        raise RuntimeError("Refusing to replace previous retrieval evidence")
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(fetch, SOURCES.items()))
    target.write_text(json.dumps(rows, indent=2) + "\n")
