import unittest

from tools.ai_outage_monitor.classify import classify_http, classify_statuspage_v2


class ClassifyTests(unittest.TestCase):
    def test_http_ok(self):
        self.assertEqual(classify_http(200), "ok")

    def test_http_degraded(self):
        self.assertEqual(classify_http(429), "degraded")
        self.assertEqual(classify_http(404), "degraded")

    def test_http_down(self):
        self.assertEqual(classify_http(503), "degraded")
        self.assertEqual(classify_http(500), "down")

    def test_http_timeout(self):
        self.assertEqual(classify_http(None, "timed out"), "down")

    def test_statuspage_indicators(self):
        self.assertEqual(
            classify_statuspage_v2({"status": {"indicator": "none"}}, 200), "ok"
        )
        self.assertEqual(
            classify_statuspage_v2({"status": {"indicator": "minor"}}, 200), "degraded"
        )
        self.assertEqual(
            classify_statuspage_v2({"status": {"indicator": "major"}}, 200), "down"
        )


if __name__ == "__main__":
    unittest.main()
