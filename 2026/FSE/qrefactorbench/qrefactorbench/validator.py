"""Dataset integrity checks beyond JSON Schema; never execute case programs."""

import ast
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .loader import DataError, discover_cases, load_document, program_files, safe_path
from .schema import schema_errors


@dataclass(frozen=True)
class Issue:
    path: str
    severity: str
    message: str


@dataclass
class ValidationReport:
    cases: list[tuple[Path, dict[str, Any]]]
    issues: list[Issue]

    @property
    def valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "case_count": len(self.cases),
                "issues": [asdict(i) for i in self.issues]}


def artifact_paths(case: dict[str, Any]) -> list[str]:
    """Enumerate all declared local evidence for validation and content hashing."""
    paths = program_files(case) + case.get("classical_tests", [])
    paths += case.get("reference_hybrid_implementation") or []
    review = case.get("review", {})
    paths += [a["artifact"] for a in review.get("independent_annotations", [])]
    paths += [review[k] for k in ("disagreements", "resolution") if k in review]
    return sorted(set(paths))


def _function_ranges(tree: ast.AST, prefix: str = "") -> dict[str, tuple[int, int]]:
    result: dict[str, tuple[int, int]] = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = f"{prefix}.{node.name}" if prefix else node.name
            if not isinstance(node, ast.ClassDef):
                start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                result[name] = (start, node.end_lineno or node.lineno)
            result.update(_function_ranges(node, name))
        else:
            result.update(_function_ranges(node, prefix))
    return result


def region_errors(regions: list[dict[str, Any]], case: dict[str, Any], root: Path) -> list[str]:
    """Validate 1-based inclusive regions and optional qualified function names."""
    errors: list[str] = []
    for region in regions:
        file = region["file"]
        if file not in program_files(case):
            errors.append(f"Region file is not a declared program artifact: {file}")
            continue
        try:
            source = safe_path(root, file).read_text(encoding="utf-8")
            start, end = region["start_line"], region["end_line"]
            if not 1 <= start <= end <= len(source.splitlines()):
                errors.append(f"Invalid source-line range in {file}: {start}..{end}")
            if region.get("function"):
                functions = _function_ranges(ast.parse(source))
                bounds = functions.get(region["function"])
                if bounds is None or not (bounds[0] <= start <= end <= bounds[1]):
                    errors.append(f"Region does not lie in function {region['function']}: {file}")
        except (DataError, OSError, UnicodeError, SyntaxError, ValueError) as exc:
            errors.append(f"{file}: {exc}")
    return errors


def validate_case(path: Path, case: Any) -> list[Issue]:
    problems = schema_errors(case)
    if problems:
        return [Issue(str(path), "error", p) for p in problems]
    root = path.parent
    for relative in artifact_paths(case):
        try:
            if not safe_path(root, relative).is_file():
                problems.append(f"Missing artifact: {relative}")
        except (DataError, OSError, ValueError) as exc:
            problems.append(str(exc))
    for relative in program_files(case):
        try:
            if not relative.endswith(".py"):
                problems.append(f"v0.1 program artifacts must be Python: {relative}")
            compile(safe_path(root, relative).read_text(encoding="utf-8"), relative, "exec")
        except (DataError, OSError, UnicodeError, SyntaxError, ValueError) as exc:
            problems.append(f"Invalid program {relative}: {exc}")
    problems += region_errors(case["candidate_regions"], case, root)
    if case["benchmark_supported"] is True and case["migration_family"] is None:
        problems.append("benchmark_supported=true requires a supported migration_family")
    if case["expected_decision"] == "QUANTUMIZE" and any(
        case[k] is False for k in ("structural_eligibility", "practical_suitability", "benchmark_supported")
    ):
        problems.append("QUANTUMIZE contradicts a false scientific label")
    if case["expected_decision"] == "REMAIN_CLASSICAL" and all(
        case[k] is True for k in ("structural_eligibility", "practical_suitability", "benchmark_supported")
    ):
        problems.append("REMAIN_CLASSICAL with all three labels true needs an explicit protocol revision")
    contracts = case.get("admissible_migration_contracts", [])
    ids = [c["contract_id"] for c in contracts]
    if len(ids) != len(set(ids)):
        problems.append("Duplicate contract_id")
    reference = case.get("reference_plan")
    if reference:
        if reference["contract_id"] not in ids:
            problems.append("reference_plan refers to an undeclared contract")
        else:
            contract = contracts[ids.index(reference["contract_id"])]
            if reference["quantum_algorithm_family"] not in contract["algorithm_families"]:
                problems.append("reference_plan algorithm is outside its declared contract")
        if reference["migration_family"] != case["migration_family"]:
            problems.append("reference_plan migration family contradicts the case")
        if case.get("computational_intent") and reference["computational_intent_id"] != case["computational_intent"]["id"]:
            problems.append("reference_plan intent contradicts the case")
    if case["annotation_status"] != "DRAFT":
        oracle = case["semantic_oracle"]
        config = oracle["config"]
        if oracle["kind"] == "deterministic_equality" and "expected" not in config:
            problems.append("Reviewed equality oracle requires an explicit expected value")
        if oracle["kind"] == "optimization_objective":
            if config.get("direction") not in {"minimize", "maximize"} or type(config.get("threshold")) not in {int, float}:
                problems.append("Reviewed objective oracle requires explicit direction and numeric threshold")
        if oracle["kind"] in {"property", "optimization_feasibility", "probabilistic"} and not oracle.get("hook_id"):
            problems.append("Reviewed property/feasibility/probabilistic oracle requires a hook_id")
        if any(c["status"] != "REVIEWED" for c in contracts):
            problems.append("Non-DRAFT cases cannot rely on DRAFT contracts")
        reviews = case["review"]["independent_annotations"]
        people = [r["annotator_id"] for r in reviews]
        if len(set(people)) < 2 or len(people) != len(set(people)):
            problems.append("Independent annotations require distinct annotators")
        if len({r["artifact"] for r in reviews}) != len(reviews):
            problems.append("Independent annotations require distinct artifact files")
        if not set(people).issubset(case["annotators"]):
            problems.append("Review annotators must be listed in annotators")
        adjudicator = case["review"].get("adjudicator_id")
        if adjudicator and adjudicator not in case["annotators"]:
            problems.append("Adjudicator must be listed in annotators")
    if case["annotation_status"] == "FROZEN" and case["license"] in {"NOASSERTION", "UNKNOWN"}:
        problems.append("FROZEN cases require resolved source licensing")
    issues = [Issue(str(path), "error", p) for p in problems]
    if case["annotation_status"] == "DRAFT":
        issues.append(Issue(str(path), "warning", "DRAFT: infrastructure example or unfinished annotation; not ground truth"))
    return issues


def validate_dataset(root: Path) -> ValidationReport:
    report = ValidationReport([], [])
    try:
        manifests = discover_cases(root)
    except DataError as exc:
        report.issues.append(Issue(str(root), "error", str(exc)))
        return report
    if not manifests:
        report.issues.append(Issue(str(root), "error", "No case manifests found"))
    seen: set[str] = set()
    for path in manifests:
        try:
            case = load_document(path)
        except DataError as exc:
            report.issues.append(Issue(str(path), "error", str(exc)))
            continue
        issues = validate_case(path, case)
        report.issues.extend(issues)
        if isinstance(case, dict) and isinstance(case.get("case_id"), str):
            if case["case_id"] in seen:
                report.issues.append(Issue(str(path), "error", f"Duplicate case_id: {case['case_id']}"))
            seen.add(case["case_id"])
        if not any(i.severity == "error" for i in issues):
            report.cases.append((path, case))
    return report
