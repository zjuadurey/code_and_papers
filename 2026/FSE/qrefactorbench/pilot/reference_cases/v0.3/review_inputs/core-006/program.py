def minimum_energy(biases: list[int], couplings: list[tuple[int, int, int]]) -> int:
    best = None
    for mask in range(1 << len(biases)):
        bits = [(mask >> i) & 1 for i in range(len(biases))]
        value = sum(b * x for b, x in zip(biases, bits))
        value += sum(w * bits[i] * bits[j] for i, j, w in couplings)
        best = value if best is None else min(best, value)
    return best
