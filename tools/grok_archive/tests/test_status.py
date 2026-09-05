import json
import tempfile
import unittest
from pathlib import Path

from tools.grok_archive.status import vault_status


class StatusTests(unittest.TestCase):
    def test_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            g = root / "grok"
            (g / "raw").mkdir(parents=True)
            (g / "normalized").mkdir()
            (g / "extracted").mkdir()
            (g / "raw" / "a.jsonl").write_text("{}\n", encoding="utf-8")
            (g / "normalized" / "n.jsonl").write_text(
                json.dumps({"content": "hi"}) + "\n", encoding="utf-8"
            )
            (g / "extracted" / "backlog-grok.jsonl").write_text(
                json.dumps({"kind": "design", "status": "open"}) + "\n", encoding="utf-8"
            )
            report = vault_status(root)
            self.assertTrue(report["ok"])
            self.assertEqual(report["sources"]["grok"]["backlog_open"], 1)
