"""Offline, versioned JSON Schema validation; no remote schema resolution."""

import json
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from . import PHASE1_PREDICTION_VERSION

SCHEMA_NAMES = ("case", "prediction", "migration_plan", "phase1_prediction")


def documents() -> dict[str, dict[str, Any]]:
    """Load the schemas from package data, independent of the working directory."""
    return {
        name: json.loads(files("schemas").joinpath(f"{name}.schema.json").read_text())
        for name in SCHEMA_NAMES
    }


def schema_errors(data: Any, kind: str = "case") -> list[str]:
    """Return stable, human-readable diagnostics without executing artifacts."""
    if kind == "prediction" and isinstance(data, dict) and data.get("schema_version") == PHASE1_PREDICTION_VERSION:
        kind = "phase1_prediction"
    docs = documents()
    registry = Registry().with_resources(
        (doc["$id"], Resource.from_contents(doc)) for doc in docs.values()
    )
    validator = Draft202012Validator(
        docs[kind], registry=registry, format_checker=FormatChecker()
    )
    errors = sorted(validator.iter_errors(data), key=lambda e: str(list(e.absolute_path)))
    return [f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in errors]
