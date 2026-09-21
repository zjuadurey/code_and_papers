"""Build pair evidence and independently described release groups."""

# Adapted source portions: C2|Q> Dataset, CC BY 4.0; see supplied NOTICE.txt.


def relation(names: list[str], latest: dict[frozenset[str], bool]) -> list[list[bool]]:
    return [[i != j and latest.get(frozenset((left, right))) is True for j, right in enumerate(names)]
            for i, left in enumerate(names)]


def compatible(indices: list[int], matrix: list[list[bool]]) -> bool:
    return all(matrix[u][v] for u in indices for v in indices if u != v)


def preview(matrix: list[list[bool]]) -> list[int]:
    selected = []
    for node in range(len(matrix)):
        if all(matrix[node][neighbor] for neighbor in selected):
            selected.append(node)
    return selected


def describe(versions: list[dict], selected: list[str], latest: dict[frozenset[str], bool]) -> dict:
    ordered = [v["version_id"] for v in versions if v["version_id"] in selected]
    inactive = [v["version_id"] for v in versions if v["version_id"] in selected and not v["active"]]
    missing = []
    for i, left in enumerate(ordered):
        for right in ordered[i + 1:]:
            outcome = latest.get(frozenset((left, right)))
            if outcome is not True:
                missing.append({"left": left, "right": right, "reason": "failed" if outcome is False else "unverified"})
    return {"selected": ordered, "size": len(ordered), "inactive": inactive, "missing_pairs": missing,
            "eligible_and_compatible": not inactive and not missing}
