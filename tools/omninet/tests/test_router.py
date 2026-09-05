import unittest
from tools.omninet.router import resolve
class T(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(resolve("mo*://vault/x")["ok"])
    def test_bad(self):
        self.assertFalse(resolve("http://x")["ok"])
