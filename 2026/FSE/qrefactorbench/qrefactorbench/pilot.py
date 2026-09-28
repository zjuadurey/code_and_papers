"""Small local pilot packet exporter and external-response collector; no model calls."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from . import PHASE1_PREDICTION_VERSION
from .evaluator.pipeline import prediction_errors
from .loader import DataError, load_document, program_files, safe_path
from .schema import documents
from .validator import validate_dataset

PUBLIC_FIELDS = ("case_id", "title", "software_contract", "input_domain", "execution_assumptions")


def _encode(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _pilot_cases(repository: Path) -> list[tuple[Path, dict[str, Any]]]:
    report = validate_dataset(repository / "cases" / "pilot")
    if not report.valid:
        raise DataError(_encode(report.to_dict()))
    return report.cases


def prepare_packets(repository: Path, output: Path) -> dict[str, Any]:
    """Export allowlisted public facts; refuse to overwrite any previous packet.

    Directory separation supports blind distribution, not filesystem access control.
    The coordinator must distribute each role separately, outside this repository.
    """
    if output.exists():
        raise DataError(f"Output already exists; choose a new directory: {output}")
    cases = _pilot_cases(repository)
    annotation_dir = repository / "pilot" / "annotation"
    catalog = load_document(repository / "pilot" / "public_contracts.json")
    prompt_template = (repository / "pilot" / "baseline" / "prompt_template.md").read_text(encoding="utf-8")
    blank = load_document(annotation_dir / "annotation_template.json")
    adjudication = load_document(annotation_dir / "adjudication_template.json")
    prepared: dict[str, str] = {}
    for role in ("annotator_a", "annotator_b"):
        prepared[f"{role}/INSTRUCTIONS.md"] = (annotation_dir / "instructions.md").read_text(encoding="utf-8")
        prepared[f"{role}/contracts.json"] = _encode(catalog)
    prepared["adjudication/INSTRUCTIONS.md"] = (annotation_dir / "adjudication_instructions.md").read_text(encoding="utf-8")
    # Export the versioned protocol, never mutable project history or result links.
    prepared["baseline/INSTRUCTIONS.md"] = (
        repository / "pilot" / "baseline" / "packet_instructions.v0.1.md"
    ).read_text(encoding="utf-8")
    prepared["baseline/run_metadata.template.json"] = (repository / "pilot" / "baseline" / "run_metadata.template.json").read_text(encoding="utf-8")
    for name, schema in documents().items():
        prepared[f"baseline/schemas/{name}.schema.json"] = _encode(schema)
    for path, case in cases:
        case_id = case["case_id"]
        raw_task = load_document(path.parent / "public_task.json")
        if not isinstance(raw_task, dict) or any(k not in raw_task for k in PUBLIC_FIELDS):
            raise DataError(f"Incomplete public task: {case_id}")
        if raw_task["case_id"] != case_id:
            raise DataError(f"Public task ID mismatch: {case_id}")
        # An explicit whitelist avoids copying curator notes, labels, plans, tests,
        # source metadata or categories even if fields are added to public_task.
        task = {field: raw_task[field] for field in PUBLIC_FIELDS}
        sources = {name: safe_path(path.parent, name).read_text(encoding="utf-8")
                   for name in program_files(case)}
        for role in ("annotator_a", "annotator_b"):
            prepared[f"{role}/{case_id}/public_task.json"] = _encode(task)
            prepared[f"{role}/{case_id}/annotation.json"] = _encode(dict(blank, case_id=case_id, role=role))
            for name, source in sources.items():
                prepared[f"{role}/{case_id}/{name}"] = source
        prepared[f"adjudication/{case_id}/adjudication.json"] = _encode(dict(adjudication, case_id=case_id))
        numbered = "\n\n".join(f"FILE: {name}\n" + "\n".join(
            f"{i:4d} | {line}" for i, line in enumerate(source.splitlines(), 1))
            for name, source in sorted(sources.items()))
        prompt = prompt_template
        for key, value in {"CASE_ID": case_id, "PUBLIC_TASK": _encode(task),
                           "CONTRACT_CATALOG": _encode(catalog), "SOURCE_FILES": numbered}.items():
            prompt = prompt.replace("{{" + key + "}}", value)
        prepared[f"baseline/prompts/{case_id}.md"] = prompt
    # Validate every output path before writing anything; all source artifacts were
    # loaded and the dataset checked first. Never append to researchers' submissions.
    for relative in prepared:
        safe_path(output, relative)
    for role in ("annotator_a", "annotator_b", "adjudication", "baseline"):
        prefix = role + "/"
        prepared[f"{role}/packet_manifest.json"] = _encode({
            "packet_version": "phase1-v0", "case_ids": [c["case_id"] for _, c in cases],
            "files_sha256": {name[len(prefix):]: hashlib.sha256(content.encode()).hexdigest()
                             for name, content in sorted(prepared.items()) if name.startswith(prefix)},
        })
    output.mkdir(parents=True, exist_ok=False)
    for relative, content in sorted(prepared.items()):
        target = safe_path(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return {"case_count": len(cases), "roles": ["annotator_a", "annotator_b", "adjudication", "baseline"],
            "output": str(output), "model_calls": 0, "annotation_state": "blank DRAFT forms"}


def collect_predictions(repository: Path, responses: Path, output: Path) -> dict[str, Any]:
    """Collect one untouched JSON response per pilot case; no repair or fallback."""
    if output.exists():
        raise DataError(f"Output already exists: {output}")
    cases = _pilot_cases(repository)
    expected = {c["case_id"] + ".json" for _, c in cases}
    actual = {p.name for p in responses.glob("*.json")}
    if actual != expected:
        raise DataError(f"Response filenames mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    predictions = []
    problems = []
    for path, case in cases:
        response_path = responses / f"{case['case_id']}.json"
        try:
            prediction = load_document(response_path)
            if not isinstance(prediction, dict) or prediction.get("schema_version") != PHASE1_PREDICTION_VERSION:
                raise DataError("Phase-1 prediction schema_version must be 0.2.0")
            errors = prediction_errors(prediction, case, path.parent)
            if errors:
                raise DataError("; ".join(errors))
            predictions.append(prediction)
        except DataError as exc:
            problems.append({"case_id": case["case_id"], "error": str(exc)})
    if problems:
        raise DataError(_encode({"invalid_responses": problems, "output_written": False}))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        stream.write(_encode(predictions))
    return {"prediction_count": len(predictions), "output": str(output), "repairs": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--output", required=True, type=Path)
    collect = commands.add_parser("collect")
    collect.add_argument("--responses", required=True, type=Path)
    collect.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = (prepare_packets(args.repository, args.output) if args.command == "prepare"
                  else collect_predictions(args.repository, args.responses, args.output))
        print(_encode(result), end="")
        return 0
    except (DataError, OSError, ValueError) as exc:
        print(_encode({"error": str(exc)}), end="")
        return 2
