import unittest

from tools.elm_tokenizer.cli import main
from tools.elm_tokenizer.tokenize import (
    frameworks,
    resolve_priority_phrase,
    score_prompt,
    tokenize,
)


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

    def test_phrase_priority_resolves_before_scoring(self):
        resolution = resolve_priority_phrase("idn gun a fuk")
        self.assertEqual(resolution["resolved"], "I don't give a fuck")
        self.assertEqual(resolution["family"], "IDGAF")
        self.assertTrue(resolution["matched"])

    def test_phrase_priority_cli_scores_resolved_phrase(self):
        from contextlib import redirect_stdout
        from io import StringIO
        import json

        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                main(["score", "--phrase-priority", "idn gun a fuk"]),
                0,
            )
        result = json.loads(output.getvalue())
        self.assertEqual(
            result["phrase_priority"]["resolved"],
            "I don't give a fuck",
        )
        self.assertEqual(result["token_count"], len(tokenize("I don't give a fuck")))
        self.assertEqual(
            result["tokens_preview"],
            tokenize("I don't give a fuck"),
        )

    def test_unknown_priority_phrase_is_scored_unchanged(self):
        resolution = resolve_priority_phrase("unlisted phrase")
        self.assertFalse(resolution["matched"])
        self.assertEqual(resolution["resolved"], "unlisted phrase")


if __name__ == "__main__":
    unittest.main()
