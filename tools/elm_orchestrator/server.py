"""Minimal stdlib HTTP server implementing openapi/elm369-orchestrator.openapi.yaml."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from tools.elm_orchestrator.agents import PROJECT_ID, diagnose, heal_propose, vault_log
from tools.elm_orchestrator.esign import watermark
from tools.elm_orchestrator.optimizer import suggest
from tools.elm_orchestrator.time_sync import sync_report


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
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        data = self.rfile.read(length)
        return json.loads(data.decode("utf-8") or "{}")

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
        self._json(404, {"error": "not_found", "path": path})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        body = self._read_json()
        if path == "/v1/vault-log":
            event = str(body.get("event") or "")
            if not event:
                self._json(400, {"error": "event required"})
                return
            self._json(200, vault_log(event, body.get("detail") or {}))
            return
        if path == "/v1/heal":
            issue = str(body.get("issue") or "")
            if not issue:
                self._json(400, {"error": "issue required"})
                return
            self._json(200, heal_propose(issue))
            return
        if path == "/v1/sign/watermark":
            payload = body.get("payload")
            if not isinstance(payload, dict):
                self._json(400, {"error": "payload object required"})
                return
            self._json(200, watermark(payload))
            return
        if path == "/v1/optimize/suggest":
            workload = str(body.get("workload") or "")
            if not workload:
                self._json(400, {"error": "workload required"})
                return
            self._json(200, suggest(workload))
            return
        self._json(404, {"error": "not_found", "path": path})


def serve(host: str = "127.0.0.1", port: int = 8769) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"ELM369 orchestrator listening on http://{host}:{port}")
    httpd.serve_forever()
