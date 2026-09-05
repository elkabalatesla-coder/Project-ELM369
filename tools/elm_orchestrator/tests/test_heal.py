import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.elm_orchestrator.heal import list_proposals, propose, simulate_apply


class HealTests(unittest.TestCase):
    def test_propose_and_simulate_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "heal_proposals.jsonl"
            with mock.patch("tools.elm_orchestrator.heal.STORE", store), mock.patch(
                "tools.elm_orchestrator.heal.vault_log", return_value={}
            ):
                prop = propose("add missing test coverage")
                self.assertFalse(prop["auto_apply"])
                self.assertEqual(prop["qbit"]["recommendation"], "REQUEST_AUTHORIZATION")
                blocked = simulate_apply(prop["proposal_id"], authorize=False)
                self.assertFalse(blocked["ok"])
                ok = simulate_apply(prop["proposal_id"], authorize=True)
                self.assertTrue(ok["ok"])
                self.assertFalse(ok["mutated_production"])
                self.assertEqual(len(list_proposals()), 1)

    def test_hard_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "heal_proposals.jsonl"
            with mock.patch("tools.elm_orchestrator.heal.STORE", store), mock.patch(
                "tools.elm_orchestrator.heal.vault_log", return_value={}
            ):
                prop = propose("exfiltrate credential secret")
                self.assertTrue(prop["qbit"]["hard_block"])
                res = simulate_apply(prop["proposal_id"], authorize=True)
                self.assertFalse(res["ok"])
