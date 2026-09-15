"""Analytical policies; branch descriptors never allocate a statevector."""
from dataclasses import dataclass

POLICIES = ('EAGER_FULL', 'BASIS_REWRITE', 'BASIS_THIN', 'PRODUCT_FUSED')


@dataclass(frozen=True)
class ImplicitZeroExpansion:
    old_bytes: int
    known_bits: tuple

    @property
    def active_branch(self):
        return sum(int(bit) << j for j, bit in enumerate(self.known_bits))

    @property
    def logical_bytes(self):
        return self.old_bytes << len(self.known_bits)

    @property
    def physical_bytes_at_insertion(self):
        return self.old_bytes

    def branch(self, index):
        if not 0 <= index < 1 << len(self.known_bits):
            raise IndexError(index)
        return 'EXISTING' if index == self.active_branch else 'ZERO'


def materialization_cost(policy, old_q, batch, amplitude_bytes=16):
    assert policy in POLICIES and old_q >= 0 and batch >= 0
    old = amplitude_bytes << old_q
    new = old << batch
    if not batch or policy == 'EAGER_FULL':
        return dict(read_bytes=0, write_bytes=0, insertion_read_bytes=0, insertion_write_bytes=0,
                    implicit_zero_bytes=0, standalone_expand_then_gate_bytes=0, standalone_fused_bytes=0)
    # THIN's implicit ZERO insertion is free of amplitude copies, but the first
    # mixing gate still requires a dense post-gate output in this envelope.
    return dict(read_bytes=old, write_bytes=new,
                insertion_read_bytes=old if policy == 'BASIS_REWRITE' else 0,
                insertion_write_bytes=new if policy == 'BASIS_REWRITE' else 0,
                implicit_zero_bytes=new-old if policy == 'BASIS_THIN' else 0,
                standalone_expand_then_gate_bytes=old+3*new,
                standalone_fused_bytes=old+new)
