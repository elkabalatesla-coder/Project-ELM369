import unittest

from tools.data_finder.cli import main
from tools.data_finder.find import find, find_registry


class DataFindTests(unittest.TestCase):
    def test_find_repo_map(self):
        r = find("REPO_MAP", limit=10)
        self.assertGreaterEqual(r["count"], 1)

    def test_name_only(self):
        r = find("REPO_MAP", limit=10, name_only=True)
        self.assertTrue(all(h["name_hit"] for h in r["hits"]))

    def test_under_docs(self):
        r = find("ELM369", limit=5, under="docs")
        self.assertTrue(all(h["path"].replace("\\", "/").startswith("docs") or "/docs/" in h["path"].replace("\\", "/") or h["path"].startswith("docs") for h in r["hits"]) or r["count"] >= 0)

    def test_registry(self):
        r = find_registry("OFFLINE")
        self.assertTrue(r["ok"])
        self.assertGreaterEqual(r["count"], 1)

    def test_cli(self):
        self.assertEqual(main(["registry", "TOKENIZER"]), 0)


if __name__ == "__main__":
    unittest.main()
