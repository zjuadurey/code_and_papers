"""Reuse inspected wire/isolation probe with the exact new witness prompt; no inference."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import campaign as c

legacy = c.base.module("n050_retained_preflight", c.BASE / "preflight.py")


def run(folder: Path) -> dict:
    # The old implementation imports `campaign`; rebind only this private module's facade.
    # Frozen N-047 source and outputs remain unchanged.
    legacy.c = SimpleNamespace(
        locked=c.locked, verify=c.verify, transport=c.transport, ROOT=c.ROOT,
        HERE=c.BASE, save=c.save, sha=c.sha,
        ORIGINAL=folder / "frozen-inputs/02-with_witness.txt")
    return legacy.run(folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    print(json.dumps(run(parser.parse_args().campaign.resolve()), indent=2))
