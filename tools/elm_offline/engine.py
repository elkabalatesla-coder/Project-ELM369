"""Offline snapshot cache for ELM369 local access (issue #14)."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CACHE = Path("tools/elm_offline/data/cache")
MANIFEST = Path("tools/elm_offline/data/manifest.json")


def snapshot(paths: list[str] | None = None) -> dict[str, Any]:
    """Copy key repo artifacts into a local offline cache."""
    defaults = [
        "docs/REPO_MAP.md",
        "docs/ELM369_IDENTITY.md",
        "data/registries/elm369_tools.json",
        "docs/BACKLOG.md",
        "vault/ELM369/JMR08241978202646902/sources/grok/extracted/backlog-grok.jsonl",
        "vault/ELM369/JMR08241978202646902/sources/github-issues/extracted/backlog-github-issues.jsonl",
    ]
    targets = paths or defaults
    CACHE.mkdir(parents=True, exist_ok=True)
    copied = []
    missing = []
    for rel in targets:
        src = Path(rel)
        if not src.exists():
            missing.append(rel)
            continue
        dest = CACHE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dest)
        copied.append(rel)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "copied": copied,
        "missing": missing,
        "note": "Local offline cache only — no satellite/modem control.",
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def status() -> dict[str, Any]:
    if not MANIFEST.exists():
        return {"ok": False, "error": "no_snapshot"}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))
