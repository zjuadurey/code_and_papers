"""Source-checkout wrapper for qrefactorbench summarize."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qrefactorbench.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(["summarize", *sys.argv[1:]]))
