"""Security Log 1, Security Log 2, and Pandora Vault local feeds."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("tools/pandora_vault/data")
PROJECT_ID = "ELM369_JMR08241978202646902"
OPERATOR = "JMR08241978202646902"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append(channel: str, level: str, message: str, **extra: Any) -> dict[str, Any]:
    channel = channel.lower()
    files = {
        "security1": ROOT / "security-log-1.jsonl",
        "security2": ROOT / "security-log-2.jsonl",
        "pandora": ROOT / "pandora-vault.jsonl",
    }
    if channel not in files:
        raise ValueError("channel must be security1|security2|pandora")
    ROOT.mkdir(parents=True, exist_ok=True)
    row = {
        "project_id": PROJECT_ID,
        "operator": OPERATOR,
        "channel": channel,
        "level": level.upper(),
        "message": message,
        "timestamp": _now(),
        **extra,
    }
    path = files[channel]
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    # mirror critical events to pandora
    if channel != "pandora" and level.upper() in {"WARN", "ERROR", "CRITICAL", "VAULT"}:
        with files["pandora"].open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**row, "channel": "pandora", "mirrored_from": channel}, ensure_ascii=False) + "\n")
    return row


def sync_event(message: str, *, level: str = "INFO") -> dict[str, Any]:
    """Write to both security logs + pandora (issue #11/#29 pattern)."""
    a = append("security1", level, message)
    b = append("security2", level, message)
    c = append("pandora", "VAULT", message)
    return {"security1": a, "security2": b, "pandora": c}


def tail(channel: str, limit: int = 20) -> list[dict[str, Any]]:
    files = {
        "security1": ROOT / "security-log-1.jsonl",
        "security2": ROOT / "security-log-2.jsonl",
        "pandora": ROOT / "pandora-vault.jsonl",
    }
    path = files[channel.lower()]
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows[-limit:]
