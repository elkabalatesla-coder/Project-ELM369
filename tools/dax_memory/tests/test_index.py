import json
import tempfile
import unittest
from pathlib import Path

from tools.dax_memory.index import build_index, indexed_recall


class DaxIndexTests(unittest.TestCase):
    def test_index_recall(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "memories.jsonl"
            store.write_text(
                json.dumps(
                    {
                        "memory_id": "m1",
                        "content": "DAX vault connection fact",
                        "kind": "fact",
                        "tags": ["vault"],
                        "archived": False,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            stats = build_index(store)
            self.assertEqual(stats["docs"], 1)
            hits = indexed_recall("vault", store_path=store)
            self.assertTrue(hits)
            self.assertEqual(hits[0]["id"], "m1")
