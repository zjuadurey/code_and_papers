"""Bounded arithmetic audit of three saved plans; no model calls or label scoring.

The formulas below are manually transcribed from plan.formulation. This does not
execute model-generated code or certify an implementation/quantum optimizer.
Run from any directory; the JSON result goes to stdout for immutable capture.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations_with_replacement, product
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "pilot/baseline-v0.1/conditional-plan-diagnostic"


def load_source(case_id: str, filename: str = "program.py") -> Any:
    """Load only the fixed, inspected original source, never model output."""
    path = ROOT / "cases/pilot" / case_id / filename
    spec = importlib.util.spec_from_file_location(case_id.replace("-", "_"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assignments(n: int) -> list[tuple[int, ...]]:
    return list(product((0, 1), repeat=n))


def term_sets(n: int, weights: tuple[int, ...]) -> list[tuple]:
    """Every multiset of 0–2 ordered-index terms for the stated finite domain."""
    terms = [(i, j, w) for i in range(n) for j in range(n) for w in weights]
    return [terms_ for size in range(3)
            for terms_ in combinations_with_replacement(terms, size)]


def qubo(case_id: str, data: dict) -> tuple[int, list[int], dict]:
    """Transcribe the saved plan, with diagonal x_i²=x_i normalization."""
    n = data["n"]
    constant, linear, pairs = 0, [0] * n, {}

    def add_pair(i: int, j: int, coefficient: int) -> None:
        if i == j:
            linear[i] += coefficient
        else:
            key = tuple(sorted((i, j)))
            pairs[key] = pairs.get(key, 0) + coefficient

    if case_id == "pilot-003":
        # Minimize -C, not C; the API returns max(C), hence negate the minimum.
        for i, j, w in data["terms"]:
            linear[i] -= w
            linear[j] -= w
            add_pair(i, j, 2 * w)
    elif case_id == "pilot-006":
        linear[:] = data["biases"]
        for i, j, w in data["terms"]:
            add_pair(i, j, w)
    else:
        for i, job in enumerate(data["jobs"]):
            constant += job["left_cost"]
            linear[i] += job["right_cost"] - job["left_cost"]
        for i, j, w in data["terms"]:
            constant += w
            linear[i] -= w
            linear[j] -= w
            add_pair(i, j, 2 * w)
    return constant, linear, pairs


def polynomial_value(q: tuple, bits: tuple) -> int:
    constant, linear, pairs = q
    return constant + sum(a * x for a, x in zip(linear, bits)) + sum(
        a * bits[i] * bits[j] for (i, j), a in pairs.items())


def ising(q: tuple) -> tuple:
    """Exact rational expansion of x=(1-z)/2; retain the constant shift."""
    constant, linear, pairs = q
    shift = Fraction(constant) + sum(Fraction(a, 2) for a in linear)
    fields = [-Fraction(a, 2) for a in linear]
    interactions = {}
    for (i, j), a in pairs.items():
        weight = Fraction(a, 4)
        shift += weight
        fields[i] -= weight
        fields[j] -= weight
        interactions[i, j] = weight
    return shift, fields, interactions


def source_assignment_value(case_id: str, data: dict, x: tuple) -> int:
    """Direct original per-assignment behavior, separate from the polynomial."""
    if case_id == "pilot-003":
        return sum(w for i, j, w in data["terms"] if x[i] != x[j])
    if case_id == "pilot-006":
        return sum(b * bit for b, bit in zip(data["biases"], x)) + sum(
            w * x[i] * x[j] for i, j, w in data["terms"])
    return sum(job["right_cost"] if x[i] else job["left_cost"]
               for i, job in enumerate(data["jobs"])) + sum(
        w for i, j, w in data["terms"] if x[i] == x[j])


def fixtures(case_id: str):
    for n in range(3):
        weights = (-2, 0, 3) if case_id == "pilot-006" else (0, 1, 3)
        for terms in term_sets(n, weights):
            if case_id == "pilot-003":
                yield {"n": n, "terms": terms}
            elif case_id == "pilot-006":
                for biases in product((-2, 0, 3), repeat=n):
                    yield {"n": n, "terms": terms, "biases": biases}
            else:
                for costs in product(((0, 0), (0, 2), (3, -1)), repeat=n):
                    jobs = [{"name": f"job-{i}", "left_cost": a, "right_cost": b}
                            for i, (a, b) in enumerate(costs)]
                    yield {"n": n, "terms": terms, "jobs": jobs}
    # One extra fixture checks >2 terms, n=3 and integer arithmetic beyond 2**53.
    huge = 2**60 + 1
    data = {"n": 3, "terms": [(0, 0, 3), (0, 1, huge), (0, 1, 3),
                                (1, 0, 1), (1, 2, 0)]}
    if case_id == "pilot-006":
        data["biases"] = [-huge, 0, 3]
        data["terms"].append((2, 1, -huge))
    if case_id == "pilot-009":
        data["jobs"] = [{"name": f"job-{i}", "left_cost": a, "right_cost": b}
                        for i, (a, b) in enumerate(((0, huge), (-3, 1), (2, 0)))]
    yield data


def original_optimum(module: Any, case_id: str, data: dict) -> int:
    if case_id == "pilot-003":
        return module.best_partition_score(data["n"], data["terms"])
    if case_id == "pilot-006":
        return module.minimum_energy(data["biases"], data["terms"])
    return module.best_cost(data["jobs"], data["terms"])


def audit(case_id: str, module: Any) -> dict:
    count = comparisons = 0
    witnesses: dict[str, dict] = {}
    for data in fixtures(case_id):
        count += 1
        q = qubo(case_id, data)
        energies = []
        original_values = []
        for bits in assignments(data["n"]):
            original = source_assignment_value(case_id, data, bits)
            energy = polynomial_value(q, bits)
            assert energy == (-original if case_id == "pilot-003" else original)
            spins = tuple(1 - 2 * bit for bit in bits)
            assert polynomial_value(ising(q), spins) == energy
            comparisons += 1
            energies.append(energy)
            original_values.append(original)
        decoded = -min(energies) if case_id == "pilot-003" else min(energies)
        optimum = original_optimum(module, case_id, data)
        assert decoded == optimum, (case_id, data)

        # Deliberate audit mutants, NOT defects attributed to the model response.
        mutants = {
            "drop_ising_constant": [e - ising(q)[0] for e in energies],
        }
        for name, terms in {
            "drop_repeated_terms": tuple(dict.fromkeys(data["terms"])),
            "drop_self_terms": tuple(t for t in data["terms"] if t[0] != t[1]),
        }.items():
            altered = qubo(case_id, {**data, "terms": terms})
            mutants[name] = [polynomial_value(altered, x) for x in assignments(data["n"])]
        if case_id == "pilot-003":
            mutants["reverse_optimization_direction"] = [-e for e in energies]
        for name, wrong in mutants.items():
            if name not in witnesses and wrong != energies:
                index = next(i for i, pair in enumerate(zip(energies, wrong)) if pair[0] != pair[1])
                witnesses[name] = {"input": data, "bits": assignments(data["n"])[index],
                                   "correct_energy": str(energies[index]),
                                   "mutant_energy": str(wrong[index])}
        # Repeat this feasible, suboptimal sample any number of times: rescoring
        # still cannot make its value equal the original exact API result.
        if "sample_only_is_not_exact" not in witnesses:
            for bits, value in zip(assignments(data["n"]), original_values):
                if value != optimum:
                    witnesses["sample_only_is_not_exact"] = {
                        "input": data, "sampled_bits": bits,
                        "verified_sample_value": value, "exact_api_value": optimum}
                    break
    expected = {"drop_ising_constant", "drop_repeated_terms", "sample_only_is_not_exact"}
    expected.add("reverse_optimization_direction" if case_id == "pilot-003" else "drop_self_terms")
    assert expected <= witnesses.keys()
    return {"case_id": case_id, "fixtures": count, "assignment_comparisons": comparisons,
            "original_optimum_comparisons": count, "mapping_checks": "PASS",
            "mutation_and_certification_witnesses": witnesses,
            "source_of_formulas": "saved plan.formulation; manual AI-assisted transcription",
            "full_contract_preservation": "NOT ESTABLISHED",
            "quantum_execution_and_resources": "NOT TESTED"}


def main() -> None:
    inputs = [Path(__file__)]
    results = []
    previous_support = sys.modules.get("support")
    try:
        sys.modules["support"] = load_source("pilot-009", "support.py")
        for case_id in ("pilot-003", "pilot-006", "pilot-009"):
            plan_path = EXPERIMENT / "parsed" / f"{case_id}.json"
            assert json.loads(plan_path.read_text())["plan"] is not None
            prompt = ROOT / "pilot/packets-v0.1/baseline/prompts" / f"{case_id}.md"
            # Check that the source being audited is the source the model saw.
            for block in prompt.read_text().split("\nFILE: ")[1:]:
                filename, numbered = block.split("\n", 1)
                lines = [match.group(1) for line in numbered.splitlines()
                         if (match := re.match(r"\s*\d+ \| (.*)$", line))]
                assert lines == (ROOT / "cases/pilot" / case_id / filename).read_text().splitlines()
            inputs.append(prompt)
            inputs.extend([plan_path, EXPERIMENT / "raw" / f"{case_id}.txt",
                           ROOT / "cases/pilot" / case_id / "program.py",
                           ROOT / "cases/pilot" / case_id / "public_task.json"])
            results.append(audit(case_id, load_source(case_id)))
    finally:
        if previous_support is None:
            sys.modules.pop("support", None)
        else:
            sys.modules["support"] = previous_support
    inputs.append(ROOT / "cases/pilot/pilot-009/support.py")
    print(json.dumps({"status": "BOUNDED AI-ASSISTED EVIDENCE — NOT GROUND TRUTH",
                      "python": sys.version, "cases": results,
                      "inputs_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in inputs}}, indent=2))


if __name__ == "__main__":
    main()
