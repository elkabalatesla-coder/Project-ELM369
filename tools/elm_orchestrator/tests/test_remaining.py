import unittest
from unittest import mock

from tools.elm_orchestrator.esign import watermark
from tools.elm_orchestrator.optimizer import suggest
from tools.elm_orchestrator.time_sync import query_ntp, sync_report


class RemainingDesignTests(unittest.TestCase):
    def test_watermark(self):
        env = watermark({"hello": "world"})
        self.assertEqual(len(env["payload_sha256"]), 64)
        self.assertIn("disclaimer", env)

    def test_optimizer(self):
        out = suggest("jsonl recall search")
        self.assertTrue(out["suggestions"])
        self.assertTrue(any("index" in s.lower() for s in out["suggestions"]))

    def test_ntp_soft_fail(self):
        with mock.patch("tools.elm_orchestrator.time_sync.socket.socket") as sock_cls:
            sock_cls.side_effect = OSError("blocked")
            r = query_ntp("example.invalid")
            self.assertEqual(r["status"], "error")
        # sync_report should still return structure
        with mock.patch("tools.elm_orchestrator.time_sync.query_ntp", return_value={"status": "error", "host": "x", "error": "e"}):
            report = sync_report()
            self.assertIn("results", report)


if __name__ == "__main__":
    unittest.main()
