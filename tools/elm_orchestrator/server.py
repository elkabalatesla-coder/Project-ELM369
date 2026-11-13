"""Minimal stdlib HTTP server implementing openapi/elm369-orchestrator.openapi.yaml."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from tools.elm_orchestrator.agents import PROJECT_ID, diagnose, heal_propose, vault_log
from tools.elm_orchestrator.heal import list_proposals, simulate_apply
from tools.elm_orchestrator.esign import watermark
from tools.elm_orchestrator.optimizer import suggest
from tools.elm_orchestrator.time_sync import sync_report

MAX_REQUEST_BYTES = 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:  # quieter
        return

    def _json(self, code: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict[str, Any]:
        if self.headers.get("Transfer-Encoding"):
            raise ValueError("Transfer-Encoding is not supported")
        length = int(self.headers.get("Content-Length") or 0)
        if length < 0:
            raise ValueError("Content-Length must be non-negative")
        if length > MAX_REQUEST_BYTES:
            raise OverflowError("request body too large")
        if length == 0:
            return {}
        self.connection.settimeout(10)
        data = self.rfile.read(length)
        if len(data) != length:
            raise ValueError("incomplete request body")
        body = json.loads(data.decode("utf-8"))
        if not isinstance(body, dict):
            raise ValueError("JSON object required")
        return body

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {"status": "ok", "project_id": PROJECT_ID})
            return
        if path == "/v1/diag":
            self._json(200, diagnose())
            return
        if path == "/v1/time/sync":
            self._json(200, sync_report())
            return
        if path == "/v1/heal/proposals":
            self._json(200, {"proposals": list_proposals()})
            return
        self._json(404, {"error": "not_found", "path": path})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            body = self._read_json()
        except OverflowError:
            self.close_connection = True
            self._json(413, {"error": "request body too large"})
            return
        except (ValueError, OSError, RecursionError):
            self.close_connection = True
            self._json(400, {"error": "invalid JSON request"})
            return
        if path == "/v1/vault-log":
            event = body.get("event")
            if not isinstance(event, str) or not event.strip():
                self._json(400, {"error": "event required"})
                return
            detail = body.get("detail", {})
            if not isinstance(detail, dict):
                self._json(400, {"error": "detail object required"})
                return
            self._json(200, vault_log(event, detail))
            return
        if path == "/v1/heal":
            issue = body.get("issue")
            if not isinstance(issue, str) or not issue.strip():
                self._json(400, {"error": "issue required"})
                return
            self._json(200, heal_propose(issue))
            return
        if path == "/v1/heal/simulate":
            pid = body.get("proposal_id")
            if not isinstance(pid, str) or not pid.strip():
                self._json(400, {"error": "proposal_id required"})
                return
            authorize = body.get("authorize", False)
            if not isinstance(authorize, bool):
                self._json(400, {"error": "authorize boolean required"})
                return
            self._json(200, simulate_apply(pid, authorize=authorize))
            return
        if path == "/v1/sign/watermark":
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._json(400, {"error": "payload object required"})
                return
            self._json(200, watermark(payload))
            return
        if path == "/v1/optimize/suggest":
            workload = body.get("workload")
            if not isinstance(workload, str) or not workload.strip():
                self._json(400, {"error": "workload required"})
                return
            self._json(200, suggest(workload))
            return
        self._json(404, {"error": "not_found", "path": path})


def serve(host: str = "127.0.0.1", port: int = 8769) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"ELM369 orchestrator listening on http://{host}:{port}")
    httpd.serve_forever()
