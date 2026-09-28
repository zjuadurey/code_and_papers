"""Small classical source checks, not a quantum implementation or benchmark scorer.

Uses unchanged public source modules and the existing environment. No network,
model, package installation, or writes outside this dossier directory.
"""
from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable
import hashlib
import importlib.util
import inspect
import itertools as it
import json
from pathlib import Path
import platform
import random
import sys
from types import ModuleType

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
sys.dont_write_bytecode = True


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(name: str, relative: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exception(call: Callable[[], object], expected: type[Exception]) -> str:
    try:
        call()
    except expected as exc:
        return type(exc).__name__
    raise AssertionError(f"Expected {expected.__name__}")


def exhaustive_match(a: str, b: str, alo: int, ahi: int, blo: int, bhi: int) -> tuple[int, int, int]:
    # Direct substring enumeration, independent of upstream's endpoint DP/index.
    candidates = [(alo, blo, 0)]
    for i in range(alo, ahi):
        for j in range(blo, bhi):
            for k in range(1, min(ahi - i, bhi - j) + 1):
                if a[i:i+k] == b[j:j+k]:
                    candidates.append((i, j, k))
    return min(candidates, key=lambda t: (-t[2], t[0], t[1]))


def check_text() -> dict:
    module = load("dossier_difflib", "sources/cpython/Lib/difflib.py")
    strings = ["".join(bits) for n in range(5) for bits in it.product("ab", repeat=n)]
    full_count = 0
    for a, b in it.product(strings, repeat=2):
        got = tuple(module.SequenceMatcher(None, a, b, autojunk=False).find_longest_match())
        require(got == exhaustive_match(a, b, 0, len(a), 0, len(b)), "text full match")
        full_count += 1
    bounded_count = 0
    for a, b in it.product([s for s in strings if len(s) <= 2], repeat=2):
        matcher = module.SequenceMatcher(None, a, b, autojunk=False)
        for alo in range(len(a)+1):
            for ahi in range(alo, len(a)+1):
                for blo in range(len(b)+1):
                    for bhi in range(blo, len(b)+1):
                        got = tuple(matcher.find_longest_match(alo, ahi, blo, bhi))
                        require(got == exhaustive_match(a, b, alo, ahi, blo, bhi), "text bounded match")
                        bounded_count += 1
    junk = tuple(module.SequenceMatcher(lambda x: x == " ", " abcd", "abcd abcd").find_longest_match())
    no_junk = tuple(module.SequenceMatcher(None, " abcd", "abcd abcd").find_longest_match())
    require(junk == (1, 0, 4) and no_junk == (0, 4, 5), "junk control")
    a, b = "x" + "a"*200, "y" + "a"*200
    auto = tuple(module.SequenceMatcher(None, a, b).find_longest_match())
    no_auto = tuple(module.SequenceMatcher(None, a, b, autojunk=False).find_longest_match())
    require(auto == (0, 0, 0) and no_auto == (1, 1, 200), "autojunk control")
    tie = tuple(module.SequenceMatcher(None, "ab", "ba", autojunk=False).find_longest_match())
    require(tie == (0, 1, 1), "earliest a then b")
    require(exhaustive_match("ab", "ba", 0, 2, 0, 2)[2] == 1, "tie witness")
    matcher = module.SequenceMatcher(None, "abcd", "bcde", autojunk=False)
    before = tuple(matcher.find_longest_match())
    matcher.set_seq1("bcde")
    after = tuple(matcher.find_longest_match())
    require(before == (1, 0, 3) and after == (0, 0, 4), "setter transition")
    errors = dict(unhashable=exception(lambda: module.SequenceMatcher(None, [], [[]]), TypeError),
                  oversized_bound=exception(lambda: module.SequenceMatcher(None, "a", "a").find_longest_match(0, 2), IndexError))
    return dict(full_binary_pairs=full_count, bounded_binary_pairs=bounded_count,
                junk_control=dict(filtered=junk, unfiltered=no_junk),
                autojunk_control=dict(default=auto, disabled=no_auto), tie=tie,
                setter_transition=[before, after], exceptions=errors,
                limitations="Finite strings only; no callback/custom equality/cache-mutation equivalence proof")


def tour_cost(matrix: np.ndarray, route: tuple | list) -> int:
    return sum(int(matrix[route[i], route[(i+1) % len(route)]]) for i in range(len(route)))


def qubo_check(matrix: np.ndarray) -> dict:
    # Proposal restricted to nonnegative integer matrices. Test its binary polynomial
    # directly, independently of the upstream recursive solver. No QUBO compiler/QPU.
    n = len(matrix)
    maximum = int(matrix.max())
    require(int(matrix.min()) >= 0, "nonnegative QUBO guard")
    penalty = n * maximum + 1
    minimum = None
    minimizers: list[tuple[int, ...]] = []
    assignments = 0
    for bits in it.product((0, 1), repeat=n*n):
        x = lambda city, pos: bits[city*n+pos]
        violations = sum((1-sum(x(i, t) for t in range(n)))**2 for i in range(n))
        violations += sum((1-sum(x(i, t) for i in range(n)))**2 for t in range(n))
        violations += (1-x(0, 0))**2
        cost = sum(int(matrix[i, j])*x(i, t)*x(j, (t+1) % n)
                   for i in range(n) for j in range(n) for t in range(n))
        energy = penalty*violations + cost
        if minimum is None or energy < minimum:
            minimum, minimizers = energy, [bits]
        elif energy == minimum:
            minimizers.append(bits)
        assignments += 1
    tours = [(0,) + p for p in it.permutations(range(1, n))]
    expected = min(tour_cost(matrix, p) for p in tours)
    decoded = []
    for bits in minimizers:
        require(all(sum(bits[i*n+t] for i in range(n)) == 1 for t in range(n)), "column feasible")
        require(all(sum(bits[i*n+t] for t in range(n)) == 1 for i in range(n)), "row feasible")
        route = tuple(next(i for i in range(n) if bits[i*n+t]) for t in range(n))
        require(route[0] == 0 and tour_cost(matrix, route) == expected, "optimal closed tour")
        decoded.append(route)
    require(minimum == expected, "QUBO objective")
    return dict(assignments=assignments, minimum=minimum, penalty=penalty, minimizers=decoded)


def check_tsp() -> dict:
    module = load("dossier_tsp", "sources/python-tsp/python_tsp/exact/dynamic_programming.py")
    matrices = [np.array([[7]], dtype=object)]
    for n in (2, 3):
        edges = [(i, j) for i in range(n) for j in range(n) if i != j]
        for weights in it.product((-1, 0, 2), repeat=len(edges)):
            matrix = np.zeros((n, n), dtype=object)
            for (i, j), w in zip(edges, weights):
                matrix[i, j] = w
            matrices.append(matrix)
    rng = random.Random(5802)
    for _ in range(40):
        matrices.append(np.array([[rng.randrange(8) if i != j else 0 for j in range(4)]
                                 for i in range(4)], dtype=object))
    calls = 0
    for matrix in matrices:
        n = len(matrix)
        original = matrix.copy()
        tours = [(0,) + p for p in it.permutations(range(1, n))]
        optimum = min(tour_cost(matrix, p) for p in tours)
        reference_route = None
        for maxsize in (None, 0, 2):
            route, value = module.solve_tsp_dynamic_programming(matrix, maxsize=maxsize)
            require(route[0] == 0 and sorted(route) == list(range(n)), "TSP permutation")
            require(value == optimum == tour_cost(matrix, route), "TSP exact cost")
            require(np.array_equal(matrix, original), "TSP input mutation")
            if reference_route is None:
                reference_route = route
            require(route == reference_route, "cache option tie stability in local environment")
            calls += 1
    matrix = np.array([[0, 1, 4], [3, 0, 1], [9, 1, 0]], dtype=object)
    routes = [(0,) + p for p in it.permutations((1, 2))]
    open_route = min(routes, key=lambda p: sum(int(matrix[p[i], p[i+1]]) for i in range(2)))
    closed_route, value = module.solve_tsp_dynamic_programming(matrix)
    require(tuple(closed_route) != open_route, "missing return edge must be detected")
    positive = np.array([[0, 2, 2], [2, 0, 2], [2, 2, 0]], dtype=object)
    # With zero penalty the all-zero assignment has energy zero < every valid tour.
    require(0 < min(tour_cost(positive, p) for p in routes), "weak penalty witness")
    qubos = [qubo_check(x) for x in (
        np.array([[0, 3], [2, 0]], dtype=object), matrix, positive,
        np.zeros((3, 3), dtype=object))]
    return dict(matrices=len(matrices), solver_calls=calls, cache_sizes=[None, 0, 2],
                exact_dtype="object/Python integers", random_seed=5802,
                exceptions=dict(empty=exception(lambda: module.solve_tsp_dynamic_programming(np.empty((0, 0))), IndexError),
                                nonsquare=exception(lambda: module.solve_tsp_dynamic_programming(np.zeros((2, 1))), IndexError)),
                closed_tour_control=dict(open_optimum=open_route, closed_optimum=closed_route, closed_cost=value),
                weak_penalty_control=dict(invalid_zero_assignment_energy=0, valid_minimum=6),
                qubo_checks=qubos, qubo_assignments=sum(q['assignments'] for q in qubos),
                limitations="Standalone unchanged module on NumPy 1.26.4, not upstream full dependency environment; ties not lex specified")


def reference_paths(graph: nx.DiGraph, source: int, target: int, cutoff: int | None) -> Counter:
    cap = len(graph)-1 if cutoff is None else cutoff
    paths = []
    for length in range(cap+1):
        for tail in it.permutations([v for v in graph if v != source], length):
            path = (source,) + tail
            if path[-1] == target and all(graph.has_edge(a, b) for a, b in zip(path, path[1:])):
                paths.append(path)
    return Counter(paths)


def check_paths() -> dict:
    import networkx.algorithms.simple_paths as implementation
    installed = Path(inspect.getsourcefile(implementation))
    pinned = ROOT / "sources/networkx/networkx/algorithms/simple_paths.py"
    require(installed.read_bytes() == pinned.read_bytes(), "installed NetworkX source differs from pinned evidence")
    edges = [(i, j) for i in range(3) for j in range(3) if i != j]
    checks = 0
    for mask in range(1 << len(edges)):
        graph = nx.DiGraph()
        graph.add_nodes_from(range(3))
        graph.add_edges_from(e for i, e in enumerate(edges) if mask & (1 << i))
        for source, target, cutoff in it.product(range(3), range(3), (-1, 0, 1, 2, None)):
            got = Counter(tuple(p) for p in nx.all_simple_paths(graph, source, target, cutoff))
            require(got == reference_paths(graph, source, target, cutoff), "path multiset comparison")
            checks += 1
    graph = nx.DiGraph([(0, 2), (2, 3), (0, 1), (1, 3)])
    ordered = list(nx.all_simple_paths(graph, 0, 3))
    require(ordered == [[0, 2, 3], [0, 1, 3]], "insertion/DFS output order")
    require(ordered != sorted(ordered) and len(ordered) > 1, "sorting and one-witness controls")
    multi = nx.MultiDiGraph()
    multi.add_edges_from([(0, 1)]*2 + [(1, 2)]*3)
    repeated = list(nx.all_simple_paths(multi, 0, 2))
    require(repeated == [[0, 1, 2]]*6, "parallel edge multiplicity")
    targets = list(nx.all_simple_paths(nx.path_graph(3, create_using=nx.DiGraph), 0, [0, 1, 2]))
    require(targets == [[0], [0, 1], [0, 1, 2]], "iterable targets / zero-edge path")
    gen = nx.all_simple_paths(graph, 99, 3)
    error = exception(lambda: next(gen), nx.NodeNotFound)
    absent_scalar = exception(lambda: list(nx.all_simple_paths(graph, 0, 99)), nx.NodeNotFound)
    absent_iterable = list(nx.all_simple_paths(graph, 0, [99]))
    require(absent_iterable == [], "absent target iterable behavior")
    changing = nx.DiGraph()
    changing.add_nodes_from([0, 1])
    gen = nx.all_simple_paths(changing, 0, 1)
    changing.add_edge(0, 1)
    lazy = list(gen)
    require(lazy == [[0, 1]], "graph consulted on iteration, not construction")
    return dict(directed_graphs=64, multiset_comparisons=checks,
                installed_module_sha256=digest(installed), ordered_paths=ordered,
                parallel_edge_multiplicity=len(repeated), iterable_targets=targets,
                deferred_source_exception=error, missing_scalar_target_exception=absent_scalar,
                missing_iterable_target=absent_iterable, mutation_before_first_next=lazy,
                limitations="Finite multiset checks plus targeted order/exception tests; not a total generator/state equivalence proof")


def run() -> dict:
    sources = json.loads((ROOT / "sources/manifest.json").read_text())
    for row in sources:
        require(digest(ROOT / row['file']) == row['sha256'], f"source hash: {row['file']}")
    protected = json.loads((ROOT / "protected-before.json").read_text())
    for relative, expected in protected.items():
        require(digest(REPO / relative) == expected, f"protected hash: {relative}")
    return dict(status="LOCAL_CLASSICAL_CHECKS_PASS", model_calls=0, qpu_calls=0,
                environment=dict(python=platform.python_version(), numpy=np.__version__, networkx=nx.__version__),
                sources_verified=len(sources), protected_files_verified=len(protected),
                text=check_text(), tsp=check_tsp(), paths=check_paths(),
                evidence_boundary="Coordinator-authored finite probes; no independent human review, gold, split, or migration claim")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Read-only exact replay against stored result")
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    target = ROOT / "validation.json"
    if args.check:
        require(target.read_text() == encoded, "exact replay differs")
    else:
        if target.exists():
            require(target.read_text() == encoded, "refusing to overwrite differing result")
        else:
            target.write_text(encoded)
    print(encoded)


if __name__ == "__main__":
    main()
