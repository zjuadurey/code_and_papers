"""Illustrate original context behavior; no migration or scientific label check.

Run with an existing Python, redirecting stdout to a new JSON output path.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def load(case_id, name):
    path = ROOT / "cases/pilot" / case_id / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    records = {}
    previous = sys.modules.get("support")
    try:
        support = load("pilot-005", "support")
        sys.modules["support"] = support
        program = load("pilot-005", "program")
        offers = [
            {"sku": "b", "units": 2, "price": 3, "available": True},
            {"sku": "a", "units": 1, "price": 1, "available": True},
            {"sku": "c", "units": 3, "price": 0, "available": False},
        ]
        before = copy.deepcopy(offers)
        prepared = support.prepare_offers(offers)
        actual = program.handle_request(offers, 3, 3)
        unfiltered = program.feasible_bundle(offers, 3, 3)
        assert actual == {"feasible": False, "considered": 2, "target": 3}
        assert unfiltered is True and offers == before
        records["pilot-005"] = {
            "input": offers, "target": 3, "budget": 3,
            "public_handler_result": actual,
            "kernel_on_unfiltered_input": unfiltered,
            "prepared_skus": [row["sku"] for row in prepared],
            "kernel_on_reversed_prepared_input": program.feasible_bundle(prepared[::-1], 3, 3),
            "caller_input_unchanged": offers == before,
            "interpretation": "Filtering changes the answer. Reordering this valid prepared input does not.",
        }
        sys.modules["support"] = load("pilot-009", "support")
        program = load("pilot-009", "program")
        jobs = [{"name": "b", "left_cost": 0, "right_cost": 2},
                {"name": "a", "left_cost": 0, "right_cost": 2}]
        report = program.placement_report(jobs, [(0, 1, 5)])
        assert report == {"cost": 2, "names": ["b", "a"], "count": 2}
        errors = {}
        for label, invalid_jobs, links in [
            ("non_string_name", [{"name": 7, "left_cost": 0, "right_cost": 2}], []),
            ("out_of_range_link", jobs, [(0, 2, 3)]),
            ("negative_penalty", jobs, [(0, 1, -1)]),
        ]:
            try:
                program.placement_report(invalid_jobs, links)
            except ValueError as exc:
                errors[label] = str(exc)
            else:
                raise AssertionError(label)
        records["pilot-009"] = {
            "input": jobs, "links": [(0, 1, 5)], "public_handler_result": report,
            "specified_error_observations": errors,
            "interpretation": "Public output contains exact cost and original name order, not an assignment.",
        }
    finally:
        if previous is None:
            sys.modules.pop("support", None)
        else:
            sys.modules["support"] = previous
    print(json.dumps({"kind": "original-code context illustrations, not ground truth",
                      "observations": records}, indent=2))


if __name__ == "__main__":
    main()
