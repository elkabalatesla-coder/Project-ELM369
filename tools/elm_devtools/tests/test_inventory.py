import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import os

from tools.elm_devtools.cli import main
from tools.elm_devtools.inventory import check_tools, list_tools


class DevtoolsTests(unittest.TestCase):
    def test_list(self):
        rows = list_tools()
        self.assertTrue(any(r["id"] == "qbit" for r in rows))
        self.assertTrue(any(r.get("registry_id") for r in rows))

    def test_check(self):
        report = check_tools()
        self.assertIn("tool_dirs", report)
        self.assertGreater(report["tool_dirs"], 5)
        self.assertIn("missing_tests", report)

    def test_cli_inventory(self):
        self.assertEqual(main(["inventory"]), 0)

    def test_list_outside_repo_root(self):
        cwd = Path.cwd()
        with TemporaryDirectory() as tmp:
            os.chdir(tmp)
            try:
                rows = list_tools()
                self.assertTrue(any(r["id"] == "qbit" for r in rows))
                self.assertTrue(any(r.get("registry_id") == "DEVTOOLS" for r in rows))
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
