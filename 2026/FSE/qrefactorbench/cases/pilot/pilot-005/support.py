def prepare_offers(offers: list[dict]) -> list[dict]:
    eligible = [dict(offer) for offer in offers if offer["available"]]
    return sorted(eligible, key=lambda offer: offer["sku"])
