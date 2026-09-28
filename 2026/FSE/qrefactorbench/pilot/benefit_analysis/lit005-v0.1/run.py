"""Deterministic finite diagnostics. Write to a NEW output file only."""
import argparse
import hashlib
import importlib.util
import json
import math
from itertools import combinations_with_replacement, product
from pathlib import Path

from analysis import assignments, build_oracle, enumerate_first, lex_dpll, prefix_repair

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-005"


def source_module():
    spec = importlib.util.spec_from_file_location("lit005_reference", CASE / "kernel.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_clauses():
    request = json.loads((CASE / "example_request.json").read_text())
    return [[(request["features"].index(x["feature"]), x["enabled"])
             for x in rule["any"]] for rule in request["rules"]]


def cases(base):
    for mask in range(64):
        clauses = [c for i, c in enumerate(base) if mask & (1 << i)]
        for locks in product((None, False, True), repeat=3):
            yield 3, clauses, {i: v for i, v in enumerate(locks) if v is not None}
    for n in range(1, 4):
        literals = list(product(range(n), (False, True)))
        for clause in combinations_with_replacement(literals, 3):
            yield n, [list(clause)], {}
    yield 0, [], {}


def diagnose():
    binding = json.loads((HERE / "input-binding.json").read_text())
    for path, expected in binding.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    ref = source_module()
    base = source_clauses()
    totals = {"formula_lock_instances": 0, "oracle_basis_checks": 0,
              "lex_dpll_checks": 0, "prefix_repair_checks": 0}
    for n, clauses, locks in cases(base):
        totals["formula_lock_instances"] += 1
        expected = ref.complete(n, clauses, locks)
        assert lex_dpll(n, clauses, locks) == expected
        totals["lex_dpll_checks"] += 1
        classical, baseline_calls = enumerate_first(n, clauses, locks)
        assert classical == expected
        oracle = build_oracle(n, clauses, locks)
        domain = list(assignments(n, locks))
        for bits in domain:
            free_bits = [bits[i] for i in oracle.free]
            output, phase = oracle.apply_basis(free_bits)
            assert output[:len(free_bits)] == free_bits
            assert not any(output[len(free_bits):])
            assert phase == (-1 if ref.conforms(bits, clauses, locks) else 1)
            totals["oracle_basis_checks"] += 1
        for witness in domain + [None]:
            answer, checks = prefix_repair(n, clauses, locks, witness)
            assert answer == expected
            assert checks >= baseline_calls
            totals["prefix_repair_checks"] += 1
    good = [x for x in assignments(3, {}) if ref.conforms(x, base, {})]
    probability = math.sin(3 * math.asin(math.sqrt(len(good) / 8))) ** 2
    return {"kind": "finite coordinator diagnostic; no physical timing or model/QPU run",
            "counts": totals, "all_checks_passed": True,
            "source_example": {"solutions": good, "domain_size": 8,
                "one_ideal_grover_iteration_any_solution_probability": probability,
                "one_ideal_grover_iteration_required_first_probability": probability / len(good),
                "probability_note": "analytic known-M diagnostic, not a measured run or freely available solution count",
                "oracle": build_oracle(3, base, {}).resources(),
                "classical_same_domain_calls": enumerate_first(3, base, {})[1],
                "repair_calls_first_witness": prefix_repair(3, base, {}, good[0])[1],
                "repair_calls_later_witness": prefix_repair(3, base, {}, good[1])[1]}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = diagnose()
    with args.output.open("x") as file:
        json.dump(result, file, indent=2, sort_keys=True)
        file.write("\n")
    print(json.dumps(result, sort_keys=True))
