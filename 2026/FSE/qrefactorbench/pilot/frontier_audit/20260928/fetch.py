"""Public evidence downloads only; never execute upstream code or install packages."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent


def main() -> None:
    manifest = []
    for row in json.loads((ROOT / "sources.json").read_text()):
        path = ROOT / row["file"]
        if path.exists():
            data = path.read_bytes()
        else:
            with urllib.request.urlopen(row["url"], timeout=45) as response:
                data = response.read()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        manifest.append({**row, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    target = ROOT / "source-manifest.json"
    encoded = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if target.exists() and target.read_text() != encoded:
        raise RuntimeError("Refusing to change existing manifest")
    target.write_text(encoded)
    print(f"Archived {len(manifest)} sources; no upstream code executed")


if __name__ == "__main__":
    main()
