"""Exercise dependency isolation, tamper detection, and rejected unsafe inputs."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "parallel_snapshot.py"
SPEC = importlib.util.spec_from_file_location("parallel_snapshot", SCRIPT)
snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(snapshot)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "module.py").write_text("VERSION = 1\n")
        self.destination = self.root / "frozen-v1"

    def tearDown(self):
        for path in self.root.rglob("*"):
            if not path.is_symlink():
                path.chmod(0o700 if path.is_dir() else 0o600)
        self.tmp.cleanup()

    def test_producer_edits_do_not_change_consumer_copy(self):
        snapshot.create(self.source, self.destination)
        frozen = self.destination / "files/module.py"
        self.assertNotEqual(frozen.stat().st_ino, (self.source / "module.py").stat().st_ino)
        (self.source / "module.py").write_text("VERSION = 2\n")
        self.assertEqual(frozen.read_text(), "VERSION = 1\n")
        self.assertFalse(frozen.stat().st_mode & 0o222)
        snapshot.verify(self.destination)

    def test_existing_version_cannot_be_overwritten(self):
        snapshot.create(self.source, self.destination)
        with self.assertRaises(FileExistsError):
            snapshot.create(self.source, self.destination)

    def test_tampering_is_detected(self):
        snapshot.create(self.source, self.destination)
        frozen = self.destination / "files/module.py"
        frozen.chmod(0o600)
        frozen.write_text("VERSION = 99\n")
        with self.assertRaises(ValueError):
            snapshot.verify(self.destination)

    def test_extra_files_are_detected(self):
        snapshot.create(self.source, self.destination)
        data = self.destination / "files"
        data.chmod(0o700)
        (data / "injected.py").write_text("pass\n")
        with self.assertRaises(ValueError):
            snapshot.verify(self.destination)

    def test_external_symlinks_are_rejected(self):
        (self.source / "live_dependency").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            snapshot.create(self.source, self.destination)
        self.assertFalse(self.destination.exists())

    def test_metadata_and_cache_are_excluded(self):
        for name in (".git", "__pycache__", ".codex"):
            (self.source / name).mkdir()
            (self.source / name / "private").write_text("not part of input")
        manifest = snapshot.create(self.source, self.destination)
        self.assertEqual(set(manifest["files"]), {"module.py"})

    def test_nested_destination_is_rejected(self):
        with self.assertRaises(ValueError):
            snapshot.create(self.source, self.source / "recursive")

    def test_missing_data_directory_is_rejected(self):
        self.destination.mkdir()
        (self.destination / "manifest.json").write_text('{"format":1,"files":{}}')
        with self.assertRaises(ValueError):
            snapshot.verify(self.destination)


if __name__ == "__main__":
    unittest.main()
