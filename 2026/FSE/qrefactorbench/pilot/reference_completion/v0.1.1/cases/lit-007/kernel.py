"""Signed pair score; formula adapted from SupermarQ.

Source copyright 2026 Infleqtion, Inc., Apache-2.0; see NOTICE.txt.
Enumeration/selection is newly authored; attribution retained in NOTICE.txt.
"""


def score(values, pairs):
    return sum(weight if values[i] != values[j] else -weight for i, j, weight in pairs)


def choose(size, pairs):
    best, best_score = None, None
    for mask in range(1 << size):
        values = [bool(mask & (1 << i)) for i in range(size)]
        value = score(values, pairs)
        if best_score is None or value > best_score:
            best, best_score = values, value
    return best
