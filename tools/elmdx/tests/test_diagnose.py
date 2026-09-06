import json
import tempfile
import unittest
from pathlib import Path

from tools.elmdx.diagnose import diagnose, load_inventory
from tools.elmdx.cli import main


class ElmdxTests(unittest.TestCase):
    def test_sample_has_errors(self):
        r = diagnose()
        self.assertIn("findings", r)
        self.assertFalse(r["ok"])
        self.assertIn("scores", r)
        self.assertIn("device_health", r)
        self.assertGreater(r["counts"]["error"], 0)

    def test_clean_inventory_ok(self):
        inv = {
            "project_id": "ELM369_JMR08241978202646902",
            "device": {"model": "Pixel", "sdk": 34, "security_patch": "2026-08-01", "encrypted": True},
            "apps": [{"name": "com.elm", "label": "ELM", "perms": 4, "status": "ok"}],
        }
        r = diagnose(inv)
        self.assertTrue(r["ok"])
        self.assertGreaterEqual(r["scores"]["overall"], 80)

    def test_unencrypted_fails(self):
        inv = {
            "device": {"sdk": 34, "security_patch": "2026-08-01", "encrypted": False},
            "apps": [{"name": "a", "status": "ok", "perms": 1}],
        }
        r = diagnose(inv)
        self.assertFalse(r["ok"])
        self.assertIn("not_encrypted", r["device_health"]["issues"])

    def test_cli_sample(self):
        self.assertEqual(main(["sample"]), 0)

    def test_load_sample(self):
        inv = load_inventory()
        self.assertIn("apps", inv)


if __name__ == "__main__":
    unittest.main()
