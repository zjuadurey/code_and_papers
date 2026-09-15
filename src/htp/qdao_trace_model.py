from .qdao_model import partition


def partition_trace(operands, n, m=16, t=2):
    if n <= m:
        return ([(0, len(operands))] if operands else []), 'whole_circuit_in_memory_extension'
    return partition(operands, m, t), 'qdao_static_partitioner'
