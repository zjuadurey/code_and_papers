"""Byte arithmetic, with explicit endpoint overlap and chunk rounding."""
from .materialization_policy import materialization_cost


def rounded_bytes(size, chunk=1):
    assert size >= 0 and chunk > 0
    return ((int(size)+chunk-1)//chunk)*chunk if size else 0


def compose_traffic(qs, events, groups, policy, amplitude_bytes=16, chunk=1):
    backing = [amplitude_bytes << int(q) for q in qs]
    reads = sum(rounded_bytes(backing[a], chunk) for a, b in groups)
    writes = sum(rounded_bytes(backing[b], chunk) for a, b in groups)
    mat_read = mat_write = credit_read = credit_write = 0
    starts = {a+1 for a, b in groups}
    ends = {b for a, b in groups}
    for event in events:
        cost = materialization_cost(policy, event['old_q'], event['materialization_batch_size'], amplitude_bytes)
        read, write = rounded_bytes(cost['read_bytes'], chunk), rounded_bytes(cost['write_bytes'], chunk)
        mat_read += read
        mat_write += write
        if policy in {'BASIS_THIN', 'PRODUCT_FUSED'}:
            if event['gate_index'] in starts:
                credit_read += read
            if event['gate_index'] in ends:
                credit_write += write
    assert credit_read <= reads and credit_write <= writes
    total = reads+writes+mat_read+mat_write
    return dict(predicted_qdao_bytes_read=reads, predicted_qdao_bytes_written=writes,
                predicted_qdao_bytes=reads+writes, materialization_read_bytes=mat_read,
                materialization_write_bytes=mat_write, predicted_materialization_bytes=mat_read+mat_write,
                predicted_total_bytes=total, total_predicted_bytes=total,
                boundary_overlap_credit_read=credit_read, boundary_overlap_credit_write=credit_write,
                predicted_total_boundary_fused=total-credit_read-credit_write,
                predicted_total_resident_lower_bound=reads+writes if policy in {'BASIS_THIN','PRODUCT_FUSED'} else total)
