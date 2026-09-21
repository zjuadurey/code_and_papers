import hashlib
import pytest
from program import ledger_digest


def test_digest_and_audit_order():
    seen = []
    result = ledger_digest([b"a", b"b"], lambda i, d: seen.append((i, d)))
    first = hashlib.sha256(bytes(32) + b"a").digest()
    last = hashlib.sha256(first + b"b").hexdigest()
    assert seen == [(0, first.hex()), (1, last)]
    assert result == last
    assert ledger_digest([], lambda i, d: None) == bytes(32).hex()


def test_callback_failure_propagates():
    seen = []
    def audit(index, digest):
        seen.append(index)
        raise RuntimeError("stop")
    with pytest.raises(RuntimeError, match="stop"):
        ledger_digest([b"a", b"b"], audit)
    assert seen == [0]
