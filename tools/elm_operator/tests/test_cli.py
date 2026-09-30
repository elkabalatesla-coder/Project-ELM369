import unittest
from unittest import mock

from tools.elm_operator.cli import main
from tools.elm_operator.provenance import COMPANION_ID, PRIMARY_ID, SPINE_ID, envelope


class ProvenanceTests(unittest.TestCase):
    def test_envelope_dual_id(self):
        env = envelope({"ping": True})
        self.assertEqual(env["spine"], SPINE_ID)
        self.assertEqual(env["dual_id"]["primary"], PRIMARY_ID)
        self.assertEqual(env["dual_id"]["companion"], COMPANION_ID)
        self.assertEqual(env["location"]["postal_code"], "46902")
        self.assertEqual(env["esign"]["initials"], "IX JR")
        self.assertIn("Kokomo", env["stamp"])
        self.assertTrue(env["data"]["ping"])

    def test_envelope_without_payload(self):
        env = envelope()
        self.assertNotIn("data", env)
        self.assertEqual(env["operator"], "Joseph Michael Rose")


class CliTests(unittest.TestCase):
    def test_stamp_exits_zero(self):
        self.assertEqual(main(["stamp"]), 0)

    def test_offline_exit_1_when_no_snapshot(self):
        fake = {
            "ok": False,
            "error": "no_snapshot",
            "cannot_control": ["telephony", "radio", "satellite", "hotspot"],
            "file_count": 0,
            "bytes": 0,
        }
        with mock.patch("tools.elm_offline.engine.status", return_value=fake):
            self.assertEqual(main(["offline"]), 1)

    def test_offline_exit_0_when_snapshot_ok(self):
        fake = {
            "ok": True,
            "file_count": 3,
            "bytes": 100,
            "cannot_control": ["telephony"],
        }
        with mock.patch("tools.elm_offline.engine.status", return_value=fake):
            self.assertEqual(main(["offline"]), 0)

    def test_roster_exits_zero(self):
        with mock.patch(
            "tools.elm_dashboard.roster.roster_lanes", return_value=[{"lane": "dev"}]
        ):
            self.assertEqual(main(["roster"]), 0)

    def test_status_exit_follows_report_ok(self):
        with mock.patch("tools.elm_status.report.build", return_value={"ok": True, "sections": {}}):
            self.assertEqual(main(["status"]), 0)
        with mock.patch("tools.elm_status.report.build", return_value={"ok": False, "sections": {}}):
            self.assertEqual(main(["status"]), 1)

    def test_daily_dry_run_exit_follows_report(self):
        class _R:
            def __init__(self, ok: bool):
                self.ok = ok
                self.dry_run = True
                self.project_id = "ELM369"
                self.started_at = "t0"
                self.finished_at = "t1"
                self.results = []

        with mock.patch(
            "tools.elm_daily_automation.runner.run_daily", return_value=_R(True)
        ):
            self.assertEqual(main(["daily-dry-run"]), 0)
        with mock.patch(
            "tools.elm_daily_automation.runner.run_daily", return_value=_R(False)
        ):
            self.assertEqual(main(["daily-dry-run"]), 1)


if __name__ == "__main__":
    unittest.main()
