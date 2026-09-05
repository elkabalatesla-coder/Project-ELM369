"""Compose a JSON dashboard from live tools (issue #11)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools.elm_progress.engine import summarize, verify_paths
from tools.grok_archive.status import vault_status
from tools.elm_artifacts.catalog import verify as artifacts_verify
from tools.elm_devtools.inventory import list_tools


def build() -> dict[str, Any]:
    progress = summarize()
    paths = verify_paths()
    vault = vault_status()
    artifacts = artifacts_verify()
    tools = list_tools()
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
        "artifacts": artifacts,
        "devtools": {"tool_dirs": len(tools)},
        "note": "JSON board scaffold — HTML artifact UIs remain in GitHub issues until extracted.",
    }
