import tempfile
import unittest
from pathlib import Path

from tools.pandora_vault.cli import main
from tools.pandora_vault.logs import append, channel_stats, sync_event, tail


class LogsTests(unittest.TestCase):
    def test_sync_and_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = sync_event("hello vault", root=root)
            self.assertTrue(result["ok"])
            rows = tail("pandora", root=root)
            self.assertTrue(rows)
            self.assertIn("Kokomo", rows[-1]["location"])
            append("security1", "WARN", "attention", root=root)
            pandora = tail("pandora", root=root)
            self.assertTrue(any(r.get("mirrored_from") == "security1" for r in pandora))

    def test_tail_limit_and_bad_channel(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i in range(5):
                append("pandora", "INFO", f"row-{i}", root=root)
            self.assertEqual(len(tail("pandora", limit=2, root=root)), 2)
            with self.assertRaises(ValueError):
                tail("nope", root=root)

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sync_event("stats check", root=root)
            stats = channel_stats(root=root)
            self.assertTrue(stats["channels"]["pandora"]["exists"])
            self.assertGreaterEqual(stats["channels"]["pandora"]["lines"], 1)

    def test_cli_stats(self):
        self.assertEqual(main(["stats"]), 0)


if __name__ == "__main__":
    unittest.main()
