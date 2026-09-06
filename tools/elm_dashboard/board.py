"""Compose a JSON dashboard from live tools (issue #11)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools.elm_artifacts.catalog import verify as artifacts_verify
from tools.elm_dashboard.cases import summarize_case_queue
from tools.elm_dashboard.roster import roster_lanes
from tools.elm_devtools.inventory import list_tools
from tools.elm_policy.geofence import stamp_line
from tools.elm_progress.engine import summarize, verify_paths
from tools.grok_archive.status import vault_status

VAULT_PRIMARY = "JMR08241978202646902"
VAULT_COMPANION = "JMR0824197846902"


def build(*, include_cases: bool = True) -> dict[str, Any]:
    progress = summarize()
    paths = verify_paths()
    vault = vault_status()
    artifacts = artifacts_verify()
    tools = list_tools()
    lanes = roster_lanes()
    case_queue = summarize_case_queue() if include_cases else {"skipped": True}
    return {
        "title": "Project ELM369 Security & Integrated Architecture Dashboard",
        "project_id": f"ELM369_{VAULT_PRIMARY}",
        "vault_ids": {
            "primary": VAULT_PRIMARY,
            "companion": VAULT_COMPANION,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": stamp_line(),
        "tabs": ["COMMAND", "TOOLS", "SECURITY", "VAULT", "PROGRESS", "ROSTER", "CASES"],
        "progress": {
            "avg_completion": progress["avg_completion"],
            "by_status": progress["by_status"],
            "tool_count": progress["tool_count"],
        },
        "path_verify": {"present": paths["present"], "missing": paths["missing"]},
        "vault": vault.get("totals"),
        "artifacts": artifacts,
        "devtools": {"tool_dirs": len(tools)},
        "roster_lanes": lanes,
        "case_queue": case_queue,
        "hard_rules": {
            "geo": "Kokomo IN 46902 only",
            "no_florida_google_retries": True,
            "filing_joseph_gated": True,
            "heal_dry_run_only": True,
            "no_live_sms_phone_adb_satellite": True,
        },
        "esign": "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902",
        "note": "JSON board — HTML artifact UIs remain in GitHub issues until extracted.",
    }
