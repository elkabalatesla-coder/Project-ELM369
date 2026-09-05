import json
import tempfile
import unittest
from pathlib import Path

from tools.grok_archive.cli import main
from tools.grok_archive.ingest import ingest_path
from tools.grok_archive.normalize import extract_backlog, normalize_record


class GrokArchiveTests(unittest.TestCase):
    def test_normalize_jsonl_message(self):
        rows = normalize_record(
            {"sender": "user", "message": "design the vault"},
            source="grok",
            origin="t.jsonl",
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["role"], "user")

    def test_ingest_and_backlog(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw"
            raw.mkdir()
            (raw / "c.jsonl").write_text(
                json.dumps(
                    {
                        "sender": "user",
                        "message": "We should implement the DAX memory store and design the schema.",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            vault = Path(tmp) / "vaultsrc"
            stats = ingest_path(raw, source="grok", vault_root=vault)
            self.assertGreaterEqual(stats["messages"], 1)
            self.assertGreaterEqual(stats["backlog_items"], 1)
            backlog_path = Path(stats["backlog"])
            items = [json.loads(l) for l in backlog_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertTrue(any(i["kind"] in {"design", "develop"} for i in items))

    def test_cli_help_path(self):
        # list with empty vault should still exit 0
        self.assertEqual(main(["list", "--source", "grok"]), 0)


if __name__ == "__main__":
    unittest.main()
