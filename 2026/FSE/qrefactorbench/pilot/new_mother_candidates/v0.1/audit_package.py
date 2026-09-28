"""Offline local-link and artifact-hash audit; --check does not write."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    links = 0
    for path in sorted(ROOT.glob("*.md")):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("http:", "https:", "#")):
                continue
            resolved = (path.parent / target.split("#")[0]).resolve()
            bootstrap_output = (not args.check and resolved.parent == ROOT and
                                resolved.name in ("artifact-manifest.json", "audit.json"))
            if not resolved.exists() and not bootstrap_output:
                raise AssertionError(f"Broken link in {path.name}: {target}")
            links += 1
    files = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(ROOT.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
        and p.name not in ("artifact-manifest.json", "audit.json")
    }
    objects = {
        "artifact-manifest.json": files,
        "audit.json": dict(status="PASS", local_link_occurrences=links,
                           artifact_files=len(files),
                           scope="Top-level dossier Markdown links and package file content hashes; not scientific adjudication"),
    }
    for name, obj in objects.items():
        target = ROOT / name
        encoded = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
        if args.check or target.exists():
            if target.read_text() != encoded:
                raise AssertionError(f"Audit differs: {name}")
        else:
            target.write_text(encoded)
    print(json.dumps(objects['audit.json'], ensure_ascii=False))


if __name__ == "__main__":
    main()
