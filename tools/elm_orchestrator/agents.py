"""Scaffold implementations for ELM369 panel agents (non-destructive)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ID = "ELM369_JMR08241978202646902"
LOG_DIR = Path("tools/elm_orchestrator/data")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def diagnose(root: Path | None = None) -> dict[str, Any]:
    """Lightweight diagnostic: presence of critical tools/docs/vault."""
    base = root or Path(".")
    checks = {
        "tools.ai_outage_monitor": (base / "tools/ai_outage_monitor").is_dir(),
        "tools.elm_daily_automation": (base / "tools/elm_daily_automation").is_dir(),
        "tools.dax_memory": (base / "tools/dax_memory").is_dir(),
        "tools.qbit": (base / "tools/qbit").is_dir(),
        "tools.liquid3d_prompting": (base / "tools/liquid3d_prompting").is_dir(),
        "tools.grok_archive": (base / "tools/grok_archive").is_dir(),
        "vault.grok": (base / "vault/ELM369/JMR08241978202646902/sources/grok").is_dir(),
        "docs.repo_map": (base / "docs/REPO_MAP.md").is_file(),
        "schemas.evolution": (base / "schemas/evolution").is_dir(),
        "openapi.orchestrator": (base / "openapi/elm369-orchestrator.openapi.yaml").is_file(),
    }
    missing = [k for k, ok in checks.items() if not ok]
    return {
        "agent": "ELM369-DIAG-AGENT-01",
        "project_id": PROJECT_ID,
        "checked_at": _now(),
        "ok": not missing,
        "checks": checks,
        "missing": missing,
    }


def vault_log(event: str, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append an audit event to the local vault logger (System-State-Archive-Gamma scaffold)."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / "vault-audit.jsonl"
    row = {
        "agent": "ELM369-VAULT-LOGGER-04",
        "project_id": PROJECT_ID,
        "vault_target": "System-State-Archive-Gamma",
        "event": event,
        "detail": detail or {},
        "timestamp": _now(),
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def heal_propose(issue: str) -> dict[str, Any]:
    """Propose a gated self-heal action — never auto-applies."""
    proposal = {
        "agent": "ELM369-QBIT-REPAIR-02",
        "project_id": PROJECT_ID,
        "issue": issue,
        "proposed_at": _now(),
        "actions": [
            "snapshot current state",
            "generate additive patch candidate",
            "run unit tests in sandbox",
            "REQUEST_AUTHORIZATION before apply",
        ],
        "auto_apply": False,
        "safety": "authorized_only",
    }
    vault_log("heal_proposal", proposal)
    return proposal
