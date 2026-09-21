"""Fetch the official UCI archive; verify against recorded source hashes, no overwrite."""
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent / "data"


def main():
    provenance = json.loads((ROOT / "provenance.json").read_text())
    with urllib.request.urlopen(provenance["download_url"], timeout=30) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    for name, expected in provenance["sha256"].items():
        data = archive.read(name)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Upstream file changed: {name}; inspect before accepting")
        target = ROOT / name
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                raise ValueError(f"Local file changed: {name}; refusing overwrite")
        else:
            target.write_bytes(data)
        print(f"VERIFIED {name}")


if __name__ == "__main__":
    main()
