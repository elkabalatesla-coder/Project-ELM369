import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.elm_offline.engine import CANNOT_CONTROL, list_cached, snapshot, status, verify


class OfflineTests(unittest.TestCase):
    def test_snapshot_and_status_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache"
            man = Path(tmp) / "manifest.json"
            with mock.patch("tools.elm_offline.engine.CACHE", cache), mock.patch(
                "tools.elm_offline.engine.MANIFEST", man
            ):
                repo_src = Path("docs/ELM369_IDENTITY.md")
                m = snapshot([str(repo_src)])
                self.assertIn("copied", m)
                self.assertEqual(m["cannot_control"], CANNOT_CONTROL)
                st = status()
                self.assertTrue(st.get("ok"))
                self.assertIn("created_at", st)
                self.assertIn("file_count", st)
                self.assertIn("bytes", st)
                self.assertIsNotNone(st.get("snapshot_age_seconds"))
                self.assertEqual(st["cannot_control"], ["telephony", "radio", "satellite", "hotspot"])
                self.assertGreaterEqual(st["file_count"], 1)
                self.assertGreaterEqual(st["bytes"], 1)
                listed = list_cached()
                self.assertGreaterEqual(listed["count"], 1)
                v = verify()
                self.assertTrue(v.get("ok"))

    def test_status_no_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache"
            man = Path(tmp) / "manifest.json"
            with mock.patch("tools.elm_offline.engine.CACHE", cache), mock.patch(
                "tools.elm_offline.engine.MANIFEST", man
            ):
                st = status()
                self.assertFalse(st["ok"])
                self.assertEqual(st["error"], "no_snapshot")
                self.assertEqual(st["cannot_control"], CANNOT_CONTROL)

    def test_snapshot_includes_expanded_defaults_keys(self):
        from tools.elm_offline.engine import DEFAULT_SNAPSHOT_PATHS

        self.assertIn("docs/STATUS.md", DEFAULT_SNAPSHOT_PATHS)
        self.assertIn("docs/BACKLOG.md", DEFAULT_SNAPSHOT_PATHS)
        self.assertIn("docs/policy", DEFAULT_SNAPSHOT_PATHS)
        self.assertIn("artifacts/sandboxes/manifest.json", DEFAULT_SNAPSHOT_PATHS)
        self.assertIn("docs/ELM369_COMPLETION_CERTIFICATE.json", DEFAULT_SNAPSHOT_PATHS)
        self.assertIn("docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md", DEFAULT_SNAPSHOT_PATHS)

    def test_snapshot_copies_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache"
            man = Path(tmp) / "manifest.json"
            policy = Path("docs/policy")
            with mock.patch("tools.elm_offline.engine.CACHE", cache), mock.patch(
                "tools.elm_offline.engine.MANIFEST", man
            ):
                if policy.is_dir():
                    m = snapshot(["docs/policy"])
                    self.assertTrue(
                        any("docs/policy" in c or c.startswith("docs/policy") for c in m["copied"])
                        or m["copied"]
                    )
                    st = status()
                    self.assertEqual(st["cannot_control"], CANNOT_CONTROL)


if __name__ == "__main__":
    unittest.main()
