import unittest
from tools.elm_flux.compose import compose, generate_stub
class T(unittest.TestCase):
    def test_compose(self):
        c = compose("a bridge")
        self.assertIn("enriched_prompt", c)
        g = generate_stub(c, token_present=False)
        self.assertFalse(g["ok"])
