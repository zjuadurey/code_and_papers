"""Review current, quick-preview and requested release groups against check history."""

# Adapted source portions: C2|Q> Dataset, CC BY 4.0; see supplied NOTICE.txt.

import json
import sys
from typing import Any

from catalog import eligible, latest_results, prepare
from reports import compatible, describe, preview, relation


def review_releases(request: Any) -> dict:
    versions, checks, requests = prepare(request)
    latest = latest_results(checks)
    results = []
    for row in requests:
        names = eligible(versions, row["members"])
        matrix = relation(names, latest)
        first = [names[i] for i in preview(matrix)]
        report = {"request_id": row["request_id"], "eligible": names,
                  "current": describe(versions, row["current"], latest),
                  "preview": describe(versions, first, latest), "proposed": None, "changes": None}
        if row["mode"] == "select":
            best = []
            for mask in range(1 << len(names)):
                subset = [i for i in range(len(names)) if mask & (1 << i)]
                if compatible(subset, matrix) and len(subset) > len(best):
                    best = subset
            chosen = [names[i] for i in best]
            report["proposed"] = describe(versions, chosen, latest)
            report["changes"] = {"add": [v for v in chosen if v not in row["current"]],
                                 "remove": [v["version_id"] for v in versions
                                            if v["version_id"] in row["current"] and v["version_id"] not in chosen]}
        results.append(report)
    return {"version_count": len(versions), "check_count": len(checks), "pair_count": len(latest),
            "superseded_check_count": len(checks) - len(latest), "requests": results}


if __name__ == "__main__":
    print(json.dumps(review_releases(json.load(sys.stdin)), indent=2))
