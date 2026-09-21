import json


def contains_record(records: list[dict], target: str) -> bool:
    for record in records:
        if record["active"] and record["key"] == target:
            return True
    return False


def check_records(payloads: list[str], target: str) -> bool:
    records = [json.loads(payload) for payload in payloads]
    return contains_record(records, target)
