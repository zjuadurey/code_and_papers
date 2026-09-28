"""Open semantic fields of one revision and start its explicit review timer."""
import json
import sys
import time
from run_frozen import campaign as c

slot = sys.argv[1]
folder = c.HERE / "campaign"
if c.state(folder)["state"] != "all_slots_terminal":
    raise ValueError("Finish all model calls before final review")
start = c.HERE / "execution-20260926" / f"{slot}.review-start.json"
if not start.exists():
    c.save(start, {"utc": c.now(), "epoch_seconds": time.time()})
document = c.load_document(c.raw_path(folder, slot))
# Resource estimates do not establish pivot semantics; keep every semantic/guard field.
if document.get("plan"):
    document["plan"].pop("expected_resource_characteristics", None)
print(json.dumps(document, ensure_ascii=False, indent=2))
