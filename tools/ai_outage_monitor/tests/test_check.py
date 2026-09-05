import json
import tempfile
import unittest
from pathlib import Path

from tools.ai_outage_monitor.check import run_checks
from tools.ai_outage_monitor.cli import main


class CheckTests(unittest.TestCase):
    def test_dry_run(self):
        results = run_checks(dry_run=True)
        self.assertTrue(results)
        self.assertTrue(all(r.status == "ok" for r in results))

    def test_mocked_fetch_writes_jsonl(self):
        def fake_fetch(url: str, timeout: float):
            payload = json.dumps(
                {"status": {"indicator": "none", "description": "All Systems Operational"}}
            )
            return 200, payload, None

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "outages.jsonl"
            results = run_checks(dry_run=False, fetch=fake_fetch, data_path=path)
            self.assertTrue(results)
            self.assertTrue(path.exists())
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), len(results))
            row = json.loads(lines[0])
            self.assertIn(row["status"], {"ok", "degraded", "down", "unknown"})

    def test_cli_dry_run(self):
        self.assertEqual(main(["check", "--dry-run"]), 0)


if __name__ == "__main__":
    unittest.main()
