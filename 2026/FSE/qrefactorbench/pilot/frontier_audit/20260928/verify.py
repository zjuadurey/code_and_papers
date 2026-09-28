"""Verify archived bytes, protected files and local links; no upstream execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    errors = []
    protected = json.loads((HERE / "protected-before.json").read_text())
    for name, expected in protected.items():
        path = PROJECT / name
        if not path.is_file() or digest(path) != expected:
            errors.append("protected: " + name)
    sources, unavailable = 0, 0
    for manifest in sorted(HERE.glob("source-manifest*.json")):
        for row in json.loads(manifest.read_text()):
            if "error" in row:
                unavailable += 1
                continue
            path = HERE / row["file"]
            if not path.is_file() or digest(path) != row["sha256"]:
                errors.append("source: " + row["file"])
            sources += 1
    for row in json.loads((HERE / "qpipe-selected-members.json").read_text()):
        if digest(HERE / row["file"]) != row["sha256"]:
            errors.append("zip member: " + row["file"])
    docs = list((PROJECT / "docs/frontier").glob("*.md")) + [HERE / "README.md"]
    docs += [PROJECT / p for p in ("PROJECT_STATUS.md", "NEXT_ACTIONS.md", "TODO.md", "CHANGELOG.md", "DECISIONS.md", "docs/research_log.md")]
    links = 0
    for doc in docs:
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", doc.read_text()):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            links += 1
            if not (doc.parent / target).exists():
                errors.append(f"link: {doc.relative_to(PROJECT)} -> {target}")
    artifact_path = HERE / "artifact-manifest.json"
    files = [p for p in HERE.rglob("*") if p.is_file() and p.name not in ("artifact-manifest.json", "validation.json")]
    files += list((PROJECT / "docs/frontier").glob("*.md"))
    artifacts = {str(p.relative_to(PROJECT)): digest(p) for p in sorted(files)}
    if args.record:
        if artifact_path.exists():
            raise RuntimeError("Manifest already exists; use check mode")
        if not errors:
            artifact_path.write_text(json.dumps(artifacts, indent=2) + "\n")
    elif not artifact_path.exists() or json.loads(artifact_path.read_text()) != artifacts:
        errors.append("artifact manifest mismatch")
    result = {"protected_files": len(protected), "archived_sources": sources,
              "manifest_download_errors": unavailable, "selected_zip_members": 6,
              "local_link_occurrences": links, "artifact_files": len(artifacts),
              "errors": errors, "passed": not errors,
              "scope": "byte integrity and local path existence only; no scientific or performance validation"}
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
