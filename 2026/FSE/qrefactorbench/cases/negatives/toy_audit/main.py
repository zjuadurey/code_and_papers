from program import inspect_flags


def inspect_batch(flags: list[bool]) -> tuple[bool, list[int]]:
    audit: list[int] = []
    return inspect_flags(flags, audit), audit
