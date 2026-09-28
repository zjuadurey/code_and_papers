"""Assess alternative capacity requests without reserving or consuming lots."""

import json
import sys
from typing import Any

from lots import describe, eligible_lots, has_total, prepare_request


def review_requests(request: Any) -> dict:
    lots, requests = prepare_request(request)
    reports = []
    for row in requests:
        eligible = eligible_lots(lots, row["sites"])
        possible = has_total([lot["units"] for lot in eligible], row["target"])
        reports.append(describe(row, eligible, possible))
    return {"lot_count": len(lots), "requests": reports,
            "possible_request_ids": [r["request_id"] for r in reports if r["exact_capacity_exists"]]}


if __name__ == "__main__":
    print(json.dumps(review_requests(json.load(sys.stdin)), indent=2))
