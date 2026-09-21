from support import validate_jobs


def best_cost(jobs: list[dict], links: list[tuple[int, int, int]]) -> int:
    best = None
    for mask in range(1 << len(jobs)):
        value = sum(job["right_cost"] if mask & (1 << i) else job["left_cost"]
                    for i, job in enumerate(jobs))
        value += sum(penalty for a, b, penalty in links
                     if ((mask >> a) & 1) == ((mask >> b) & 1))
        best = value if best is None else min(best, value)
    return best


def placement_report(jobs: list[dict], links: list[tuple[int, int, int]]) -> dict:
    validate_jobs(jobs, links)
    return {"cost": best_cost(jobs, links),
            "names": [job["name"] for job in jobs], "count": len(jobs)}
