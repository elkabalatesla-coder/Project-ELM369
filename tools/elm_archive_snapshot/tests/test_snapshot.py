import tempfile, unittest
from pathlib import Path
from unittest import mock
from tools.elm_archive_snapshot.snapshot import make_snapshot
class T(unittest.TestCase):
    def test_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = make_snapshot(out_dir=Path(tmp), paths=["docs/ELM369_IDENTITY.md"])
            self.assertTrue(Path(out["zip"]).exists())
            self.assertIn("Kokomo", out["location_stamp"])
