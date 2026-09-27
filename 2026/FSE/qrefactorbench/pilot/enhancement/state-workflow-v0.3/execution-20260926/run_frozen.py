"""Select the already-installed, approved CLI binary; retain frozen runner/config."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import campaign

campaign.transport.CODEX = Path(
    "/home/audrey/.codex/packages/standalone/releases/0.156.1-x86_64-unknown-linux-musl/bin/codex"
)

if __name__ == "__main__":
    campaign.main()
