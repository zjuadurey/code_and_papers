"""Content fingerprints and observed software versions for evaluation artifacts."""

import hashlib
import importlib.metadata
import platform
from pathlib import Path
from typing import Any

from . import SCHEMA_VERSION, __version__
from .loader import safe_path
from .schema import documents
from .validator import artifact_paths


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(cases: list[tuple[Path, dict[str, Any]]], prediction_path: Path) -> dict[str, Any]:
    import json

    dependencies: dict[str, str | None] = {}
    for name in ("jsonschema", "referencing", "PyYAML", "qiskit", "pytest"):
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None
    package_root = Path(__file__).parent
    return {
        "package_version": __version__, "schema_version": SCHEMA_VERSION,
        "python": platform.python_version(), "dependencies": dependencies,
        "implementation_sha256": {str(p.relative_to(package_root)): digest(p)
                                  for p in sorted(package_root.rglob("*.py"))},
        "schema_sha256": {name: hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()
                          for name, doc in documents().items()},
        "predictions_sha256": digest(prediction_path),
        "cases": {case["case_id"]: {"version": case["version"],
                                   "annotation_status": case["annotation_status"],
                                   "manifest_sha256": digest(path),
                                   "artifacts_sha256": {p: digest(safe_path(path.parent, p)) for p in artifact_paths(case)}}
                  for path, case in cases},
        "randomness": "Static evaluators use no random sampling; execution seeds belong in case configuration.",
    }

