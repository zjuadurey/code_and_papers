"""Exact region metrics and descriptive line coverage (provisional D-004)."""

from typing import Any

from . import ratio

Region = dict[str, Any]


def _key(region: Region) -> tuple[str, int, int]:
    return region["file"], region["start_line"], region["end_line"]


def _intervals(regions: list[Region]) -> dict[str, list[tuple[int, int]]]:
    merged: dict[str, list[tuple[int, int]]] = {}
    for file, start, end in sorted({_key(r) for r in regions}):
        spans = merged.setdefault(file, [])
        if spans and start <= spans[-1][1] + 1:
            spans[-1] = (spans[-1][0], max(end, spans[-1][1]))
        else:
            spans.append((start, end))
    return merged


def _length(spans: dict[str, list[tuple[int, int]]]) -> int:
    return sum(end - start + 1 for group in spans.values() for start, end in group)


def evaluate_candidates(expected: list[Region], predicted: list[Region]) -> dict[str, Any]:
    """No overlap threshold; no expansion into individual lines."""
    gold, pred = {_key(r) for r in expected}, {_key(r) for r in predicted}
    true_positives = len(gold & pred)
    g_spans, p_spans = _intervals(expected), _intervals(predicted)
    intersection = 0
    for file in g_spans.keys() & p_spans.keys():
        left, right = g_spans[file], p_spans[file]
        i = j = 0
        while i < len(left) and j < len(right):
            a, b = left[i], right[j]
            intersection += max(0, min(a[1], b[1]) - max(a[0], b[0]) + 1)
            if a[1] < b[1]:
                i += 1
            else:
                j += 1
    gold_lines, pred_lines = _length(g_spans), _length(p_spans)
    return {
        "candidate_correct": gold == pred,
        "exact": {"true_positives": true_positives, "predicted": len(pred), "reference": len(gold),
                  "precision": ratio(true_positives, len(pred)), "recall": ratio(true_positives, len(gold)),
                  "f1": ratio(2 * true_positives, len(gold) + len(pred))},
        "line_overlap": {"intersection": intersection, "predicted_lines": pred_lines,
                         "reference_lines": gold_lines, "precision": ratio(intersection, pred_lines),
                         "recall": ratio(intersection, gold_lines),
                         "iou": ratio(intersection, gold_lines + pred_lines - intersection),
                         "correctness_threshold": None},
    }

