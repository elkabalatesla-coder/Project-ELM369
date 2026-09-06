"""OMNINET / .mo* namespace router for Project ELM369.

Logical URI router only — no network mesh, satellite, hotspot, or radio control.
"""

from __future__ import annotations

import re
from typing import Any

MO = re.compile(r"^mo\*://(?P<ns>[a-z0-9_-]+)(?:/(?P<path>.*))?$", re.I)

WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"
PROJECT_ID = "ELM369_JMR08241978202646902"

# namespace -> {routes_to, lane, note}
ROUTES: dict[str, dict[str, str]] = {
    "vault": {"routes_to": "tools/pandora_vault + vault/ sources", "lane": "vault", "note": "Hope tips / Pandora logs"},
    "memory": {"routes_to": "tools/dax_memory", "lane": "memory", "note": "DAX memory"},
    "archive": {"routes_to": "tools/grok_archive / github_issues", "lane": "archive", "note": "Grok + issues intake"},
    "heal": {"routes_to": "tools/elm_orchestrator heal", "lane": "heal", "note": "Propose / dry-run only"},
    "progress": {"routes_to": "tools/elm_progress", "lane": "ops", "note": "Progress engine"},
    "diag": {"routes_to": "tools/elm_orchestrator diag / tools/elmdx", "lane": "diagnostics", "note": "Diag agent + ELMDX"},
    "flux": {"routes_to": "tools/elm_flux", "lane": "creative", "note": "Dry-run FLUX prompts"},
    "bo": {"routes_to": "tools/bo_assistant", "lane": "comms", "note": "Draft-only Bo"},
    "status": {"routes_to": "tools/elm_status", "lane": "ops", "note": "Unified health"},
    "artifacts": {"routes_to": "artifacts/ + tools/elm_artifacts", "lane": "ops", "note": "Artifact sandboxes"},
    "tokenizer": {"routes_to": "tools/elm_tokenizer", "lane": "ai", "note": "Prompt framework score"},
    "offline": {"routes_to": "tools/elm_offline", "lane": "ops", "note": "Local offline cache"},
    "translator": {"routes_to": "tools/elm_translator", "lane": "comms", "note": "Phrase glossary"},
    "devtools": {"routes_to": "tools/elm_devtools", "lane": "ops", "note": "Tool inventory"},
    "dashboard": {"routes_to": "tools/elm_dashboard", "lane": "ops", "note": "AI-HUB board"},
    "finder": {"routes_to": "tools/data_finder", "lane": "ops", "note": "Data location finder"},
    "evolution": {"routes_to": "tools/elm_evolution", "lane": "automation", "note": "Gated evolution"},
    "qbit": {"routes_to": "tools/qbit", "lane": "ai", "note": "QSTATE scoring"},
    "liquid3d": {"routes_to": "tools/liquid3d_prompting", "lane": "creative", "note": "Liquid3D prompts"},
    "daily": {"routes_to": "tools/elm_daily_automation", "lane": "ops", "note": "Daily automation runner"},
    "ziggy": {"routes_to": "docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md", "lane": "intake", "note": "Ziggy case intake"},
    "hope": {"routes_to": "docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md + vault/", "lane": "vault", "note": "Hope vault tips"},
    "pix": {"routes_to": "docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md", "lane": "research", "note": "Private Eye X dig"},
    "roster": {"routes_to": "docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md", "lane": "ops", "note": "Grok bot roster"},
}


def namespaces() -> dict[str, Any]:
    return {
        "project_id": PROJECT_ID,
        "protocol": "OMNINET/.mo*",
        "count": len(ROUTES),
        "namespaces": {k: v for k, v in sorted(ROUTES.items())},
        "note": "Logical router only — no network mesh control.",
        "watermark": WATERMARK,
    }


def resolve(uri: str) -> dict[str, Any]:
    m = MO.match((uri or "").strip())
    if not m:
        return {
            "ok": False,
            "error": "invalid_uri",
            "hint": "Use mo*://<namespace>[/path]",
            "watermark": WATERMARK,
        }
    ns = m.group("ns").lower()
    path = m.group("path") or ""
    target = ROUTES.get(ns)
    if not target:
        return {
            "ok": False,
            "error": "unknown_namespace",
            "namespace": ns,
            "known": sorted(ROUTES),
            "watermark": WATERMARK,
        }
    return {
        "ok": True,
        "uri": uri,
        "namespace": ns,
        "path": path,
        "routes_to": target["routes_to"],
        "lane": target.get("lane"),
        "detail": target.get("note"),
        "protocol": "OMNINET/.mo*",
        "project_id": PROJECT_ID,
        "note": "Logical router only — no network mesh control.",
        "watermark": WATERMARK,
    }


def validate(uri: str) -> dict[str, Any]:
    """Resolve plus a boolean valid flag for scripting."""
    out = resolve(uri)
    return {**out, "valid": bool(out.get("ok"))}
