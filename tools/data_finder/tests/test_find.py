import unittest
from tools.data_finder.find import find
class T(unittest.TestCase):
    def test_find_repo_map(self):
        r = find("REPO_MAP", limit=10)
        self.assertGreaterEqual(r["count"], 1)
