import json
import pytest
from program import check_records


def test_ingestion_and_membership():
    payloads = ['{"key": "a", "active": false}', '{"key": "b", "active": true}']
    assert check_records(payloads, "b") is True
    assert check_records(payloads, "a") is False
    assert check_records([], "b") is False
    with pytest.raises(json.JSONDecodeError):
        check_records(['{"key": "b", "active": true}', 'invalid'], "b")
