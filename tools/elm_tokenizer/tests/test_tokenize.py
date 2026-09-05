import unittest
from tools.elm_tokenizer.tokenize import score_prompt, tokenize
class T(unittest.TestCase):
    def test_score(self):
        s = score_prompt("You are an engineer. Build a plan. Output JSON only. Never leak secrets.")
        self.assertGreaterEqual(s["token_count"], 5)
        self.assertIn("role", s["frameworks_present"])
