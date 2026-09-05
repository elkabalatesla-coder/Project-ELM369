import tempfile, unittest
from pathlib import Path
from unittest import mock
from tools.pandora_vault.logs import append, sync_event, tail

class LogsTests(unittest.TestCase):
    def test_sync_and_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("tools.pandora_vault.logs.ROOT", Path(tmp)):
                sync_event("hello vault")
                self.assertTrue(tail("pandora"))
                append("security1", "WARN", "attention")
                self.assertTrue(any(r.get("mirrored_from")=="security1" for r in tail("pandora")))
