"""Fraction-based values oracle and observable row-identity regressions."""

from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

import pytest
import program


def oracle(request):
    entries = []
    for row in request["rows"]:
        scale = sum(abs(v) for v in row["values"])
        for i in range(request["copies"]):
            entries.append({"row_id": row["row_id"], "copy_index": i,
                            "values": [float(Fraction(v, scale)) if scale else 0.0 for v in row["values"]]})
    return {"columns": request["columns"][:], "source_row_count": len(request["rows"]), "export_row_count": len(entries),
            "zero_row_ids": [r["row_id"] for r in request["rows"] if not any(r["values"])],
            "column_totals": [sum(e["values"][i] for e in entries) for i in range(len(request["columns"]))],
            "entries": entries}


def example():
    return json.loads(Path(__file__).with_name("example_request.json").read_text())


def test_bounded_tables_including_empty_columns_rows_and_zero_copies():
    tables = 0
    for width in range(3):
        columns = [f"c{width-i}" for i in range(width)]
        possible = list(product((-1, 0, 2), repeat=width))
        for n in range(3):
            for rows in product(possible, repeat=n):
                for copies in range(3):
                    request = {"columns": columns, "rows": [{"row_id": str(i), "values": list(r)} for i, r in enumerate(rows)],
                               "copies": copies}
                    before = deepcopy(request)
                    assert program.export_table(request) == oracle(request)
                    assert request == before
                    tables += 1
    assert tables == 321


def test_example_and_large_signed_integers():
    assert program.export_table(example()) == oracle(example())
    request = {"columns": ["a", "b"], "rows": [{"row_id": "r", "values": [10**500, -(10**500)]}], "copies": 2}
    assert program.export_table(request) == oracle(request)


def test_copies_are_independent_and_input_is_not_aliased():
    request = example()
    before = deepcopy(request)
    report = program.export_table(request)
    frozen = deepcopy(report)
    report["entries"][0]["values"][0] = 999
    assert report["entries"][1:] == frozen["entries"][1:]
    report["columns"].append("extra")
    assert request == before


def invalid_requests():
    yield None
    yield {}
    for key, value in [("columns", None), ("columns", ["a", "a"]), ("columns", [[]]), ("rows", {}),
                       ("copies", -1), ("copies", True), ("copies", 1.5), ("extra", 1)]:
        yield dict(example(), **{key: value})
    for key, value in [("row_id", ""), ("row_id", []), ("values", [1]), ("values", [True, 1]),
                       ("values", [float("inf"), 0]), ("values", [None, 0]), ("values", [1.5, 0])]:
        request = example()
        request["rows"][-1][key] = value
        yield request
    request = example()
    request["rows"].append(deepcopy(request["rows"][0]))
    yield request
    request = example()
    request["copies"] = 0
    request["rows"][-1]["values"] = []
    yield request


@pytest.mark.parametrize("payload", list(invalid_requests()))
def test_validate_even_zero_copy_requests_before_materialization(payload, monkeypatch):
    request = payload
    monkeypatch.setattr(program, "materialize", lambda *_: pytest.fail("invalid input reached materializer"))
    with pytest.raises(ValueError):
        program.export_table(request)


def test_value_correct_but_aliased_copies_are_detectable(monkeypatch):
    def bad(rows, copies):
        output = []
        for row in rows:
            scale = sum(abs(v) for v in row)
            shared = [v / scale if scale else 0.0 for v in row]
            output.extend([shared] * copies)
        return output
    monkeypatch.setattr(program, "materialize", bad)
    report = program.export_table(example())
    assert report == oracle(example())  # Value equality alone misses this bug.
    report["entries"][0]["values"][0] = 999
    assert report["entries"][1]["values"][0] == 999


def test_signed_denominator_bug_and_reordered_labels_are_detected(monkeypatch):
    monkeypatch.setattr(program, "materialize", lambda rows, copies: [[0.0] * len(row) for row in rows for _ in range(copies)])
    assert program.export_table(example()) != oracle(example())
    monkeypatch.undo()
    original = program.labels
    monkeypatch.setattr(program, "labels", lambda rows, copies: list(reversed(original(rows, copies))))
    assert program.export_table(example()) != oracle(example())
