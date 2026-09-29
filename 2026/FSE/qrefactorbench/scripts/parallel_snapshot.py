"""Create independent, read-only code/data snapshots without Git commits."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile


EXCLUDED = {".git", ".parallel", ".codex", ".aws", ".agents", ".venv",
            "__pycache__", ".pytest_cache", ".env", ".lock"}


def inventory(root: Path, *, exclude: bool = False) -> dict[str, dict[str, str | int]]:
    """Hash regular files only; refuse links that could escape the snapshot."""
    result: dict[str, dict[str, str | int]] = {}
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not (exclude and d in EXCLUDED))
        for name in dirs + sorted(files):
            if exclude and name in EXCLUDED:
                continue
            path = Path(directory) / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError(f"Symlink is not allowed: {path}")
            if stat.S_ISDIR(mode):
                continue
            if not stat.S_ISREG(mode):
                raise ValueError(f"Not a regular file: {path}")
            result[path.relative_to(root).as_posix()] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "executable": int(bool(mode & 0o111)),
            }
    return result


def verify(snapshot: Path) -> dict:
    if snapshot.is_symlink() or (snapshot / "files").is_symlink():
        raise ValueError("Snapshot roots must not be symlinks")
    if not (snapshot / "files").is_dir():
        raise ValueError("Snapshot files directory is missing")
    manifest = json.loads((snapshot / "manifest.json").read_text())
    if manifest.get("format") != 1:
        raise ValueError("Unsupported snapshot format")
    actual = inventory(snapshot / "files")
    if actual != manifest["files"]:
        raise ValueError("Snapshot hash/file-set mismatch")
    return manifest


def create(source: Path, destination: Path) -> dict:
    if source.is_symlink():
        raise ValueError("Source root must not be a symlink")
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise ValueError("Source must be a directory")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    destination = destination.absolute()
    if destination.resolve().is_relative_to(source):
        raise ValueError("Destination cannot be inside the source")
    files = inventory(source, exclude=True)
    if not files:
        raise ValueError("Refusing an empty snapshot")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Reserving the destination makes concurrent attempts with the same ID fail.
    destination.mkdir()
    stage = Path(tempfile.mkdtemp(prefix=".snapshot-", dir=destination.parent))
    try:
        data = stage / "files"
        data.mkdir()
        for name in files:
            target = data / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target, follow_symlinks=False)
        if inventory(source, exclude=True) != files or inventory(data) != files:
            raise ValueError("Source changed during snapshot creation")
        manifest = {"format": 1, "source": str(source),
                    "excluded_names": sorted(EXCLUDED), "files": files}
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        verify(stage)
        os.replace(stage, destination)  # The reserved directory is empty.
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        destination.rmdir()
        raise
    for path in destination.rglob("*"):
        if path.is_file():
            path.chmod(0o555 if path.stat().st_mode & 0o111 else 0o444)
    for path in sorted(destination.rglob("*"), reverse=True):
        if path.is_dir():
            path.chmod(0o555)
    destination.chmod(0o555)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("create")
    make.add_argument("source", type=Path)
    make.add_argument("destination", type=Path)
    check = sub.add_parser("verify")
    check.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    manifest = (create(args.source, args.destination) if args.command == "create"
                else verify(args.snapshot))
    path = args.destination if args.command == "create" else args.snapshot
    print(json.dumps({"snapshot": str(path), "files": len(manifest["files"]),
                      "manifest_sha256": hashlib.sha256(
                          (path / "manifest.json").read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
