import unittest

from tools.omninet.cli import main
from tools.omninet.router import namespaces, resolve, validate


class OmninetTests(unittest.TestCase):
    def test_ok(self):
        r = resolve("mo*://vault/x")
        self.assertTrue(r["ok"])
        self.assertEqual(r["namespace"], "vault")
        self.assertEqual(r["path"], "x")

    def test_roster_ns(self):
        self.assertTrue(resolve("mo*://ziggy/CASE-1")["ok"])
        self.assertTrue(resolve("mo*://hope/")["ok"])
        self.assertTrue(resolve("mo*://daily")["ok"])

    def test_bad(self):
        self.assertFalse(resolve("http://x")["ok"])
        self.assertFalse(validate("mo*://nope")["valid"])

    def test_namespaces(self):
        ns = namespaces()
        self.assertGreaterEqual(ns["count"], 10)
        self.assertIn("vault", ns["namespaces"])

    def test_cli(self):
        self.assertEqual(main(["namespaces"]), 0)


if __name__ == "__main__":
    unittest.main()
