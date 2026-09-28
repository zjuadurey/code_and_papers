"""Produce a complete row-labelled table for independent downstream consumers."""

import json
import sys
from typing import Any

from exports import labels, materialize, prepare_request


def export_table(request: Any) -> dict:
    columns, rows, copies = prepare_request(request)
    values = materialize([row["values"] for row in rows], copies)
    entries = [{**label, "values": row} for label, row in zip(labels(rows, copies), values)]
    return {"columns": list(columns), "source_row_count": len(rows), "export_row_count": len(entries),
            "zero_row_ids": [row["row_id"] for row in rows if all(v == 0 for v in row["values"])],
            "column_totals": [sum(row[i] for row in values) for i in range(len(columns))], "entries": entries}


if __name__ == "__main__":
    print(json.dumps(export_table(json.load(sys.stdin)), indent=2))
