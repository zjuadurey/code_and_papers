import hashlib
from collections.abc import Callable


def ledger_digest(events: list[bytes], audit: Callable[[int, str], None]) -> str:
    digest = bytes(32)
    for index, event in enumerate(events):
        digest = hashlib.sha256(digest + event).digest()
        audit(index, digest.hex())
    return digest.hex()
