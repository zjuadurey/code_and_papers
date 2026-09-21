"""Generate corrected review inputs with the unchanged v0.1 exporter and task."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.with_name('v0.1')


def prepare(output: Path) -> None:
    """Reuse the fixed source snapshot; refuse to overwrite any output directory."""
    protected = json.loads((HERE / 'protected_before.json').read_text())
    for relative, expected in protected.items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Protected input changed: {relative}')
    spec = importlib.util.spec_from_file_location('reference_completion_v01', PREVIOUS / 'build_package.py')
    assert spec is not None and spec.loader is not None
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    exporter.HERE = HERE  # Only case source location changes; prompt/schemas/old views do not.
    exporter.prepare(output)
    path = output / 'manifest.json'
    manifest = json.loads(path.read_text())
    manifest.update(package_version='0.1.1', parent_package='pilot/reference_completion/v0.1',
                    correction_scope=['lit-005 lock-report ordering', 'lit-009 delta overflow',
                                      'lit-007 explicit algorithm cue removal'])
    path.write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', type=Path, required=True)
    prepare(parser.parse_args().prepare)
