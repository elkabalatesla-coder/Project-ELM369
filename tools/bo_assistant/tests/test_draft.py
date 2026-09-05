import unittest
from tools.bo_assistant.draft import draft
class T(unittest.TestCase):
    def test_draft(self):
        r = draft("status please", channel="email", tone="government")
        self.assertFalse(r["sends"])
        self.assertIn("Subject", r["draft"])
