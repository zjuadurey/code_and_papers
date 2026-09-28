"""Post-run stronger-comparator and source-contract audit; no inference/QPU."""
from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

import run as r


def gray(n: int, edges: list) -> tuple[int, int]:
    neighbors = [[] for _ in range(n)]
    for u, v, w in edges:
        neighbors[u].append((v, w))
        neighbors[v].append((u, w))
    mask = current = best = best_mask = 0
    for ordinal in range(1, 1 << (n-1)):
        bit = (ordinal & -ordinal).bit_length()-1
        current += sum(w if ((mask >> bit) & 1) == ((mask >> v) & 1) else -w
                       for v, w in neighbors[bit])
        mask ^= 1 << bit
        if current > best or (current == best and mask < best_mask):
            best, best_mask = current, mask
    return best, best_mask


def main() -> None:
    output = r.HERE/'audit'
    output.mkdir(exist_ok=False)
    spec = importlib.util.spec_from_file_location('original_maxcut_kernel',
        r.ROOT/'pilot/source_adaptations/v0.1/cases/lit-001/kernel.py')
    kernel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel)
    finite = []
    # All 64 unweighted four-node graphs, including empty/disconnected/tied graphs.
    pairs = [(i, j) for i in range(4) for j in range(i+1, 4)]
    for code in range(64):
        edges = [(u, v, 1) for i, (u, v) in enumerate(pairs) if code & (1 << i)]
        matrix = [[0]*4 for _ in range(4)]
        for u, v, w in edges:
            matrix[u][v] = matrix[v][u] = w
        score, (left, _) = kernel.maxcut_bruteforce(matrix)
        expected = (score, sum(1 << v for v in left))
        observed = r.solve(4, edges, 10)
        assert observed['complete']
        assert (observed['optimum'], observed['minimum_mask']) == expected == gray(4, edges)
        finite.append(code)
    timings = []
    # Added after the frozen run: strengthen, never weaken, the classical comparator.
    for n in (8, 16):
        for seed in r.SEEDS:
            edges = r.graph(n, seed)
            expected = json.loads((r.HERE/f'run/classical-{n}-{seed}.json').read_text())
            batches = []
            for _ in range(3):
                start = time.perf_counter()
                actual = gray(n, edges)
                batches.append(time.perf_counter()-start)
            assert actual == (expected['optimum'], expected['minimum_mask'])
            timings.append({'n': n, 'seed': seed, 'seconds': batches,
                            'best_seconds': min(batches), 'matches_milp': True})
    r.save(output/'validation.json', {'original_kernel_all_four_node_graphs': len(finite),
        'milp_and_gray_both_match_source': True, 'gray_timings': timings,
        'posthoc_note': 'Added optimized enumeration comparator after frozen scale run; only strengthens baseline.',
        'certificate_obstruction': 'Every generated graph includes positive triangle 0-1-2; all-edges-cut certificate cannot accept any mask.'})
    r.save(output/'manifest.json', {p.name: r.digest(p) for p in output.iterdir() if p.is_file()})


if __name__ == '__main__':
    main()
