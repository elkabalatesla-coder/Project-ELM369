import tempfile
import unittest
from pathlib import Path

from tools.dax_memory import store as mem
from tools.dax_memory.cli import main


class DaxMemoryTests(unittest.TestCase):
    def test_store_recall_organize(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memories.jsonl"
            a = mem.store("DAX holds portable AI state", kind="fact", tags=["dax"], path=path)
            mem.store("DAX holds portable AI state", kind="fact", tags=["dax"], path=path)
            mem.store("connection to quantum memory", kind="connection", path=path)
            hits = mem.recall("portable", path=path)
            self.assertTrue(hits)
            self.assertEqual(hits[0].memory_id, a.memory_id)
            stats = mem.organize(path=path)
            self.assertEqual(stats["after"], 2)
            self.assertEqual(stats["removed"], 1)

    def test_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memories.jsonl"
            e = mem.store("temporary note", path=path)
            archived = mem.archive(e.memory_id, path=path)
            self.assertIsNotNone(archived)
            self.assertTrue(archived.archived)
            self.assertEqual(mem.list_entries(path=path), [])
            self.assertEqual(len(mem.list_entries(path=path, include_archived=True)), 1)

    def test_cli_store_list(self):
        # Uses default store path under package data; fine for smoke in CI temp workspace
        self.assertEqual(main(["store", "hello from test", "--kind", "note", "--tag", "test"]), 0)


if __name__ == "__main__":
    unittest.main()
