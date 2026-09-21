"""Compare a selected component package with the lowest possible catalogue charge."""

import json
import sys
from typing import Any

from packages import coefficients, describe, minimum_energy, prepare_request


def review_package(request: Any) -> dict:
    components, adjustments, selected, base = prepare_request(request)
    current = describe(components, adjustments, selected, base)
    biases, couplings = coefficients(components, adjustments)
    lowest = base + minimum_energy(biases, couplings)
    return {"component_count": len(components), "base_cost": base, "current": current,
            "lowest_cost": lowest, "avoidable_cost": current["total_cost"] - lowest}


if __name__ == "__main__":
    print(json.dumps(review_package(json.load(sys.stdin)), indent=2))
