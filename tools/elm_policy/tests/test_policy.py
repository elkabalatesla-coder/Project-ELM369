import unittest
from tools.elm_policy.geofence import location, stamp_line
class T(unittest.TestCase):
    def test_home(self):
        loc = location()
        self.assertEqual(loc["postal_code"], "46902")
        self.assertIn("Kokomo", stamp_line())
