import unittest

from tools.elm_tokenizer.cli import main
from tools.elm_tokenizer.tokenize import frameworks, score_prompt, tokenize


class TokenizerTests(unittest.TestCase):
    def test_tokenize(self):
        toks = tokenize("Hello, world!")
        self.assertGreaterEqual(len(toks), 3)

    def test_score(self):
        s = score_prompt(
            "You are an engineer. Build a plan. Output JSON only. Never leak secrets. Given this context:"
        )
        self.assertGreaterEqual(s["token_count"], 5)
        self.assertIn("role", s["frameworks_present"])
        self.assertGreaterEqual(s["integration_score"], 0.45)

    def test_frameworks(self):
        f = frameworks()
        self.assertIn("role", f["frameworks"])

    def test_cli(self):
        self.assertEqual(main(["frameworks"]), 0)


if __name__ == "__main__":
    unittest.main()
