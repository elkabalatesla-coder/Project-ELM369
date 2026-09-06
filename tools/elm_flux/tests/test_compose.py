import unittest

from tools.elm_flux.cli import main
from tools.elm_flux.compose import compose, generate_stub, list_styles


class FluxTests(unittest.TestCase):
    def test_compose(self):
        c = compose("a bridge", style="noir", aspect="16:9")
        self.assertIn("enriched_prompt", c)
        self.assertEqual(c["style"], "noir")
        self.assertEqual(c["aspect"], "16:9")
        self.assertFalse(c["live_api"])
        self.assertFalse(c["generate"])

    def test_generate_stub_no_token(self):
        c = compose("a bridge")
        g = generate_stub(c, token_present=False)
        self.assertFalse(g["ok"])
        self.assertEqual(g["error"], "missing_token")

    def test_generate_stub_with_token_still_refuses(self):
        c = compose("a bridge")
        g = generate_stub(c, token_present=True)
        self.assertFalse(g["ok"])
        self.assertEqual(g["error"], "generator_not_wired")
        self.assertFalse(g["live_api"])

    def test_styles(self):
        s = list_styles()
        self.assertIn("cyberpunk", s["styles"])
        self.assertIn("1:1", s["aspects"])

    def test_cli_styles(self):
        self.assertEqual(main(["styles"]), 0)


if __name__ == "__main__":
    unittest.main()
