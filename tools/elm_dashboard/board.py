"""Compose a JSON dashboard from live tools (issue #11)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools.elm_progress.engine import summarize, verify_paths
from tools.grok_archive.status import vault_status


def build() -> dict[str, Any]:
    progress = summarize()
    paths = verify_paths()
    vault = vault_status()
    return {
        "title": "Project ELM369 Security & Integrated Architecture Dashboard",
        "project_id": "ELM369_JMR08241978202646902",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tabs": ["COMMAND", "TOOLS", "SECURITY", "VAULT", "PROGRESS"],
        "progress": {
            "avg_completion": progress["avg_completion"],
            "by_status": progress["by_status"],
            "tool_count": progress["tool_count"],
        },
        "path_verify": {"present": paths["present"], "missing": paths["missing"]},
        "vault": vault.get("totals"),
        "note": "JSON board scaffold — HTML artifact UIs remain in GitHub issues until extracted.",
    }
