"""Run the browser-native engine's dependency-free Node test suite."""
import pathlib
import shutil
import subprocess
import unittest


class CoreTests(unittest.TestCase):
    def test_native_engine(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is required for browser engine tests")
        suite = pathlib.Path(__file__).with_name("core.test.mjs")
        result = subprocess.run(
            [node, "--test", str(suite)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
