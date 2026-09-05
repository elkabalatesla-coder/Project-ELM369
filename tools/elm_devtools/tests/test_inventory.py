import unittest
from tools.elm_devtools.inventory import list_tools
class T(unittest.TestCase):
    def test_list(self):
        rows = list_tools()
        self.assertTrue(any(r["id"]=="qbit" for r in rows))
