def has_code(codes: list[int], target: int) -> bool:
    if len(codes) > 8:
        raise ValueError("at most eight codes")
    for code in codes:
        if code == target:
            return True
    return False
