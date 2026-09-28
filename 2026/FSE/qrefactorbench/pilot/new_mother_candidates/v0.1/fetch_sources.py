"""Fetch only public, commit-pinned source evidence; never install or execute it."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = (
    ("cpython", "python/cpython", "v3.10.14", "976ea78599d71f22e9c0fefc2dc37c1d9fc835a4",
     ("Lib/difflib.py", "Doc/library/difflib.rst", "LICENSE")),
    ("python-tsp", "fillipe-gsm/python-tsp", "v0.5.0", "b38179d06861e48a46c20c90a3d8162eb739795e",
     ("python_tsp/exact/dynamic_programming.py", "python_tsp/exact/brute_force.py", "LICENSE", "pyproject.toml")),
    ("networkx", "networkx/networkx", "networkx-3.4.2", "2acf1590f82757c01a57b81b8c5dfb79e60aa416",
     ("networkx/algorithms/simple_paths.py", "networkx/algorithms/tests/test_simple_paths.py", "LICENSE.txt")),
)


def main() -> None:
    records = []
    for project, repo, tag, revision, paths in SOURCES:
        for path in paths:
            url = f"https://raw.githubusercontent.com/{repo}/{revision}/{path}"
            target = ROOT / "sources" / project / path
            target.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read()
            if target.exists():
                if target.read_bytes() != data:
                    raise RuntimeError(f"Refusing to replace changed snapshot: {target}")
            else:
                target.write_bytes(data)
            records.append(dict(project=project, repository=repo, tag=tag, revision=revision,
                                upstream_path=path, url=url, file=str(target.relative_to(ROOT)),
                                bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    target = ROOT / "sources/manifest.json"
    data = json.dumps(records, indent=2) + "\n"
    if target.exists() and target.read_text() != data:
        raise RuntimeError("Refusing to replace source manifest")
    target.write_text(data)
    print(f"Verified {len(records)} pinned public source files")


if __name__ == "__main__":
    main()
