"""Run dependency-free browser casino-math tests with Node's native assertions."""
import pathlib
import shutil
import subprocess
import unittest


class CasinoMathTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js is required for ES module math tests")
    def test_math_modules(self):
        script = pathlib.Path(__file__).with_name("math.test.mjs")
        result = subprocess.run(
            ["node", str(script)],
            cwd=script.parent,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Casino math:", result.stdout)


if __name__ == "__main__":
    unittest.main()
