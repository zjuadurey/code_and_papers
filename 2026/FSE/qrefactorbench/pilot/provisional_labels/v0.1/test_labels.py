"""Reference/formula and scoring witnesses, never model-performance experiments."""

import copy
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys

import pytest

SPEC = importlib.util.spec_from_file_location("provisional_evaluation", Path(__file__).with_name("evaluate.py"))
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


def predictions(condition="C", *, recognized=True, plans=True):
    _, refs = evaluation.references(condition)
    responses = []
    for ref in refs:
        family = ref["migration_family"] if recognized else None
        plan = None
        if plans and family:
            plan = {
                "schema_version": "0.1.0", "contract_id": "synthetic-fixture",
                "computational_intent_id": "fixture-only", "migration_family": family,
                "formulation": "Synthetic text; not a verified plan.",
                "input_encoding": "fixture", "quantum_algorithm_family": "fixture",
                "output_decoding": "fixture", "assumptions": [], "risks": [],
                "expected_resource_characteristics": {},
            }
        responses.append({
            "schema_version": "0.2.0", "case_id": ref["case_id"], "decision": "REMAIN_CLASSICAL",
            "candidate_regions": copy.deepcopy(ref["candidate_regions"]) if recognized else [],
            "migration_family": family, "plan": plan, "rationale": "SYNTHETIC TEST FIXTURE, not a model response",
            "structural_eligibility": ref["structural_eligibility"] if recognized else False,
            "practical_suitability": None, "benchmark_supported": False,
            "computational_intent": "fixture", "assumptions": [], "risks": [],
            "contract_applicability": [],
        })
    return responses


@pytest.mark.parametrize("condition", list("ABC"))
def test_all_views_pinned_and_pending(condition):
    labels, refs = evaluation.references(condition)
    assert labels["annotation_status"] == "DRAFT" and labels["review_status"] == "PENDING"
    assert labels["human_reviews"] == [] and len(refs) == 10
    assert sum(ref["structural_eligibility"] is True for ref in refs) == 7
    assert sum(ref["structural_eligibility"] is None for ref in refs) == 3
    assert all(ref["checks"] for ref in refs)
    assert all(len({c["id"] for c in ref["checks"]}) == len(ref["checks"]) for ref in refs)


def test_bc_same_references_but_distinct_inputs():
    _, b = evaluation.references("B")
    _, c = evaluation.references("C")
    for left, right in zip(b, c):
        assert left["input_sha256"] != right["input_sha256"]
        assert {k: v for k, v in left.items() if k != "input_sha256"} == {k: v for k, v in right.items() if k != "input_sha256"}


def test_constructed_difference_without_fake_plan_correctness():
    matched = evaluation.evaluate(predictions(), "C", "SYNTHETIC_MATCHED")
    missed = evaluation.evaluate(predictions(recognized=False), "C", "SYNTHETIC_MISSED")
    assert matched["aggregate"]["structural_eligibility"]["matched"] == 7
    assert missed["aggregate"]["structural_eligibility"]["mismatched"] == 7
    assert matched["plan_coverage"] == {"reference_required": 7, "present": 7}
    assert missed["plan_coverage"] == {"reference_required": 7, "present": 0}
    assert matched["decision_agreement"] == missed["decision_agreement"] == {"matched": 10, "total": 10}
    assert all(r["plan_correct"] is None and r["task_pass"] is None for r in matched["results"])


def test_unknown_references_and_abstentions_keep_denominators():
    response = predictions()
    for row in response:
        row["structural_eligibility"] = None
    report = evaluation.evaluate(response, "C", "SYNTHETIC_NULL")
    score = report["aggregate"]["structural_eligibility"]
    assert score["reference_known"] == 7 and score["unresolved"] == 10
    assert score["agreement_on_resolved_pairs"] is None
    assert score["matched_over_known_references"] == 0
    assert report["aggregate"]["practical_suitability"]["reference_known"] == 0
    assert report["aggregate"]["practical_suitability"]["matched_over_known_references"] is None


def test_alternative_family_is_not_automatically_wrong():
    response = predictions()
    response[2]["migration_family"] = "combinatorial_optimization"
    response[2]["plan"]["migration_family"] = "combinatorial_optimization"
    report = evaluation.evaluate(response, "C", "SYNTHETIC_ALTERNATIVE")
    cell = report["results"][2]["recognition"]["migration_family"]
    assert cell["reference_agreement"] is None and "review" in cell["reason"]


def test_plan_denominator_includes_missed_structural_yes():
    response = predictions(plans=False)
    response[0]["structural_eligibility"] = False
    report = evaluation.evaluate(response, "C", "SYNTHETIC_NO_PLAN")
    assert report["plan_coverage"] == {"reference_required": 7, "present": 0}
    assert sum(r["self_reported_yes_without_plan"] for r in report["results"]) == 6


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "wrong_id", "schema", "outside", "function", "family"])
def test_invalid_responses_rejected_without_dropping(mutation):
    response = predictions()
    if mutation == "missing":
        response.pop()
    elif mutation == "duplicate":
        response.append(copy.deepcopy(response[0]))
    elif mutation == "wrong_id":
        response[0]["case_id"] = "core-001"
    elif mutation == "schema":
        response[0]["structural_eligibility"] = "YES"
    elif mutation == "outside":
        response[0]["candidate_regions"][0]["end_line"] = 99999
    elif mutation == "function":
        response[0]["candidate_regions"][0]["function"] = "prepare_request"
    else:
        response[0]["plan"]["migration_family"] = "unstructured_search"
    with pytest.raises(evaluation.DataError):
        evaluation.evaluate(response, "C", "SYNTHETIC_INVALID")


def test_changed_version_refused(monkeypatch):
    original = evaluation.sha256
    monkeypatch.setattr(evaluation, "sha256", lambda p: "changed" if p.name == "labels.json" else original(p))
    with pytest.raises(evaluation.DataError, match="artifact changed"):
        evaluation.references("C")


def test_cli_and_no_overwrite(tmp_path):
    source, output = tmp_path / "predictions.json", tmp_path / "result.json"
    source.write_text(json.dumps(predictions()))
    command = [sys.executable, "-B", str(evaluation.HERE / "evaluate.py"), "--condition", "C",
               "--predictions", str(source), "--model-id", "SYNTHETIC_CLI", "--output", str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    before = output.read_bytes()
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 2 and output.read_bytes() == before


def core(number):
    _, refs = evaluation.references("A")
    namespace = {"__name__": "trusted_local_formula_fixture"}
    # Reviewed repository-authored classical kernels only. No model code or QPU execution.
    for source in refs[number - 1]["sources"].values():
        exec(compile(source, f"public-core-{number}", "exec"), namespace)
    return namespace


def vectors(n):
    return list(itertools.product((0, 1), repeat=n))


def test_weighted_cut_mapping_against_source():
    implementation = core(1)["maxcut_bruteforce"]
    for weights in itertools.product(range(3), repeat=3):
        matrix = [[0] * 3 for _ in range(3)]
        for (i, j), w in zip(itertools.combinations(range(3), 2), weights):
            matrix[i][j] = matrix[j][i] = w
        mapped = [sum(matrix[i][j] * (x[i] + x[j] - 2*x[i]*x[j]) for i in range(3) for j in range(i+1, 3)) for x in vectors(3)]
        assert max(mapped) == implementation(matrix)[0]


def test_cover_penalty_against_source_and_wrong_tie_witness():
    implementation = core(2)["min_vertex_cover_bruteforce"]
    possible = list(itertools.combinations(range(4), 2))
    for flags in vectors(len(possible)):
        edges = [e for e, present in zip(possible, flags) if present]
        energy = lambda x: sum(x) + 5*sum((1-x[u])*(1-x[v]) for u, v in edges)
        states = vectors(4)
        minimum = min(map(energy, states))
        selected = [tuple(i for i, bit in enumerate(x) if bit) for x in states if energy(x) == minimum]
        assert min(selected) == tuple(sorted(implementation(edges, 4)))
    # Equal-size lexicographic and numeric-mask ordering are different contracts.
    assert (0, 3) < (1, 2) and (1 << 0) + (1 << 3) > (1 << 1) + (1 << 2)


def test_coloring_predicate_and_onehot_against_source():
    implementation = core(3)["kcolor_backtracking"]
    edges_possible = list(itertools.combinations(range(3), 2))
    for flags in vectors(3):
        edges = [e for e, present in zip(edges_possible, flags) if present]
        neighbors = {i: [j for j in range(3) if (min(i,j), max(i,j)) in edges] for i in range(3)}
        feasible = [c for c in itertools.product(range(2), repeat=3) if all(c[u] != c[v] for u,v in edges)]
        minimum = min(sum((sum(x[2*i:2*i+2])-1)**2 for i in range(3)) + sum(x[2*u+a]*x[2*v+a] for u,v in edges for a in range(2)) for x in vectors(6))
        assert (minimum == 0) == bool(feasible)
        if feasible:
            assert implementation(neighbors, 2) == list(min(feasible))
        else:
            with pytest.raises(ValueError):
                implementation(neighbors, 2)


def test_clique_penalty_against_source():
    implementation = core(4)["clique_bitmask"]
    possible = list(itertools.combinations(range(4), 2))
    for flags in vectors(6):
        edges = [e for e, present in zip(possible, flags) if present]
        missing = [e for e in possible if e not in edges]
        energy = lambda x: -sum(x) + 5*sum(x[u]*x[v] for u,v in missing)
        states = vectors(4)
        minimum = min(map(energy, states))
        winner = min((x for x in states if energy(x) == minimum), key=lambda x: sum(bit << i for i, bit in enumerate(x)))
        assert [i for i, bit in enumerate(winner) if bit] == implementation(4, edges)


def test_locked_sat_predicate_against_source():
    implementation = core(5)["complete"]
    clauses = [[(0, True), (1, False), (1, True)], [(0, False), (0, False), (1, True)]]
    for lock in ({}, {0: False}, {0: True}, {0: True, 1: False}):
        feasible = [list(map(bool, x)) for x in vectors(2) if all(x[i] == v for i,v in lock.items()) and all(any(x[i] == v for i,v in clause) for clause in clauses)]
        assert implementation(2, clauses, lock) == (feasible[0] if feasible else None)
    assert implementation(0, [], {}) == []


def test_knapsack_penalty_against_dynamic_program():
    implementation = core(6)["choose"]
    items = [{"weight": 2, "value": 3}, {"weight": 1, "value": 3}, {"weight": 3, "value": 0}]
    for capacity in range(7):
        penalty = 1 + sum(i["value"] for i in items)
        energies = {}
        for x in vectors(3):
            value = sum(i["value"]*bit for i,bit in zip(items,x))
            weight = sum(i["weight"]*bit for i,bit in zip(items,x))
            energies[sum(bit << i for i,bit in enumerate(x))] = min(-value + penalty*(weight+s-capacity)**2 for s in range(capacity+1))
        minimum = min(energies.values())
        assert min(mask for mask, e in energies.items() if e == minimum) == implementation(items, capacity)


def test_signed_ising_scores_against_source():
    implementation = core(7)
    for weights in itertools.product((-1, 1), repeat=3):
        pairs = [(i, j, w) for (i,j), w in zip(itertools.combinations(range(3),2), weights)]
        for x in vectors(3):
            qubo = sum(w*(2*x[i]+2*x[j]-4*x[i]*x[j]-1) for i,j,w in pairs)
            ising = -sum(w*(1-2*x[i])*(1-2*x[j]) for i,j,w in pairs)
            assert qubo == ising == implementation["score"](x, pairs)
