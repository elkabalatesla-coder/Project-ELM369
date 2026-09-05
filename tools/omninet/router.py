"""OMNINET / .mo* namespace router scaffold."""

from __future__ import annotations

import re
from typing import Any

MO = re.compile(r"^mo\*://(?P<ns>[a-z0-9_-]+)(?:/(?P<path>.*))?$", re.I)

ROUTES = {
    "vault": "tools/pandora_vault + vault/ sources",
    "memory": "tools/dax_memory",
    "archive": "tools/grok_archive / github_issues",
    "heal": "tools/elm_orchestrator heal",
    "progress": "tools/elm_progress",
    "diag": "tools/elm_orchestrator diag / tools/elmdx",
    "flux": "tools/elm_flux",
    "bo": "tools/bo_assistant",
}


def resolve(uri: str) -> dict[str, Any]:
    m = MO.match((uri or "").strip())
    if not m:
        return {"ok": False, "error": "invalid_uri", "hint": "Use mo*://<namespace>[/path]"}
    ns = m.group("ns").lower()
    path = m.group("path") or ""
    target = ROUTES.get(ns)
    if not target:
        return {"ok": False, "error": "unknown_namespace", "namespace": ns, "known": sorted(ROUTES)}
    return {
        "ok": True,
        "uri": uri,
        "namespace": ns,
        "path": path,
        "routes_to": target,
        "protocol": "OMNINET/.mo*",
        "note": "Logical router only — no network mesh control.",
    }
