import io
import json
import unittest
from wsgiref.util import setup_testing_defaults
from .api import KeyboardAPI


class KeyboardAPITests(unittest.TestCase):
    def request(self, app, path="/v1/command", method="POST", payload=None,
                token="test-token-that-is-long-enough", content_type="application/json"):
        env = {}
        setup_testing_defaults(env)
        body = b"" if payload is None else json.dumps(payload).encode()
        env.update({"PATH_INFO": path, "REQUEST_METHOD": method,
                    "CONTENT_TYPE": content_type, "CONTENT_LENGTH": str(len(body)),
                    "wsgi.input": io.BytesIO(body)})
        if token is not None:
            env["HTTP_AUTHORIZATION"] = "Bearer " + token
        captured = {}
        def start(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)
        data = b"".join(app(env, start))
        return captured, json.loads(data.decode())

    def setUp(self):
        self.app = KeyboardAPI(token="test-token-that-is-long-enough")

    def test_host_validation_rejects_dns_rebinding_style_host(self):
        env = {}
        setup_testing_defaults(env)
        env.update({"PATH_INFO": "/health", "REQUEST_METHOD": "GET",
                    "HTTP_HOST": "localhost.attacker.example"})
        captured = {}
        def start(status, headers):
            captured["status"] = status
        body = b"".join(self.app(env, start))
        self.assertEqual(captured["status"], "421 Misdirected Request")
        self.assertIn(b"LOCAL_HOST_ONLY", body)

    def test_host_validation_accepts_bracketed_ipv6_loopback(self):
        env = {}
        setup_testing_defaults(env)
        env.update({"PATH_INFO": "/health", "REQUEST_METHOD": "GET",
                    "HTTP_HOST": "[::1]:8769"})
        captured = {}
        def start(status, headers):
            captured["status"] = status
        b"".join(self.app(env, start))
        self.assertEqual(captured["status"], "200 OK")

    def test_health_is_read_only(self):
        response, body = self.request(self.app, "/health", "GET", token=None)
        self.assertEqual(response["status"], "200 OK")
        self.assertEqual(body["execution"], "disabled")

    def test_auth_required(self):
        response, body = self.request(self.app, token="wrong-token")
        self.assertEqual(response["status"], "401 Unauthorized")
        self.assertEqual(body["status"], "UNAUTHORIZED")

    def test_command_must_be_allowlisted(self):
        response, body = self.request(self.app, payload={"command": "/not-a-command"})
        self.assertEqual(response["status"], "200 OK")
        self.assertEqual(body["status"], "DENIED")

    def test_info_command_resolves_without_execution(self):
        response, body = self.request(self.app, payload={"command": "/help"})
        self.assertEqual(body["status"], "RESOLVED")
        self.assertIn("no code executed", body["reason"])

    def test_invalid_json_shape_rejected(self):
        response, body = self.request(self.app, payload=["/help"])
        self.assertEqual(response["status"], "400 Bad Request")
        self.assertEqual(body["status"], "OBJECT_REQUIRED")

    def test_content_type_required(self):
        response, body = self.request(self.app, payload={"command": "/help"}, content_type="text/plain")
        self.assertEqual(response["status"], "415 Unsupported Media Type")

    def test_audit_endpoint_requires_auth(self):
        response, body = self.request(self.app, "/v1/audit", "GET", token="bad")
        self.assertEqual(response["status"], "401 Unauthorized")

    def test_audit_endpoint_returns_verified_chain(self):
        self.request(self.app, payload={"command": "/help"})
        response, body = self.request(self.app, "/v1/audit", "GET")
        self.assertEqual(response["status"], "200 OK")
        self.assertTrue(body["valid"])
        self.assertEqual(len(body["events"]), 1)

    def test_confirmation_field_type(self):
        response, body = self.request(self.app, payload={"command": "/run", "confirmed": "yes"})
        self.assertEqual(response["status"], "400 Bad Request")
        self.assertEqual(body["status"], "INVALID_CONFIRMATION")

    def test_api_does_not_execute_code(self):
        response, body = self.request(self.app, payload={"command": "/run", "confirmed": True})
        self.assertEqual(body["status"], "DENIED")
        self.assertIn("manifest or artifact content unavailable", body["reason"])


if __name__ == "__main__":
    unittest.main()
