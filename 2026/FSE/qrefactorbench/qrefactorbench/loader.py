"""Load JSON or optional YAML documents and resolve case-local artifacts."""

import json
import math
from pathlib import Path, PurePosixPath
from typing import Any


class DataError(ValueError):
    """An input document or artifact cannot be safely interpreted."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DataError(f"Duplicate mapping key: {key}")
        result[key] = value
    return result


def _json_compatible(value: Any, ancestors: frozenset[int] = frozenset()) -> None:
    if isinstance(value, (dict, list)):
        if id(value) in ancestors:
            raise DataError("Recursive YAML aliases are not supported")
        ancestors = ancestors | {id(value)}
        if isinstance(value, dict):
            if not all(isinstance(k, str) for k in value):
                raise DataError("Mapping keys must be strings")
            values = value.values()
        else:
            values = value
        for child in values:
            _json_compatible(child, ancestors)
    elif not (value is None or isinstance(value, (str, bool, int, float))):
        raise DataError("Document must contain JSON-compatible values")
    elif isinstance(value, float) and not math.isfinite(value):
        raise DataError("Non-finite numbers are not supported")


def load_document(path: Path) -> Any:
    """Reject duplicate keys and non-JSON YAML types rather than losing data."""
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml
            except ImportError as exc:
                raise DataError("YAML requires the optional 'yaml' dependency") from exc

            class UniqueLoader(yaml.SafeLoader):
                pass

            def mapping(loader: Any, node: Any) -> dict[str, Any]:
                loader.flatten_mapping(node)
                pairs = [(loader.construct_object(k), loader.construct_object(v))
                         for k, v in node.value]
                if not all(isinstance(k, str) for k, _ in pairs):
                    raise DataError("Mapping keys must be strings")
                return _pairs(pairs)

            UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
            try:
                data = yaml.load(text, Loader=UniqueLoader)
            except yaml.YAMLError as exc:
                raise DataError(str(exc)) from exc
        else:
            data = json.loads(text, object_pairs_hook=_pairs)
        _json_compatible(data)
        return data
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise DataError(f"{path}: {exc}") from exc


def safe_path(root: Path, relative: str) -> Path:
    """Require portable case-relative paths, including symlink containment."""
    parts = PurePosixPath(relative)
    if (not relative or parts.is_absolute() or ".." in parts.parts
            or "\\" in relative or ":" in relative or str(parts) != relative
            or relative == "."):
        raise DataError(f"Invalid relative path: {relative!r}")
    result = (root / relative).resolve()
    if not result.is_relative_to(root.resolve()):
        raise DataError(f"Artifact escapes case directory: {relative}")
    return result


def discover_cases(root: Path) -> list[Path]:
    """Only case.json/case.yaml/case.yml are dataset manifests."""
    if root.is_file():
        return [root]
    if not root.is_dir():
        raise DataError(f"Dataset path does not exist: {root}")
    return sorted(p for p in root.rglob("case.*") if p.suffix in {".json", ".yaml", ".yml"})


def program_files(case: dict[str, Any]) -> list[str]:
    return [case["classical_program"]] if "classical_program" in case else case["files"]
