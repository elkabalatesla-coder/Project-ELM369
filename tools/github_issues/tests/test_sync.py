import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.github_issues.sync import write_raw


class SyncTests(unittest.TestCase):
    def test_write_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_raw(
                [
                    {
                        "number": 1,
                        "title": "design the vault",
                        "body": "We should implement shorthand save.",
                        "html_url": "https://example.com/1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "updated_at": "2026-01-01T00:00:00Z",
                        "labels": [{"name": "enhancement"}],
                    }
                ],
                raw_dir=Path(tmp),
            )
            self.assertTrue(path.exists())
            row = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(row["issue_number"], 1)
            self.assertIn("design the vault", row["message"])
