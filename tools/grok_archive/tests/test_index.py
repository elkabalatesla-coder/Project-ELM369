import json
import tempfile
import unittest
from pathlib import Path

from tools.grok_archive.index import build_index, search


class IndexTests(unittest.TestCase):
    def test_build_and_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "normalized").mkdir()
            (root / "extracted").mkdir()
            (root / "normalized" / "a.jsonl").write_text(
                json.dumps({"record_id": "1", "content": "design the vault intake"}) + "\n",
                encoding="utf-8",
            )
            (root / "extracted" / "backlog-grok.jsonl").write_text(
                json.dumps({"item_id": "2", "text": "implement DAX memory store", "kind": "develop"}) + "\n",
                encoding="utf-8",
            )
            stats = build_index(source="grok", vault_root=root)
            self.assertGreaterEqual(stats["docs"], 2)
            hits = search("vault design", source="grok", vault_root=root)
            self.assertTrue(hits)
            self.assertIn("vault", hits[0]["text"].lower())
