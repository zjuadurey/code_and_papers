"""Syntax-only routing over explicitly supplied public source strings. Never executes them."""
from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
from typing import Any

LEGACY = Path(__file__).resolve().parent.parent / "state-workflow-v0.1/workflow.py"
spec = importlib.util.spec_from_file_location("retained_lexical_inventory_n055", LEGACY)
assert spec and spec.loader
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)

LIMITS = [
    "Syntax-only, source-order inventory; no candidate ranking or eligibility verdict.",
    "Declared regions are never silently expanded, narrowed, or replaced.",
    "Function scope and complete statement spans are analysis context, not proposed migrations.",
    "Top-level functions only; no alias/call-effect/range/reachability proof or sound slicing.",
    "No candidate means no nomination, not evidence that no opportunity exists.",
]


def digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def statement_rows(fn: ast.AST, source: str) -> list[dict[str, Any]]:
    lines = source.splitlines()
    result = []
    def walk(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                result.append({"syntax": type(child).__name__, "start_line": child.lineno,
                               "end_line": child.end_lineno, "column": child.col_offset,
                               "end_column": child.end_col_offset,
                               "source_start_line": lines[child.lineno - 1]})
            # Nested definitions are listed, but their bodies belong to a different scope.
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                walk(child)
    walk(fn)
    return sorted(result, key=lambda row: (row["start_line"], row["column"], row["end_line"]))


def catalog(sources: dict[str, str]) -> tuple[list[dict[str, Any]], dict[str, ast.Module]]:
    rows, trees = [], {}
    for filename, source in sources.items():
        tree = ast.parse(source)
        trees[filename] = tree
        rows.append({"file": filename, "source_sha256": digest(source),
                     "functions": [{"function": fn.name, "start_line": fn.lineno,
                                    "end_line": fn.end_lineno, "statements": statement_rows(fn, source)}
                                   for fn in tree.body if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))]})
    return rows, trees


def analyze(sources: dict[str, str], regions: list[dict[str, Any]]) -> dict[str, Any]:
    """The source mapping is the entire allowlist; nomination strings never become paths."""
    if not isinstance(sources, dict) or not sources or not all(isinstance(k, str) and isinstance(v, str)
                                                               for k, v in sources.items()):
        raise ValueError("Explicit public filename-to-source mapping required")
    if not isinstance(regions, list):
        raise ValueError("Candidate regions must be a list")
    if len(regions) > 64 or sum(len(v.encode()) for v in sources.values()) > 1_000_000:
        raise ValueError("Offline inventory budget exceeded")
    outlines, trees = catalog(sources)
    result = {"version": "candidate-routing-0.1", "kind": "public_syntax_analysis_entry",
              "status": "no_nomination" if not regions else "nomination_routes",
              "source_catalog": outlines, "routes": [], "limits": LIMITS.copy(),
              "candidate_discovery_performed": False, "eligibility_verdict": None}
    for region in regions:
        route = {"declared_region": deepcopy(region), "analysis_scope": None,
                 "seed_statement": None, "boundary_statements": [], "inventory": None,
                 "status": "invalid_region"}
        result["routes"].append(route)
        if (not isinstance(region, dict) or set(region) != {"file", "function", "start_line", "end_line"}
                or not isinstance(region["file"], str) or not isinstance(region["function"], str)
                or type(region["start_line"]) is not int or type(region["end_line"]) is not int
                or not 1 <= region["start_line"] <= region["end_line"]):
            continue
        name, first, last = region["file"], region["start_line"], region["end_line"]
        if name not in sources:
            route["status"] = "file_not_in_public_allowlist"
            continue
        candidates = [fn for fn in trees[name].body if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and fn.name == region["function"]]
        enclosing = [fn for fn in candidates if fn.lineno <= first <= last <= fn.end_lineno]
        if len(enclosing) != 1:
            route["status"] = "outside_or_unknown_function" if not enclosing else "ambiguous_function"
            continue
        fn = enclosing[0]
        route["analysis_scope"] = {"file": name, "function": fn.name, "start_line": fn.lineno,
                                   "end_line": fn.end_lineno, "role": "enclosing_lexical_function"}
        statements = statement_rows(fn, sources[name])
        route["boundary_statements"] = [{**s, "relation":
            "exact" if first == s["start_line"] and last == s["end_line"] else
            "within_declared" if first <= s["start_line"] <= s["end_line"] <= last else
            "contains_declared" if s["start_line"] <= first <= last <= s["end_line"] else "crosses_boundary"}
            for s in statements if s["start_line"] <= last and s["end_line"] >= first]
        if (first, last) == (fn.lineno, fn.end_lineno):
            route["status"] = "function_outline"
            continue
        exact = [s for s in statements if (s["start_line"], s["end_line"]) == (first, last)]
        if len(exact) != 1:
            route["status"] = "ambiguous_statement_span" if len(exact) > 1 else "region_outline"
            continue
        # Same-line statements cannot be safely selected by the retained line-only analyzer.
        if sum(s["start_line"] == first for s in statements) != 1:
            route["status"] = "ambiguous_statement_start"
            continue
        route["seed_statement"] = exact[0]
        try:
            route["inventory"] = legacy.analyze_source(sources[name], fn.name, first)
            route["status"] = "statement_inventory"
        except ValueError as exc:
            route["status"] = "inventory_unsupported"
            route["inventory_reason"] = str(exc)
    return result
