"""Conservative peak-file budget for the fixed-t end-to-end scale extension."""


def scaling_capacity_bytes(n, block_bytes=4096):
    if n not in (26, 28) or not 0 < block_bytes <= 4096:
        raise ValueError('Budget audited only for 26/28q, t=12, <=4 KiB filesystem blocks')
    # QDAO/GBSA overwrite one bank. QThin has source+destination only when growing,
    # with old <= new/2; 2B is a deliberately looser bound than 1.5B.
    # Every bank has <=2^(n-t) files: one for each materialized high logical wire
    # assignment. NPY headers (128 bytes) cost <=one extra filesystem block/file.
    # Two banks at 28q add <=512 MiB in rounding; another >=512 MiB is reserved
    # for directories/inodes/journal metadata. This does not assume VHDX shrinkage.
    return 2 * (16 << n) + (1 << 30)
