"""Reviewer-bound local pivot claims, evaluated as data rather than Python code.

This module does not infer a formula from prose, validate an entire Phase-1
response, or certify that a reviewer has transcribed the prose faithfully.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from typing import Any


class InvalidClaim(ValueError):
    pass


class ClaimBudget(ValueError):
    pass


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def response_digest(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


class Expression:
    """Bounded Boolean/quantifier interpreter; no eval, imports or arbitrary calls."""

    def __init__(self, text: str, variables: set[str]) -> None:
        if not isinstance(text, str) or len(text) > 2048:
            raise ClaimBudget("Expression must be a string of at most 2048 characters")
        try:
            self.node = ast.parse(text, mode="eval").body
        except (SyntaxError, RecursionError) as exc:
            raise InvalidClaim("Invalid expression syntax") from exc
        if len(list(ast.walk(self.node))) > 256:
            raise ClaimBudget("Expression exceeds 256 AST nodes")
        self._validate(self.node, variables | {"values", "indices"})

    def _validate(self, node: ast.AST, allowed: set[str]) -> None:
        if isinstance(node, ast.Constant):
            if type(node.value) not in (bool, int) or abs(node.value) > 10000:
                raise InvalidClaim("Only small integer/Boolean constants are supported")
        elif isinstance(node, ast.Name):
            if node.id not in allowed:
                raise InvalidClaim("Unknown variable: " + node.id)
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
            for item in node.values:
                self._validate(item, allowed)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self._validate(node.operand, allowed)
        elif isinstance(node, ast.Compare) and all(isinstance(op, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for op in node.ops):
            for item in [node.left, *node.comparators]:
                self._validate(item, allowed)
        elif isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id in ("values", "indices"):
            self._validate(node.slice, allowed)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords and len(node.args) == 1:
            if node.func.id in ("all", "any"):
                gen = node.args[0]
                if not isinstance(gen, ast.GeneratorExp) or len(gen.generators) != 1:
                    raise InvalidClaim("Quantifier needs a single generator over indices")
                loop = gen.generators[0]
                if (loop.is_async or not isinstance(loop.target, ast.Name)
                        or loop.target.id in allowed or not isinstance(loop.iter, ast.Name)
                        or loop.iter.id != "indices"):
                    raise InvalidClaim("Quantifier requires a fresh variable and the indices domain")
                nested = allowed | {loop.target.id}
                self._validate(gen.elt, nested)
                for condition in loop.ifs:
                    self._validate(condition, nested)
            elif node.func.id in ("isnan", "isfinite", "abs"):
                self._validate(node.args[0], allowed)
            else:
                raise InvalidClaim("Unsupported function")
        else:
            raise InvalidClaim("Unsupported expression node: " + type(node).__name__)

    def boolean(self, env: dict[str, Any]) -> bool:
        budget = [20000]

        def truth(value: Any) -> bool:
            if type(value) is not bool:
                raise InvalidClaim("A predicate/guard must evaluate to Boolean")
            return value

        def visit(node: ast.AST, scope: dict[str, Any]) -> Any:
            budget[0] -= 1
            if budget[0] < 0:
                raise ClaimBudget("Expression evaluation budget exceeded")
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.Name):
                return scope[node.id]
            if isinstance(node, ast.Subscript):
                index = visit(node.slice, scope)
                if type(index) is not int:
                    raise InvalidClaim("Index must be an integer")
                try:
                    return scope[node.value.id][index]
                except (IndexError, KeyError) as exc:
                    raise InvalidClaim("Index outside current state") from exc
            if isinstance(node, ast.UnaryOp):
                return not truth(visit(node.operand, scope))
            if isinstance(node, ast.BoolOp):
                if isinstance(node.op, ast.And):
                    return all(truth(visit(v, scope)) for v in node.values)
                return any(truth(visit(v, scope)) for v in node.values)
            if isinstance(node, ast.Compare):
                left = visit(node.left, scope)
                for operator, right_node in zip(node.ops, node.comparators):
                    right = visit(right_node, scope)
                    if isinstance(operator, ast.Eq): result = left == right
                    elif isinstance(operator, ast.NotEq): result = left != right
                    elif isinstance(operator, ast.Lt): result = left < right
                    elif isinstance(operator, ast.LtE): result = left <= right
                    elif isinstance(operator, ast.Gt): result = left > right
                    else: result = left >= right
                    if not result:
                        return False
                    left = right
                return True
            name = node.func.id
            if name in ("all", "any"):
                gen = node.args[0]
                loop = gen.generators[0]
                def elements():
                    for index in scope["indices"]:
                        nested = {**scope, loop.target.id: index}
                        if all(truth(visit(c, nested)) for c in loop.ifs):
                            yield truth(visit(gen.elt, nested))
                return all(elements()) if name == "all" else any(elements())
            value = visit(node.args[0], scope)
            return {"isnan": math.isnan, "isfinite": math.isfinite, "abs": abs}[name](value)

        try:
            return truth(visit(self.node, env))
        except (TypeError, OverflowError) as exc:
            raise InvalidClaim("Expression type mismatch") from exc


def pointer(document: Any, path: str) -> Any:
    if not isinstance(path, str) or not path.startswith("/"):
        raise InvalidClaim("A JSON pointer is required")
    try:
        for part in path[1:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            document = document[int(part)] if isinstance(document, list) else document[part]
    except (KeyError, ValueError, TypeError, IndexError) as exc:
        raise InvalidClaim("Quote pointer does not resolve") from exc
    return document


def validate_binding(raw: str, binding: dict[str, Any]) -> None:
    if binding.get("response_sha256") != response_digest(raw):
        raise InvalidClaim("Response hash mismatch")
    if binding.get("scope") != "lit009_pivot_selection":
        raise InvalidClaim("Unsupported claim scope")
    if binding.get("origin") not in ("model_response", "synthetic_control"):
        raise InvalidClaim("Explicit claim origin required")
    reviewer = binding.get("reviewer", {})
    if not reviewer.get("identity") or reviewer.get("status") not in ("AI_REVIEW_PENDING", "HUMAN_REVIEWED"):
        raise InvalidClaim("Reviewer provenance is required; it does not certify expertise")
    resolution = binding.get("resolution")
    if resolution not in ("transcribed", "ambiguous", "unsupported", "withdrawn"):
        raise InvalidClaim("Unknown transcription resolution")
    try:
        document = json.loads(raw)
    except ValueError as exc:
        raise InvalidClaim("Response is not JSON") from exc
    anchors = binding.get("anchors", [])
    if not anchors:
        raise InvalidClaim("At least one exact prose anchor required")
    for anchor in anchors:
        if not isinstance(anchor.get("quote"), str) or not anchor["quote"] or pointer(document, anchor["pointer"]) != anchor["quote"]:
            raise InvalidClaim("Exact quote binding mismatch")
    if not binding.get("rationale"):
        raise InvalidClaim("Interpretation rationale required")
    interpretations = binding.get("interpretations", [])
    if resolution == "transcribed" and len(interpretations) != 1:
        raise InvalidClaim("Transcribed claims require exactly one interpretation")
    if resolution == "ambiguous" and len(interpretations) < 2:
        raise InvalidClaim("Ambiguity must retain at least two interpretations")
    if resolution in ("unsupported", "withdrawn") and interpretations:
        raise InvalidClaim("Unsupported/withdrawn claims must not receive invented formulas")
    if len({item.get("id") for item in interpretations}) != len(interpretations):
        raise InvalidClaim("Interpretation ids must be unique")
    for item in interpretations:
        if not item.get("id") or not item.get("meaning"):
            raise InvalidClaim("Each interpretation needs its own id and meaning")
        if item.get("mode") not in ("predicate", "ordered_scan"):
            raise InvalidClaim("Unknown declarative selection mode")
        Expression(item["expression"], {"i"} if item["mode"] == "predicate" else {"candidate", "incumbent"})
        Expression(item.get("guard", "True"), set())
        if item.get("outside_guard", "unresolved") not in ("unresolved", "classical_fallback_declared"):
            raise InvalidClaim("Outside-guard action is declarative only")


def seal_suite(role: str, requests: list[dict[str, Any]]) -> dict[str, Any]:
    if role not in ("development", "evaluator_reserved"):
        raise ValueError("Unknown suite role")
    payload = {"role": role, "requests": requests, "mother_case": "lit-009"}
    return {**payload, "sha256": digest(payload)}


def validate_suite(suite: dict[str, Any]) -> None:
    payload = {k: v for k, v in suite.items() if k != "sha256"}
    if suite.get("sha256") != digest(payload) or suite.get("role") not in ("development", "evaluator_reserved"):
        raise ValueError("Suite integrity/role mismatch")
    if suite.get("mother_case") != "lit-009" or not suite.get("requests"):
        raise ValueError("Suite needs lit-009 requests")
    for request in suite["requests"]:
        if request.get("input_sha256") != digest(request["input"]):
            raise ValueError("Request input hash mismatch")
        for state in request["states"]:
            indices = state["indices"]
            if (not indices or len(indices) > 16 or any(type(i) is not int or i < 0 for i in indices)
                    or indices != list(range(indices[0], indices[0] + len(indices)))
                    or len(indices) != len(state["values_repr"]) or state["original"] not in indices):
                raise ValueError("Invalid pivot state")
            # Check the archived oracle against direct Python max on the stored values.
            values = dict(zip(indices, map(float, state["values_repr"])))
            if max(indices, key=values.__getitem__) != state["original"]:
                raise ValueError("Archived original pivot disagrees with state")


def evaluate(raw: str, binding: dict[str, Any] | None, suite: dict[str, Any]) -> dict[str, Any]:
    validate_suite(suite)
    base = {"split": suite["role"], "suite_sha256": suite["sha256"],
            "response_sha256": response_digest(raw), "task_pass": None,
            "fallback_execution": None, "prose_fidelity_automatically_proved": False}
    if binding is None:
        return {**base, "status": "insufficient_evidence", "reason": "No reviewed binding", "interpretations": []}
    validate_binding(raw, binding)
    base.update(binding_sha256=digest(binding), origin=binding["origin"])
    if binding["resolution"] in ("unsupported", "withdrawn"):
        return {**base, "status": "claim_withdrawn" if binding["resolution"] == "withdrawn" else "insufficient_evidence",
                "reason": binding["rationale"], "interpretations": []}
    results = []
    for item in binding["interpretations"]:
        expr = Expression(item["expression"], {"i"} if item["mode"] == "predicate" else {"candidate", "incumbent"})
        guard = Expression(item.get("guard", "True"), set())
        checked = excluded = 0
        failures = []
        for request in suite["requests"]:
            for state in request["states"]:
                indices = state["indices"]
                env = {"indices": indices, "values": dict(zip(indices, map(float, state["values_repr"])))}
                if not guard.boolean(env):
                    excluded += 1
                    continue
                checked += 1
                if item["mode"] == "predicate":
                    selected = [i for i in indices if expr.boolean({**env, "i": i})]
                else:
                    incumbent = indices[0]
                    for candidate in indices[1:]:
                        if expr.boolean({**env, "candidate": candidate, "incumbent": incumbent}):
                            incumbent = candidate
                    selected = [incumbent]
                if selected != [state["original"]]:
                    failures.append({"request_id": request["id"], "input": request["input"],
                                     "state": state, "selected": selected,
                                     "original_outcome": request["outcome"]})
        status = ("contradicted" if failures else "not_exercised" if not checked else
                  "finite_guarded_pass" if excluded else "finite_scope_pass")
        results.append({"id": item["id"], "status": status, "checked_states": checked,
                        "excluded_states": excluded, "outside_guard": item.get("outside_guard", "unresolved"),
                        "failures": failures})
    statuses = {r["status"] for r in results}
    if len(results) == 1:
        status = results[0]["status"]
    elif statuses == {"contradicted"}:
        status = "all_interpretations_contradicted"
    else:
        status = "ambiguous_interpretation"  # Even all finite passes don't settle prose ambiguity.
    return {**base, "status": status, "interpretations": results}


def development_feedback(raw: str, binding: dict[str, Any] | None, suite: dict[str, Any]) -> dict[str, Any]:
    if suite.get("role") != "development":
        raise ValueError("Evaluator-reserved results cannot become revision feedback")
    result = evaluate(raw, binding, suite)
    feedback = {"kind": "semantic_feedback", "status": result["status"], "task_pass": None,
                "scope": "Reviewer-transcribed pivot selection on finite development checks only",
                "prose_fidelity_automatically_proved": False, "interpretations": []}
    for interpretation in result["interpretations"]:
        feedback["interpretations"].append({
            "id": interpretation["id"], "status": interpretation["status"],
            "checked_states": interpretation["checked_states"], "excluded_states": interpretation["excluded_states"],
            "outside_guard": interpretation["outside_guard"],
            "first_counterexample": interpretation["failures"][0] if interpretation["failures"] else None,
        })
    feedback["limits"] = ["Finite checks are not full-domain proof, whole-plan correctness or quantum execution.",
                          "Excluded states and a declared fallback are not verified repairs.",
                          "Ambiguous, withdrawn or unsupported claims are not automatic successes."]
    return feedback
