def validate_jobs(jobs: list[dict], links: list[tuple[int, int, int]]) -> None:
    if any(not isinstance(job["name"], str) for job in jobs):
        raise ValueError("job names must be strings")
    if any(a < 0 or b < 0 or a >= len(jobs) or b >= len(jobs) or penalty < 0
           for a, b, penalty in links):
        raise ValueError("invalid placement link")
