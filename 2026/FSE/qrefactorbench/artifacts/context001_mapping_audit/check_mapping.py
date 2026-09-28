"""Source-to-QUBO/Ising audit for context-001; classical arithmetic only.

Loads inspected source and reuses existing exact-rational polynomial utilities.
No model outputs, quantum execution, labels or production files are changed.
"""

from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import sys
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "pilot/context_adaptations/v0.1/cases/context-001"
HELPERS = ROOT / "artifacts/plan_mapping_audit/check_mappings.py"


def load_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_modules() -> tuple[Any, Any]:
    maintenance = load_file("context001_maintenance", CASE / "maintenance.py")
    previous = sys.modules.get("maintenance")
    sys.modules["maintenance"] = maintenance
    try:
        program = load_file("context001_program", CASE / "program.py")
    finally:
        if previous is None:
            sys.modules.pop("maintenance", None)
        else:
            sys.modules["maintenance"] = previous
    return maintenance, program


def qubo(request: dict) -> tuple[int, list[int], dict[tuple[int, int], int]]:
    """Build C + sum a_i x_i + sum_(i<j) b_ij x_i x_j from raw requests.

    x_i=1 means equipment i is in window 0. Upper-triangular pair coefficients
    are counted once; this is not a symmetric full-matrix x^T Q x convention.
    """
    index = {name: i for i, name in enumerate(request["equipment"])}
    constant, linear, pairs = 0, [0] * len(index), {}
    for requirement in request["requirements"]:
        i, j = sorted((index[requirement["first"]], index[requirement["second"]]))
        weight = requirement["weight"]
        constant += weight
        linear[i] -= weight
        linear[j] -= weight
        pairs[i, j] = pairs.get((i, j), 0) + 2 * weight
    return constant, linear, pairs


def raw_cost(request: dict, bits: tuple[int, ...]) -> int:
    positions = dict(zip(request["equipment"], bits))
    return sum(item["weight"] for item in request["requirements"]
               if positions[item["first"]] == positions[item["second"]])


def decode(bits: tuple[int, ...]) -> list[list[int]]:
    return [[i for i, bit in enumerate(bits) if bit == value] for value in (1, 0)]


def fixtures() -> Iterator[dict]:
    for n in range(5):
        names = [f"item-{i}" for i in range(n)]
        edges = list(combinations(names, 2))
        weights = (0, 1, 3) if n <= 3 else (0, 1)
        for values in product(weights, repeat=len(edges)):
            yield {"equipment": names, "requirements": [
                {"first": first, "second": second, "weight": weight}
                for (first, second), weight in zip(edges, values)],
                "current_windows": [names[::2], names[1::2]]}
    yield {"equipment": ["z", "a", "isolated"], "requirements": [
        {"first": "z", "second": "a", "weight": 2**60 + 1},
        {"first": "a", "second": "z", "weight": 3},
        {"first": "z", "second": "isolated", "weight": 0}],
        "current_windows": [["isolated", "z", "a"], []]}
    yield json.loads((CASE / "example_request.json").read_text())


def run() -> dict:
    helpers = load_file("existing_exact_polynomials", HELPERS)
    maintenance, program = source_modules()
    count = comparisons = report_matches = 0
    for request in fixtures():
        count += 1
        before = deepcopy(request)
        names, matrix, _ = maintenance.prepare_request(request)
        q = qubo(request)
        shift, fields, interactions = helpers.ising(q)
        # For this pure pair-equality objective: H = W/2 I + sum w_ij/2 ZiZj.
        assert shift == Fraction(q[0], 2)
        assert all(field == 0 for field in fields)
        assert all(value == Fraction(matrix[i][j], 2)
                   for (i, j), value in interactions.items())
        ranked = []
        for bits in product((0, 1), repeat=len(names)):
            comparisons += 1
            windows = decode(bits)
            observed = maintenance.evaluate_windows(names, matrix, windows)["conflict_weight"]
            direct = raw_cost(request, bits)
            energy = helpers.polynomial_value(q, bits)
            spins = tuple(1 - 2 * bit for bit in bits)
            ising_energy = shift + sum(h * z for h, z in zip(fields, spins)) + sum(
                coupling * spins[i] * spins[j] for (i, j), coupling in interactions.items())
            assert observed == direct == energy == ising_energy
            mask = sum(bit << i for i, bit in enumerate(bits))
            ranked.append((energy, mask, bits))
        energy, _, best_bits = min(ranked)
        expected_windows = decode(best_bits)
        score, original_windows = maintenance.maxcut_bruteforce(matrix)
        assert score == q[0] - energy
        assert list(original_windows) == expected_windows
        original_report = program.review_schedule(request)
        original_solver = program.maxcut_bruteforce
        # Interface check with a classical exact polynomial enumeration result.
        # This substitutes neither a quantum algorithm nor an approximate sample.
        program.maxcut_bruteforce = lambda _adj: (q[0] - energy, tuple(expected_windows))
        try:
            assert program.review_schedule(request) == original_report
            report_matches += 1
        finally:
            program.maxcut_bruteforce = original_solver
        assert request == before

    example = json.loads((CASE / "example_request.json").read_text())
    q = qubo(example)
    table = [{"mask": mask, "x_by_equipment_order": [(mask >> i) & 1 for i in range(3)],
              "conflict_weight": helpers.polynomial_value(q, tuple((mask >> i) & 1 for i in range(3)))}
             for mask in range(8)]
    minimum = min(row["conflict_weight"] for row in table)
    minimizers = [row["mask"] for row in table if row["conflict_weight"] == minimum]
    _, matrix, _ = maintenance.prepare_request(example)
    _, (first, _) = maintenance.maxcut_bruteforce(matrix)
    source_mask = sum(1 << i for i in first)
    assert source_mask == min(minimizers)
    # Deliberately faulty encodings must produce concrete counterexamples.
    mutants = {}
    for name, modified in {
        "omitted_constant": (0, q[1], q[2]),
        "wrong_linear_sign": (q[0], [-a for a in q[1]], q[2]),
        "half_pair_coefficient": (q[0], q[1], {key: value // 2 for key, value in q[2].items()}),
    }.items():
        for row in table:
            bits = tuple(row["x_by_equipment_order"])
            wrong = helpers.polynomial_value(modified, bits)
            if wrong != row["conflict_weight"]:
                mutants[name] = {"bits": bits, "correct": row["conflict_weight"], "wrong": wrong}
                break
        assert name in mutants
    bits = (1, 0, 0)
    assert raw_cost(example, bits) != raw_cost(example, bits[::-1])
    mutants["reversed_equipment_bit_order"] = {"bits": bits, "correct": raw_cost(example, bits),
                                               "wrong": raw_cost(example, bits[::-1])}
    inputs = [CASE / name for name in ("maintenance.py", "program.py", "public_task.json", "example_request.json")]
    inputs += [HELPERS, Path(__file__)]
    return {"status": "AI-ASSISTED STRUCTURAL EVIDENCE; NOT HUMAN-VALIDATED GROUND TRUTH",
            "case_id": "context-001", "input_count": count, "assignment_comparisons": comparisons,
            "exact_polynomial_report_matches": report_matches,
            "example_qubo": {"constant": q[0], "linear": q[1],
                             "upper_triangle": [{"i": i, "j": j, "coefficient": a} for (i, j), a in sorted(q[2].items())]},
            "example_assignments": table, "example_minimizers": minimizers, "source_tie_choice": source_mask,
            "mutant_counterexamples": mutants,
            "quantum_runs": 0, "model_calls": 0, "scientific_labels_changed": False,
            "inputs_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
