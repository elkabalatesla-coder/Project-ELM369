import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.elm_evolution.engine import advance, discover, propose


class EvolutionTests(unittest.TestCase):
    def test_discover(self):
        result = discover(Path("."))
        self.assertIn("findings", result)

    def test_propose_and_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "changes.jsonl"
            with mock.patch("tools.elm_evolution.engine.STORE", store):
                ch = propose("add unit test for vault status", operation="correct")
                self.assertEqual(ch["lifecycle"], "PROPOSED")
                self.assertFalse(ch["auto_deploy"])
                # advance freely through early stages
                r = advance(ch["change_id"])
                self.assertTrue(r["ok"])
                self.assertEqual(r["change"]["lifecycle"], "SANDBOX")
                r = advance(ch["change_id"])
                self.assertTrue(r["ok"])
                self.assertEqual(r["change"]["lifecycle"], "TESTING")
                r = advance(ch["change_id"])
                self.assertTrue(r["ok"])
                self.assertEqual(r["change"]["lifecycle"], "VALIDATING")
                # gated
                blocked = advance(ch["change_id"])
                self.assertFalse(blocked["ok"])
                ok = advance(ch["change_id"], authorize=True)
                self.assertTrue(ok["ok"])
                self.assertFalse(ok["change"]["production_mutation"])

    def test_hard_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "changes.jsonl"
            with mock.patch("tools.elm_evolution.engine.STORE", store):
                ch = propose("change production credential secret", operation="fix")
                self.assertTrue(ch["qbit"]["hard_block"])
                r = advance(ch["change_id"])
                self.assertFalse(r["ok"])
                self.assertEqual(r["change"]["lifecycle"], "QUARANTINED")


if __name__ == "__main__":
    unittest.main()
