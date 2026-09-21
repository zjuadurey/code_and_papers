"""Offline, reviewer-transcribed witness for one Flash formulation branch."""
from itertools import combinations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
response = HERE / "runs/deepseek-flash/lit-002/response.txt"
formulation = json.loads(response.read_text())["plan"]["formulation"]
assert "superincreasing secondary weights" in formulation and "added to x_i" in formulation

# Two stations connected by one edge; both singleton covers have minimum size.
# The public contract chooses the lexicographically first selected-index tuple.
covers = list(combinations(range(2), 1))
weights = [2, 1]
assert weights[0] > sum(weights[1:]) and weights[1] > 0
expected = min(covers)
chosen = min(covers, key=lambda cover: sum(weights[i] for i in cover))
assert expected == (0,) and chosen == (1,)

# Include dominating cardinality/coverage terms, so the failure is tie direction.
# These constants instantiate the unspecified scales; they are not model constants.
A, B = 3, 10
energy = {mask: A * mask.bit_count() + B * (1 - (mask & 1)) * (1 - (mask >> 1 & 1))
          + sum(weights[i] * (mask >> i & 1) for i in range(2)) for mask in range(4)}
assert min(energy, key=energy.get) == 2  # selects index 1

print(json.dumps({
    "reviewer": "Codex coordinator; AI technical review, not gold adjudication",
    "response_sha256": hashlib.sha256(response.read_bytes()).hexdigest(),
    "claim_source": str(response.relative_to(HERE)), "formulation": formulation,
    "input": {"station_indices": [0, 1], "edges": [[0, 1]]},
    "minimum_covers": covers, "secondary_weights": weights,
    "contract_expected": expected, "positive_weight_minimizer": chosen,
    "reviewer_instantiated_scales": {"A": A, "B": B}, "energy_by_mask": energy,
    "finding": "Positive superincreasing weights added to selected bits in minimization prefer the wrong selected-index tuple.",
    "limit": "Refutes this encoding branch only. The separate exact two-stage alternative is not refuted. No model-generated program, quantum circuit, or full migration was executed. Labels and scores unchanged."
}, ensure_ascii=False, indent=2))
