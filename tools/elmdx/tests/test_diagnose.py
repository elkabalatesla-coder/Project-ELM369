import unittest
from tools.elmdx.diagnose import diagnose
class T(unittest.TestCase):
    def test_sample(self):
        r = diagnose()
        self.assertIn("findings", r)
        self.assertFalse(r["ok"])  # sample includes errors
