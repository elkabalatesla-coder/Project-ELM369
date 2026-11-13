"""Run the native arcade math and headless lifecycle contract tests."""
from pathlib import Path
import shutil
import subprocess
import unittest


class ArcadeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js is required for ES module tests")
    def test_native_arcade_suite(self):
        suite = Path(__file__).with_name("arcade.test.mjs")
        result = subprocess.run(
            ["node", "--test", str(suite)],
            cwd=suite.parent.parent,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
