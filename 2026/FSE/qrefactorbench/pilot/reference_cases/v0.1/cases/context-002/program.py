"""Review an existing inspection arrangement and produce station worklists."""

import json
import sys
from typing import Any

from inspection import compare_plans, describe_plan, min_vertex_cover_bruteforce, prepare_request


def review_inspections(request: Any) -> dict[str, Any]:
    """Validate, assess current coverage, propose stations, and explain work transfers."""
    names, edges, selected = prepare_request(request)
    current = describe_plan(names, edges, selected)
    proposed = describe_plan(names, edges, min_vertex_cover_bruteforce(edges, len(names)))
    return {"station_count": len(names), "connection_count": len(edges),
            "current": current, "proposed": proposed,
            "changes": compare_plans(names, edges, current, proposed)}


if __name__ == "__main__":
    print(json.dumps(review_inspections(json.load(sys.stdin)), indent=2))
