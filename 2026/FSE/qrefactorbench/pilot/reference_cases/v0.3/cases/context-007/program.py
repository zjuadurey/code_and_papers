"""Review a staging selection and produce a complete proposed transfer manifest."""

import json
import sys
from typing import Any

from archive import describe, prepare_request, select_items, transfer_manifest


def review_archive(request: Any) -> dict:
    items, current, capacity = prepare_request(request)
    chosen = select_items([i["size"] for i in items], [i["priority"] for i in items], capacity)
    proposed = [items[i]["item_id"] for i in chosen]
    return {"item_count": len(items), "capacity": capacity,
            "current": describe(items, current, capacity), "proposed": describe(items, proposed, capacity),
            "changes": {"add": [n for n in proposed if n not in current],
                        "remove": [i["item_id"] for i in items if i["item_id"] in current and i["item_id"] not in proposed]},
            "manifest": transfer_manifest(items, proposed)}


if __name__ == "__main__":
    print(json.dumps(review_archive(json.load(sys.stdin)), indent=2))
