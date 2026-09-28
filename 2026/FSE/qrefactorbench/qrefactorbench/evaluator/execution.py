"""Static checks plus an explicit trusted-code subprocess interface.

The subprocess helper is NOT a security sandbox. CLI evaluation never calls it.
"""

import ast
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from . import Check


def check_syntax(files: Mapping[str, str]) -> Check:
    if not files:
        return Check(None, "No generated files; patches are not automatically applied")
    python_files = {name: text for name, text in files.items() if name.endswith(".py")}
    if not python_files:
        return Check(None, "No Python artifacts supplied")
    try:
        for name, text in python_files.items():
            compile(text, name, "exec")
    except (SyntaxError, ValueError) as exc:
        return Check(False, str(exc))
    return Check(True, "All supplied Python artifacts parse")


def _signature(source: str, name: str) -> tuple[bool, str] | None:
    parts = name.split(".")
    nodes = ast.parse(source).body
    found: Any = None
    for part in parts:
        found = next((n for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == part), None)
        if found is None:
            return None
        nodes = found.body
    if not isinstance(found, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None
    # Signatures include argument names/kinds/defaults and annotations. This is a
    # conservative static diagnostic, not proof of runtime API equivalence.
    return isinstance(found, ast.AsyncFunctionDef), ast.dump(found.args, include_attributes=False)


def check_interface(reference: str, generated: str, functions: Sequence[str]) -> Check:
    if not functions:
        return Check(None, "No expected interfaces declared")
    try:
        for name in functions:
            before, after = _signature(reference, name), _signature(generated, name)
            if before is None:
                return Check(None, f"Reference interface not found: {name}")
            if before != after:
                return Check(False, f"Static signature changed or disappeared: {name}")
    except (SyntaxError, ValueError) as exc:
        return Check(False, str(exc))
    return Check(True, "Declared static signatures match; runtime interface tests remain necessary")


def run_trusted_python(arguments: Sequence[str], *, cwd: Path,
                       trusted: bool = False, timeout: float = 10.0) -> Check:
    """Run researcher-reviewed local Python only; caller supplies argv, not shell."""
    if not trusted:
        return Check(None, "Execution requires explicit trusted=True; this helper is not a sandbox")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    try:
        result = subprocess.run([sys.executable, *arguments], cwd=cwd, timeout=timeout,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return Check(result.returncode == 0, f"Python process exit code {result.returncode}")
    except subprocess.TimeoutExpired:
        return Check(False, "Execution timed out")
    except OSError as exc:
        return Check(None, f"Execution infrastructure error: {exc}")


def check_imports(module: str, *, cwd: Path, trusted: bool = False,
                  timeout: float = 10.0) -> Check:
    """Importing executes code and therefore uses the same explicit trust gate."""
    return run_trusted_python(
        ["-c", "import importlib, sys; importlib.import_module(sys.argv[1])", module],
        cwd=cwd, trusted=trusted, timeout=timeout)


def static_execution(files: Mapping[str, str]) -> dict[str, Any]:
    missing = Check(None, "Not run: CLI performs static evaluation only").to_dict()
    return {"syntax": check_syntax(files).to_dict(), "imports": missing.copy(),
            "execution": missing.copy(), "interface": missing.copy()}
