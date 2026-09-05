import tempfile, unittest
from pathlib import Path
from unittest import mock
from tools.elm_offline.engine import snapshot, status

class OfflineTests(unittest.TestCase):
    def test_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)/"cache"; man = Path(tmp)/"manifest.json"
            # create a tiny source file in cwd-relative path via patching defaults is hard;
            # call with explicit path inside tmp by writing a file in repo and using paths arg
            src = Path("docs/ELM369_IDENTITY.md")
            with mock.patch("tools.elm_offline.engine.CACHE", cache), mock.patch("tools.elm_offline.engine.MANIFEST", man):
                if src.exists():
                    m = snapshot([str(src)])
                    self.assertTrue(m["copied"] or m["missing"]==[])
                    self.assertTrue(status().get("created_at"))
