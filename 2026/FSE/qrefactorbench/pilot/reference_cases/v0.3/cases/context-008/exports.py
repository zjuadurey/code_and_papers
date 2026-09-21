"""Validate row-labelled data and construct independent normalized copies."""

from typing import Any


def prepare_request(request: Any) -> tuple[list[str], list[dict], int]:
    if not isinstance(request, dict) or set(request) != {"columns", "rows", "copies"}:
        raise ValueError("invalid request fields")
    columns, rows, copies = request["columns"], request["rows"], request["copies"]
    if (not isinstance(columns, list) or any(not isinstance(c, str) or not c for c in columns)
            or len(set(columns)) != len(columns)):
        raise ValueError("distinct nonempty column names required")
    if not isinstance(rows, list) or type(copies) is not int or copies < 0:
        raise ValueError("invalid rows or copy count")
    ids = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"row_id", "values"}:
            raise ValueError("invalid row")
        if not isinstance(row["row_id"], str) or not row["row_id"] or row["row_id"] in ids:
            raise ValueError("unique nonempty row IDs required")
        ids.add(row["row_id"])
        if (not isinstance(row["values"], list) or len(row["values"]) != len(columns)
                or any(type(v) is not int for v in row["values"])):
            raise ValueError("row width and integer values required")
    return columns, rows, copies


def materialize(rows: list[list[int]], copies: int) -> list[list[float]]:
    output = []
    for row in rows:
        scale = sum(abs(value) for value in row)
        normalized = [value / scale if scale else 0.0 for value in row]
        for _ in range(copies):
            output.append(list(normalized))
    return output


def labels(rows: list[dict], copies: int) -> list[dict]:
    return [{"row_id": row["row_id"], "copy_index": index} for row in rows for index in range(copies)]
