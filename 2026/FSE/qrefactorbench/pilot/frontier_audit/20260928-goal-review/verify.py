"""Check survey integrity and document paths, not scientific novelty or performance."""
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
REPORT = PROJECT / "docs/frontier/v2"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    protected = json.loads((HERE / "protected-before.json").read_text())
    for name, value in protected.items():
        path = PROJECT / name
        if not path.is_file() or sha(path) != value:
            errors.append("protected: " + name)
    success, failed = 0, 0
    for manifest in HERE.glob("source-manifest*.json"):
        for row in json.loads(manifest.read_text()):
            if "error" in row:
                failed += 1
                continue
            path = HERE / row["file"]
            if not path.is_file() or sha(path) != row["sha256"]:
                errors.append("source: " + row["file"])
            success += 1
    # Verify the prior artifact manifest without rerunning its stateful verifier.
    old_manifest = PROJECT / "pilot/frontier_audit/20260928/artifact-manifest.json"
    prior = json.loads(old_manifest.read_text())
    for name, value in prior.items():
        path = PROJECT / name
        if not path.is_file() or sha(path) != value:
            errors.append("N-059 artifact: " + name)
    docs = list(REPORT.glob("*.md")) + [HERE / "README.md"]
    docs += [PROJECT / name for name in (
        "PROJECT_STATUS.md", "NEXT_ACTIONS.md", "DECISIONS.md", "TODO.md", "CHANGELOG.md",
        "docs/RESEARCH_CHARTER.md", "docs/research_log.md")]
    links = 0
    for doc in docs:
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", doc.read_text()):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            links += 1
            if not (doc.parent / target).exists():
                errors.append(f"link: {doc.relative_to(PROJECT)} -> {target}")
    for name in ("PROJECT_STATUS.md", "NEXT_ACTIONS.md"):
        if "docs/frontier/v2/README.md" not in (PROJECT / name).read_text():
            errors.append("current pointer: " + name)
    completion = json.loads((HERE / "completion-audit.json").read_text())
    for row in completion["requirements"]:
        if row["status"] != "verified":
            errors.append("completion review: " + row["id"])
        for name in row["evidence_files"]:
            if not (PROJECT / name).is_file():
                errors.append("completion evidence: " + name)
    files = [p for p in HERE.rglob("*") if p.is_file() and p.name not in
             ("artifact-manifest.json", "validation.json")]
    files += list(REPORT.glob("*.md"))
    artifacts = {str(p.relative_to(PROJECT)): sha(p) for p in sorted(files)}
    manifest_path = HERE / "artifact-manifest.json"
    if args.record:
        if manifest_path.exists():
            raise RuntimeError("Refusing to replace artifact manifest")
        if not errors:
            manifest_path.write_text(json.dumps(artifacts, indent=2) + "\n")
    elif not manifest_path.exists() or json.loads(manifest_path.read_text()) != artifacts:
        errors.append("artifact manifest mismatch")
    result = {"passed": not errors, "protected_files": len(protected),
              "prior_artifact_files": len(prior), "new_source_files": success,
              "recorded_download_failures": failed, "local_link_occurrences": links,
              "artifact_files": len(artifacts), "manual_completion_rows": len(completion["requirements"]),
              "scope": "byte integrity, source hashes, path existence, handoff pointers; not scientific validation",
              "errors": errors}
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
