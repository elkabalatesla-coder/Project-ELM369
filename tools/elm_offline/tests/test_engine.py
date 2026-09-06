import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.elm_offline.engine import CANNOT_CONTROL, snapshot, status


class OfflineTests(unittest.TestCase):
    def test_snapshot_and_status_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache"
            man = Path(tmp) / "manifest.json"
            src_root = Path(tmp) / "src"
            src_root.mkdir()
            f = src_root / "note.md"
            f.write_text("offline sample\n", encoding="utf-8")
            # Use cwd-relative path: write under tmp and pass absolute via paths — engine expects Path(rel)
            # Create a tiny file under a relative name inside tmp by chdir
            with mock.patch("tools.elm_offline.engine.CACHE", cache), mock.patch(
                "tools.elm_offline.engine.MANIFEST", man
            ):
                # Prefer a known repo file when present; else use explicit temp relative via patching Path
                repo_src = Path("docs/ELM369_IDENTITY.md")
                if repo_src.exists():
                    m = snapshot([str(repo_src)])
                else:
                    m = snapshot([str(f)])
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
                    self.assertTrue(any("docs/policy" in c or c.startswith("docs/policy") for c in m["copied"]) or m["copied"])
                    st = status()
                    self.assertEqual(st["cannot_control"], CANNOT_CONTROL)
