import unittest
from tools.elm_status.report import build
class T(unittest.TestCase):
    def test_build(self):
        r = build()
        self.assertIn("sections", r)
        self.assertIn("diag", r["sections"])
