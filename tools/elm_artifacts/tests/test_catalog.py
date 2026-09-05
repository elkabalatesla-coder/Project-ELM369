import unittest
from tools.elm_artifacts.catalog import load, verify
class T(unittest.TestCase):
    def test_manifest(self):
        data = load()
        self.assertGreaterEqual(len(data.get("artifacts") or []), 10)
        self.assertTrue(verify()["ok"])
