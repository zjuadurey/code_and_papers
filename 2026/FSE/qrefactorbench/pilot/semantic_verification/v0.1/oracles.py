"""Private definition-based oracles; never import a candidate or its helpers."""
from itertools import combinations, product
from typing import Any


def graph_solution(problem: dict[str, Any], kind: str) -> list[int]:
    n, edges = problem['n'], {tuple(e) for e in problem['edges']}
    feasible = []
    for size in range(n + 1):
        for chosen in combinations(range(n), size):
            if kind == 'cover':
                valid = all(u in chosen or v in chosen for u, v in edges)
            else:
                valid = all(pair in edges for pair in combinations(chosen, 2))
            if valid:
                feasible.append(chosen)
    key = ((lambda x: (len(x), x)) if kind == 'cover'
           else (lambda x: (-len(x), sum(2 ** i for i in x))))
    return list(min(feasible, key=key))


def assignments(n: int) -> list[tuple[int, ...]]:
    """Canonical variable order, not integer-mask enumeration order."""
    return list(product((0, 1), repeat=n))


def sat_solutions(problem: dict[str, Any]) -> list[list[int]]:
    accepted = []
    for bits in assignments(problem['n']):
        if any(bits[i] != value for i, value in problem['locked']):
            continue
        if any(all(bits[i] != value for i, value in clause)
               for clause in problem['clauses']):
            continue
        accepted.append(list(bits))
    return accepted


def receipts(problem: dict[str, Any]) -> dict[str, Any]:
    """Derive each output bit by inequality; no XOR kernel or candidate import."""
    rows, checksum = [], 0
    for row in problem['records']:
        digits = [int((row['left'] // 2 ** i) % 2 != (row['right'] // 2 ** i) % 2)
                  for i in range(7, -1, -1)]
        bits = ''.join(map(str, digits))
        value = sum(bit * 2 ** (7 - i) for i, bit in enumerate(digits))
        checksum = (checksum + value) % 256
        rows.append({'id': row['id'], 'bits': bits, 'set_bits': sum(digits),
                     'counts': {bits: problem['repetitions']} if problem['mode'] == 'counts' else None,
                     'prefix_checksum': checksum})
    return {'record_count': len(rows), 'receipts': rows, 'checksum': checksum}


def expected(kind: str, problem: dict[str, Any]) -> Any:
    if kind in ('cover', 'clique'):
        return graph_solution(problem, kind)
    if kind == 'predicate':
        solutions = sat_solutions(problem)
        return {'marked': solutions, 'first': solutions[0] if solutions else None}
    if kind == 'receipts':
        return receipts(problem)
    raise ValueError(f'No definition oracle for {kind}')
