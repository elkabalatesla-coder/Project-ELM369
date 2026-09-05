import unittest
from tools.elm_progress.engine import summarize, verify_paths
class T(unittest.TestCase):
    def test_summary(self):
        s = summarize()
        self.assertGreater(s["tool_count"], 5)
    def test_verify(self):
        v = verify_paths()
        self.assertIn("present", v)
