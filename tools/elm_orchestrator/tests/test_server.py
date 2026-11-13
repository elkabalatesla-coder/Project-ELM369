import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest import mock

from tools.elm_orchestrator.server import Handler, MAX_REQUEST_BYTES


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, body, headers=None):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request("POST", path, body=body, headers=headers or {})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_rejects_malformed_or_non_object_json(self):
        for body in (b"{", b"[]", b"null", b'"text"', b"\xff", b"[" * 2000):
            with self.subTest(body=body):
                status, result = self.request("/v1/heal", body)
                self.assertEqual(status, 400)
                self.assertEqual(result["error"], "invalid JSON request")

    def test_rejects_invalid_body_framing(self):
        for headers, expected in (
            ({"Content-Length": "-1"}, 400),
            ({"Content-Length": "invalid"}, 400),
            ({"Content-Length": str(MAX_REQUEST_BYTES + 1)}, 413),
            ({"Transfer-Encoding": "chunked"}, 400),
        ):
            with self.subTest(headers=headers):
                status, _ = self.request("/v1/heal", b"", headers)
                self.assertEqual(status, expected)

    def test_simulation_requires_boolean_authorization(self):
        with mock.patch("tools.elm_orchestrator.server.simulate_apply", return_value={"ok": True}) as apply:
            for value in ("false", "true", 1, [], None):
                with self.subTest(value=value):
                    status, _ = self.request(
                        "/v1/heal/simulate",
                        json.dumps({"proposal_id": "test", "authorize": value}),
                    )
                    self.assertEqual(status, 400)
            apply.assert_not_called()
            for value in (False, True):
                status, _ = self.request(
                    "/v1/heal/simulate",
                    json.dumps({"proposal_id": "test", "authorize": value}),
                )
                self.assertEqual(status, 200)
                apply.assert_called_with("test", authorize=value)
            status, _ = self.request("/v1/heal/simulate", '{"proposal_id":"test"}')
            self.assertEqual(status, 200)
            apply.assert_called_with("test", authorize=False)

    def test_vault_detail_requires_object(self):
        with mock.patch("tools.elm_orchestrator.server.vault_log", return_value={"ok": True}) as log:
            status, _ = self.request("/v1/vault-log", '{"event":"test","detail":[]}')
            self.assertEqual(status, 400)
            log.assert_not_called()
            status, _ = self.request("/v1/vault-log", '{"event":"test","detail":{"ok":true}}')
            self.assertEqual(status, 200)
            log.assert_called_once_with("test", {"ok": True})

    def test_required_fields_are_nonempty_strings(self):
        for path, field in (
            ("/v1/vault-log", "event"),
            ("/v1/heal", "issue"),
            ("/v1/heal/simulate", "proposal_id"),
            ("/v1/optimize/suggest", "workload"),
        ):
            for value in (None, 1, [], {}, "", "   "):
                with self.subTest(path=path, value=value):
                    status, _ = self.request(path, json.dumps({field: value}))
                    self.assertEqual(status, 400)

    def test_valid_watermark_request(self):
        status, result = self.request("/v1/sign/watermark", '{"payload":{"test":true}}')
        self.assertEqual(status, 200)
        self.assertEqual(len(result["payload_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
