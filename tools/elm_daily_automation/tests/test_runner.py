import json
import tempfile
import unittest
from pathlib import Path

from tools.elm_daily_automation.cli import main
from tools.elm_daily_automation.runner import run_daily


class DailyAutomationTests(unittest.TestCase):
    def test_run_with_stub_outage(self):
        def stub():
            return {"status": "ok", "detail": "stubbed"}

        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "daily_runs.jsonl"
            report = run_daily(dry_run=True, outage_runner=stub, log_path=log)
            self.assertTrue(report.ok)
            self.assertTrue(log.exists())
            row = json.loads(log.read_text(encoding="utf-8").strip().splitlines()[-1])
            self.assertTrue(row["ok"])
            kinds = {r["task_id"] for r in row["results"]}
            self.assertIn("outage_probe", kinds)
            self.assertIn("repo_hygiene", kinds)

    def test_attention_when_outage_bad(self):
        def stub():
            return {"status": "attention", "detail": "1 down"}

        with tempfile.TemporaryDirectory() as tmp:
            report = run_daily(
                dry_run=True,
                outage_runner=stub,
                log_path=Path(tmp) / "daily_runs.jsonl",
            )
            self.assertFalse(report.ok)

    def test_cli_dry_run(self):
        self.assertEqual(main(["run", "--dry-run"]), 0)


if __name__ == "__main__":
    unittest.main()


class VaultBacklogTaskTests(unittest.TestCase):
    def test_vault_backlog_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "sources" / "grok" / "extracted"
            root.mkdir(parents=True)
            (root / "backlog-grok.jsonl").write_text(
                json.dumps({"kind": "design", "text": "x", "status": "open"}) + "\n"
                + json.dumps({"kind": "develop", "text": "y", "status": "done"}) + "\n",
                encoding="utf-8",
            )
            cfg = {
                "project_id": "t",
                "tasks": [
                    {
                        "id": "vault_backlog",
                        "name": "Vault backlog",
                        "kind": "vault_backlog",
                        "enabled": True,
                        "sources_root": str(Path(tmp) / "sources"),
                    }
                ],
            }
            report = run_daily(cfg, dry_run=True, log_path=Path(tmp) / "log.jsonl")
            self.assertEqual(report.results[0].status, "ok")
            self.assertIn("1 open", report.results[0].detail)
