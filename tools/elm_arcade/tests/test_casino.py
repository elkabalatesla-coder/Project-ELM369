"""Run the native browser/Node casino integration suite without Python dependencies."""

import pathlib
import shutil
import subprocess
import unittest


class CasinoIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js is required for native casino tests")
    def test_native_casino_integration(self):
        arcade_root = pathlib.Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["node", "--test", "tests/casino.test.mjs"],
            cwd=arcade_root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
