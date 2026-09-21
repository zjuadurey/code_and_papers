from copy import deepcopy
from program import handle_request


def test_request_preserves_context():
    offers = [
        {"sku": "b", "units": 2, "price": 3, "available": True},
        {"sku": "a", "units": 1, "price": 1, "available": True},
        {"sku": "c", "units": 3, "price": 0, "available": False},
    ]
    before = deepcopy(offers)
    assert handle_request(offers, 3, 4) == {"feasible": True, "considered": 2, "target": 3}
    assert handle_request(offers, 3, 3)["feasible"] is False
    assert offers == before
    assert handle_request([], 0, 0) == {"feasible": True, "considered": 0, "target": 0}
