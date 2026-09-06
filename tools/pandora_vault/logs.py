"""Security Log 1, Security Log 2, and Pandora Vault local feeds."""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("tools/pandora_vault/data")
PROJECT_ID = "ELM369_JMR08241978202646902"
OPERATOR = "JMR08241978202646902"
COMPANION_ID = "JMR0824197846902"
CHANNELS = ("security1", "security2", "pandora")
MIRROR_LEVELS = frozenset({"WARN", "ERROR", "CRITICAL", "VAULT"})
ESIGN = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"


def _files(root: Path | None = None) -> dict[str, Path]:
    base = root or ROOT
    return {
        "security1": base / "security-log-1.jsonl",
        "security2": base / "security-log-2.jsonl",
        "pandora": base / "pandora-vault.jsonl",
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append(
    channel: str,
    level: str,
    message: str,
    *,
    root: Path | None = None,
    **extra: Any,
) -> dict[str, Any]:
    channel = channel.lower()
    files = _files(root)
    if channel not in files:
        raise ValueError("channel must be security1|security2|pandora")
    base = root or ROOT
    base.mkdir(parents=True, exist_ok=True)
    row = {
        "project_id": PROJECT_ID,
        "companion_id": COMPANION_ID,
        "operator": OPERATOR,
        "channel": channel,
        "level": level.upper(),
        "message": message,
        "timestamp": _now(),
        "location": "Kokomo, Indiana 46902 USA",
        "esign": ESIGN,
        **extra,
    }
    path = files[channel]
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    # mirror critical events to pandora
    if channel != "pandora" and row["level"] in MIRROR_LEVELS:
        mirrored = {**row, "channel": "pandora", "mirrored_from": channel}
        with files["pandora"].open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(mirrored, ensure_ascii=False) + "\n")
    return row


def sync_event(
    message: str,
    *,
    level: str = "INFO",
    root: Path | None = None,
) -> dict[str, Any]:
    """Write to both security logs + pandora (issue #11/#29 pattern)."""
    a = append("security1", level, message, root=root)
    b = append("security2", level, message, root=root)
    c = append("pandora", "VAULT", message, root=root)
    return {
        "ok": True,
        "security1": a,
        "security2": b,
        "pandora": c,
        "channels_written": list(CHANNELS),
        "esign": ESIGN,
    }


def tail(
    channel: str,
    limit: int = 20,
    *,
    root: Path | None = None,
) -> list[dict[str, Any]]:
    channel = channel.lower()
    files = _files(root)
    if channel not in files:
        raise ValueError("channel must be security1|security2|pandora")
    if limit < 0:
        raise ValueError("limit must be >= 0")
    path = files[channel]
    if not path.exists():
        return []
    buf: deque[dict[str, Any]] = deque(maxlen=limit if limit > 0 else None)
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                buf.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return list(buf)


def channel_stats(*, root: Path | None = None) -> dict[str, Any]:
    files = _files(root)
    out: dict[str, Any] = {}
    for name, path in files.items():
        if not path.exists():
            out[name] = {"exists": False, "lines": 0, "bytes": 0}
            continue
        lines = 0
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    lines += 1
        out[name] = {"exists": True, "lines": lines, "bytes": path.stat().st_size}
    return {
        "project_id": PROJECT_ID,
        "companion_id": COMPANION_ID,
        "channels": out,
        "esign": ESIGN,
    }
