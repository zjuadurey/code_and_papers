"""Produce ordered masking receipts and optional repeated-outcome histograms."""
import json
import sys
from common import fields, integer, names
from kernel import encode


def review(request):
    fields(request, ("records", "repetitions", "mode"))
    repetitions = integer(request["repetitions"], 1)
    if request["mode"] not in ("inspect", "counts") or not isinstance(request["records"], list):
        raise ValueError("invalid mode or records")
    for row in request["records"]:
        fields(row, ("id", "left", "right"))
        if integer(row["left"]) > 255 or integer(row["right"]) > 255:
            raise ValueError("eight-bit integers required")
    names([row["id"] for row in request["records"]])
    receipts, checksum = [], 0
    for row in request["records"]:
        value, text = encode(row["left"], row["right"])
        checksum = (checksum + value) % 256
        receipts.append({"id": row["id"], "bits": text, "set_bits": text.count("1"),
                         "counts": {text: repetitions} if request["mode"] == "counts" else None,
                         "prefix_checksum": checksum})
    return {"record_count": len(receipts), "receipts": receipts, "checksum": checksum}


if __name__ == "__main__":
    print(json.dumps(review(json.load(sys.stdin)), indent=2))
