"""Archive primary papers for the scoped benefit analysis; never execute source code."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
PAPERS = {
    "bbht.pdf": "https://arxiv.org/pdf/quant-ph/9605034v1",
    "minimum.pdf": "https://arxiv.org/pdf/quant-ph/9607014v1",
    "end-to-end.pdf": "https://arxiv.org/pdf/2310.03011v2",
    "resources.pdf": "https://arxiv.org/pdf/2211.07629v1",
    "quadratic.pdf": "https://arxiv.org/pdf/2011.04149v1",
}


def fetch(item: tuple[str, str]) -> dict:
    name, url = item
    row = {"file": "sources/" + name, "url": url}
    try:
        data = urllib.request.urlopen(url, timeout=35).read()
        if not data.startswith(b"%PDF"):
            raise ValueError("Response is not a PDF")
        path = ROOT / row["file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as error:
        row["error"] = str(error)
    print(name, row.get("bytes", row.get("error")), flush=True)
    return row


if __name__ == "__main__":
    path = ROOT / "source-manifest.json"
    if path.exists():
        raise RuntimeError("Refusing to overwrite retrieval record")
    with ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(fetch, PAPERS.items()))
    path.write_text(json.dumps(rows, indent=2) + "\n")
