import unittest
from unittest.mock import patch

from tools.elm_status.report import build
class T(unittest.TestCase):
    def test_build(self):
        r = build()
        self.assertIn("sections", r)
        self.assertIn("diag", r["sections"])

    def test_build_security_fallback(self):
        with patch("tools.elm_status.report._security_posture", side_effect=RuntimeError("boom")):
            report = build()
        self.assertFalse(report["ok"])
        self.assertEqual(report["sections"]["security"]["ok"], False)
        self.assertEqual(report["sections"]["security"]["error"], "boom")
