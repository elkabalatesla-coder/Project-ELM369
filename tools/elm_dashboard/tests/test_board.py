import tempfile
import unittest
from pathlib import Path

from tools.elm_dashboard.board import build
from tools.elm_dashboard.cases import summarize_case_queue
from tools.elm_dashboard.cli import main
from tools.elm_dashboard.roster import roster_lanes


class BoardTests(unittest.TestCase):
    def test_roster_lanes(self):
        lanes = roster_lanes()
        names = {r["bot"] for r in lanes}
        self.assertIn("Ziggy", names)
        self.assertIn("Hope", names)
        self.assertIn("White Rook", names)
        self.assertEqual(len(lanes), 8)

    def test_build_includes_roster_and_rules(self):
        board = build(include_cases=False)
        self.assertIn("roster_lanes", board)
        self.assertEqual(board["vault_ids"]["primary"], "JMR08241978202646902")
        self.assertTrue(board["hard_rules"]["filing_joseph_gated"])
        self.assertIn("Kokomo", board["esign"])

    def test_case_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "note.md").write_text("Opened CASE-20260906-001 for intake.\n", encoding="utf-8")
            summary = summarize_case_queue(root)
            self.assertEqual(summary["open_count"], 1)
            self.assertEqual(summary["cases"][0]["id"], "CASE-20260906-001")

    def test_cli_roster(self):
        self.assertEqual(main(["roster"]), 0)


if __name__ == "__main__":
    unittest.main()
