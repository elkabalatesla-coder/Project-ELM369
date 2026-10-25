"""Local-only JSON API adapter for the ELM369 adaptive keyboard.

This API resolves commands and evaluates policy. It never executes generated code.
Run on loopback only; provide ELM369_API_TOKEN through the environment.
"""
import hmac
import json
import os
from pathlib import Path
from wsgiref.simple_server import make_server, WSGIServer
from socketserver import ThreadingMixIn

from .policy_gate import ArtifactManifest
from .service import KeyboardCommandService
from .audit_store import SQLiteAuditLedger

MAX_BODY_BYTES = 16 * 1024
MAX_COMMAND_CHARS = 256
MAX_CONTENT_BYTES = 8 * 1024


def _json_bytes(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class KeyboardAPI:
    def __init__(self, service=None, token=None):
        self.service = service or KeyboardCommandService()
        self.token = token if token is not None else os.environ.get("ELM369_API_TOKEN", "")

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")
        host = environ.get("HTTP_HOST", "").lower()
        if host and host.split(":", 1)[0].strip("[]") not in {"127.0.0.1", "localhost", "::1"}:
            return self._respond(start_response, "421 Misdirected Request", {"status": "LOCAL_HOST_ONLY"})
        if path in {"/", "/ui"} and method == "GET":
            dashboard = Path(__file__).resolve().parent.parent / "demos" / "adaptive_keyboard_dashboard" / "index.html"
            try:
                body = dashboard.read_bytes()
            except OSError:
                return self._respond(start_response, "503 Service Unavailable", {"status": "DASHBOARD_UNAVAILABLE"})
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"),
                                      ("Content-Length", str(len(body))), ("Cache-Control", "no-store"),
                                      ("X-Content-Type-Options", "nosniff"),
                                      ("Content-Security-Policy", "default-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'")])
            return [body]
        if path == "/health" and method == "GET":
            return self._respond(start_response, "200 OK", {"status": "ok", "execution": "disabled"})
        if path not in {"/v1/command", "/v1/audit"}:
            return self._respond(start_response, "404 Not Found", {"status": "NOT_FOUND"})
        if not self.token:
            return self._respond(start_response, "503 Service Unavailable",
                                  {"status": "UNAVAILABLE", "reason": "API token is not configured"})
        supplied = environ.get("HTTP_AUTHORIZATION", "")
        expected = "Bearer " + self.token
        if not hmac.compare_digest(supplied, expected):
            return self._respond(start_response, "401 Unauthorized", {"status": "UNAUTHORIZED"})
        if path == "/v1/audit":
            if method != "GET":
                return self._respond(start_response, "405 Method Not Allowed", {"status": "METHOD_NOT_ALLOWED"})
            return self._respond(start_response, "200 OK", {
                "status": "OK", "valid": self.service.audit_is_valid(),
                "events": list(self.service.audit_events()),
            })
        if method != "POST":
            return self._respond(start_response, "405 Method Not Allowed", {"status": "METHOD_NOT_ALLOWED"})
        raw_length = environ.get("CONTENT_LENGTH", "")
        try:
            length = int(raw_length)
        except (TypeError, ValueError):
            return self._respond(start_response, "400 Bad Request", {"status": "INVALID_LENGTH"})
        if length < 0 or length > MAX_BODY_BYTES:
            return self._respond(start_response, "413 Payload Too Large", {"status": "BODY_TOO_LARGE"})
        if environ.get("CONTENT_TYPE", "").split(";", 1)[0].strip().lower() != "application/json":
            return self._respond(start_response, "415 Unsupported Media Type", {"status": "JSON_REQUIRED"})
        try:
            raw = environ["wsgi.input"].read(length)
            payload = json.loads(raw.decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
            return self._respond(start_response, "400 Bad Request", {"status": "INVALID_JSON"})
        if not isinstance(payload, dict):
            return self._respond(start_response, "400 Bad Request", {"status": "OBJECT_REQUIRED"})
        command = payload.get("command")
        if not isinstance(command, str) or not command.strip() or len(command) > MAX_COMMAND_CHARS:
            return self._respond(start_response, "400 Bad Request", {"status": "INVALID_COMMAND"})
        confirmed = payload.get("confirmed", False)
        if not isinstance(confirmed, bool):
            return self._respond(start_response, "400 Bad Request", {"status": "INVALID_CONFIRMATION"})
        manifest_data = payload.get("manifest")
        content_text = payload.get("content")
        manifest = None
        content = None
        if manifest_data is not None or content_text is not None:
            if not isinstance(manifest_data, dict) or not isinstance(content_text, str):
                return self._respond(start_response, "400 Bad Request", {"status": "INVALID_ARTIFACT_INPUT"})
            if len(content_text.encode("utf-8")) > MAX_CONTENT_BYTES:
                return self._respond(start_response, "413 Payload Too Large", {"status": "ARTIFACT_TOO_LARGE"})
            try:
                capabilities = manifest_data["capabilities"]
                if not isinstance(capabilities, list) or any(not isinstance(x, str) for x in capabilities):
                    raise ValueError("capabilities must be a string list")
                manifest = ArtifactManifest(
                    artifact_id=manifest_data["artifact_id"],
                    version=manifest_data["version"],
                    content_sha256=manifest_data["content_sha256"],
                    capabilities=tuple(capabilities),
                    risk_class=manifest_data.get("risk_class", "low"),
                    network=manifest_data.get("network", "deny-by-default"),
                    timeout_ms=manifest_data.get("timeout_ms", 5000),
                    memory_mb=manifest_data.get("memory_mb", 128),
                )
                if not all(isinstance(getattr(manifest, k), str) for k in
                           ("artifact_id", "version", "content_sha256", "risk_class", "network")):
                    raise ValueError("manifest text fields must be strings")
                if not isinstance(manifest.timeout_ms, int) or isinstance(manifest.timeout_ms, bool):
                    raise ValueError("timeout_ms must be an integer")
                if not isinstance(manifest.memory_mb, int) or isinstance(manifest.memory_mb, bool):
                    raise ValueError("memory_mb must be an integer")
                content = content_text.encode("utf-8")
            except (KeyError, TypeError, ValueError):
                return self._respond(start_response, "400 Bad Request", {"status": "INVALID_MANIFEST"})
        result = self.service.request(command, manifest, content, confirmed)
        return self._respond(start_response, "200 OK", result)

    @staticmethod
    def _respond(start_response, status, payload):
        body = _json_bytes(payload)
        start_response(status, [("Content-Type", "application/json; charset=utf-8"),
                                ("Content-Length", str(len(body))),
                                ("Cache-Control", "no-store"),
                                ("X-Content-Type-Options", "nosniff")])
        return [body]


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


def main():
    token = os.environ.get("ELM369_API_TOKEN", "")
    if len(token) < 24:
        raise SystemExit("Set ELM369_API_TOKEN to a random secret of at least 24 characters.")
    audit_path = os.environ.get("ELM369_AUDIT_DB", "elm369_audit.sqlite3")
    service = KeyboardCommandService(ledger=SQLiteAuditLedger(audit_path))
    app = KeyboardAPI(service=service, token=token)
    # Loopback-only same-origin dashboard/API bridge. Do not expose publicly.
    with make_server("127.0.0.1", 8769, app, server_class=ThreadingWSGIServer) as server:
        print("ELM369 keyboard dashboard/API listening on http://127.0.0.1:8769/ui")
        print("Durable audit database:", audit_path)
        server.serve_forever()


if __name__ == "__main__":
    main()
