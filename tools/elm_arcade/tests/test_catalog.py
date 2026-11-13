import shutil
import subprocess
import unittest
from pathlib import Path


class CatalogTests(unittest.TestCase):
    def test_catalog(self):
        self.assertIsNotNone(shutil.which("node"), "Node.js 22 is required for arcade tests")
        subprocess.run(
            ["node", str(Path(__file__).with_name("catalog.test.mjs"))],
            check=True,
            timeout=30,
        )
