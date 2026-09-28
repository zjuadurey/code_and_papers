"""Offline witness: smallest numeric mask is not smallest selected-index tuple."""
from fractions import Fraction
from itertools import combinations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
path = HERE / "runs/deepseek-v4-pro/lit-002/response.txt"
formulation = json.loads(path.read_text())["plan"]["formulation"]
assert "C * sum_i 2^i x_i" in formulation
n = 4
edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
covers = [c for c in combinations(range(n), 2) if all(u in c or v in c for u, v in edges)]
assert covers == [(0, 3), (1, 2)]
assert not any(all(u == i or v == i for u, v in edges) for i in range(n))
A, P, C = 1, 10, Fraction(1, 32)
assert 0 < C < Fraction(A, 2**n)
energies = {mask: A * mask.bit_count() + P * sum((1 - (mask >> u & 1)) * (1 - (mask >> v & 1)) for u, v in edges) + C * mask
            for mask in range(1 << n)}
winner = min(energies, key=energies.get)
decoded = tuple(i for i in range(n) if winner >> i & 1)
assert min(covers) == (0, 3) and decoded == (1, 2)
print(json.dumps({
    "reviewer": "Codex coordinator; AI technical review, not gold adjudication",
    "response_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "claim_source": str(path.relative_to(HERE)), "formulation": formulation,
    "input": {"station_indices": list(range(n)), "edges": edges}, "minimum_covers": covers,
    "contract_expected": min(covers), "qubo_decoded": decoded,
    "reviewer_instantiated_scales": {"A": A, "P": P, "C": str(C)},
    "energy_by_mask": {str(k): str(v) for k, v in energies.items()},
    "finding": "The proposed positive C*numeric-mask objective selects (1,2), whereas the required selected-index tuple order selects (0,3).",
    "limit": "Refutes the stated QUBO tie objective. A correctly implemented classical verifier/fallback could still preserve external behavior; no complete migration was executed or graded."
}, ensure_ascii=False, indent=2))
