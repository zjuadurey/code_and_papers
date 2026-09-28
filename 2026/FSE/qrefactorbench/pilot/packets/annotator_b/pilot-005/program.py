from support import prepare_offers


def feasible_bundle(offers: list[dict], target: int, budget: int) -> bool:
    for mask in range(1 << len(offers)):
        units = sum(offer["units"] for i, offer in enumerate(offers)
                    if mask & (1 << i))
        price = sum(offer["price"] for i, offer in enumerate(offers)
                    if mask & (1 << i))
        if units == target and price <= budget:
            return True
    return False


def handle_request(offers: list[dict], target: int, budget: int) -> dict:
    eligible = prepare_offers(offers)
    found = feasible_bundle(eligible, target, budget)
    return {"feasible": found, "considered": len(eligible), "target": target}
