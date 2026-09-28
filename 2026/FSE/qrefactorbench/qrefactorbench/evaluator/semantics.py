"""Semantic oracle extension points. No inferred tolerances or quantum thresholds."""

import math
from collections.abc import Callable
from typing import Any

from . import Check

SemanticHook = Callable[[Any, dict[str, Any]], bool | None]


class SemanticOracles:
    """Explicit in-process trusted hooks; configuration never imports Python paths."""

    def __init__(self) -> None:
        self._hooks: dict[str, SemanticHook] = {}

    def register(self, hook_id: str, hook: SemanticHook) -> None:
        if hook_id in self._hooks:
            raise ValueError(f"Duplicate oracle hook: {hook_id}")
        self._hooks[hook_id] = hook

    def evaluate(self, specification: dict[str, Any] | None, output: Any) -> Check:
        if specification is None:
            return Check(None, "Missing semantic oracle")
        kind, config = specification["kind"], specification["config"]
        try:
            if kind == "deterministic_equality":
                if "expected" not in config:
                    return Check(None, "Equality oracle requires an explicit expected value")
                passed = output == config["expected"]
            elif kind == "optimization_objective":
                # Scalar quality only; feasibility is a separate, necessary check.
                if "threshold" not in config or config.get("direction") not in {"minimize", "maximize"}:
                    return Check(None, "Objective oracle requires annotated direction and threshold")
                threshold = config["threshold"]
                if type(output) not in {int, float} or type(threshold) not in {int, float}:
                    return Check(None, "Objective values must be finite numeric scalars")
                if not math.isfinite(output) or not math.isfinite(threshold):
                    return Check(False, "Non-finite objective value or threshold")
                passed = output <= threshold if config["direction"] == "minimize" else output >= threshold
            elif kind in {"property", "optimization_feasibility", "probabilistic"}:
                hook = self._hooks.get(specification.get("hook_id", ""))
                if hook is None:
                    return Check(None, f"No trusted {kind} hook registered; no thresholds assumed")
                passed = hook(output, config)
            else:
                return Check(None, f"Unsupported oracle kind: {kind}")
            if passed is not None and type(passed) is not bool:
                return Check(None, "Oracle must return a scalar bool or None")
            return Check(passed, f"{kind} oracle result")
        except Exception as exc:
            return Check(None, f"Oracle infrastructure error: {type(exc).__name__}: {exc}")
