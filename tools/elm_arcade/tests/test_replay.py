import subprocess
import unittest
from pathlib import Path


class ReplayTests(unittest.TestCase):
    def test_tape(self):
        subprocess.run(
            ["node", str(Path(__file__).with_name("replay.test.mjs"))],
            check=True,
            timeout=30,
        )
