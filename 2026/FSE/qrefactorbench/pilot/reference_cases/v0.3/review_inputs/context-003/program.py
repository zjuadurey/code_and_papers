"""Review whether partial feature profiles can be completed under catalogue rules."""

import json
import sys
from typing import Any

from configurations import clauses_for_profile, describe_profile, has_assignment, prepare_request


def review_profiles(request: Any) -> dict:
    names, clauses, profiles = prepare_request(request)
    reports = [describe_profile(names, profile, has_assignment(len(names), clauses_for_profile(names, clauses, profile)))
               for profile in profiles]
    return {"feature_count": len(names), "profile_count": len(profiles), "profiles": reports,
            "compatible_profile_ids": [row["profile_id"] for row in reports if row["completion_exists"]],
            "incompatible_profile_ids": [row["profile_id"] for row in reports if not row["completion_exists"]]}


if __name__ == "__main__":
    print(json.dumps(review_profiles(json.load(sys.stdin)), indent=2))
