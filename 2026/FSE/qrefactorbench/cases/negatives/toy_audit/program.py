def inspect_flags(flags: list[bool], audit: list[int]) -> bool:
    found = False
    for index, flag in enumerate(flags):
        audit.append(index)
        found = found or flag
    return found
