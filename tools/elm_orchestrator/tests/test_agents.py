import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.elm_orchestrator.agents import diagnose, heal_propose, vault_log
from tools.elm_orchestrator.cli import main


class OrchestratorTests(unittest.TestCase):
    def test_diagnose_on_repo(self):
        # When run from repo root in CI/clone, should be mostly ok
        result = diagnose(Path("."))
        self.assertIn("checks", result)

    def test_vault_log_and_heal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("tools.elm_orchestrator.agents.LOG_DIR", Path(tmp)):
                row = vault_log("test_event", {"x": 1})
                self.assertEqual(row["event"], "test_event")
                prop = heal_propose("missing coverage")
                self.assertFalse(prop["auto_apply"])

    def test_cli_diag(self):
        # may return 1 if missing pieces in sparse checkout; just ensure no crash
        rc = main(["diag"])
        self.assertIn(rc, (0, 1))


if __name__ == "__main__":
    unittest.main()
