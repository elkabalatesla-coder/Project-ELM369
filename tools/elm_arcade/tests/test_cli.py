import http.client
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer

from tools.elm_arcade.cli import ArcadeHandler, ROOT, main


class ArcadeCLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(ArcadeHandler, directory=str(ROOT))
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_launcher_and_security_headers(self):
        status, headers, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn(b"no monetary value", body)
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("object-src 'none'", headers["Content-Security-Policy"])

    def test_catalog_and_module_mime(self):
        status, _, body = self.request("/catalog.json")
        self.assertEqual(status, 200)
        self.assertIn(b'"schemaVersion": 1', body)
        self.assertEqual(
            ArcadeHandler.extensions_map[".mjs"], "text/javascript"
        )

    def test_no_repository_or_directory_listing(self):
        self.assertEqual(self.request("/../README.md")[0], 404)
        self.assertEqual(self.request("/tests/")[0], 403)

    def test_invalid_port(self):
        with self.assertRaises(SystemExit):
            main(["--port", "-1"])
