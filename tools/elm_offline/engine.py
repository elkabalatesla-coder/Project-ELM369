"""Offline snapshot cache for ELM369 local access (issue #14).

Supported offline path for ELM369 — local file cache only.
Does not control telephony, radio, satellite, or hotspot hardware.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CACHE = Path("tools/elm_offline/data/cache")
MANIFEST = Path("tools/elm_offline/data/manifest.json")

CANNOT_CONTROL = ["telephony", "radio", "satellite", "hotspot"]

DEFAULT_SNAPSHOT_PATHS = [
    "docs/REPO_MAP.md",
    "docs/ELM369_IDENTITY.md",
    "docs/STATUS.md",
    "docs/BACKLOG.md",
    "docs/policy",
    "docs/ELM369_COMPLETION_CERTIFICATE.json",
    "data/registries/elm369_tools.json",
    "artifacts/sandboxes/manifest.json",
    "vault/ELM369/JMR08241978202646902/README.md",
    "vault/ELM369/JMR0824197846902/README.md",
    "vault/ELM369/JMR08241978202646902/sources/grok/README.md",
    "vault/ELM369/JMR08241978202646902/sources/github-issues/README.md",
    "vault/ELM369/JMR08241978202646902/sources/grok/extracted/backlog-grok.jsonl",
    "vault/ELM369/JMR08241978202646902/sources/github-issues/extracted/backlog-github-issues.jsonl",
]


def _copy_tree_or_file(src: Path, dest: Path) -> list[str]:
    """Copy a file or recursively copy a directory; return relative paths copied under dest root naming."""
    copied: list[str] = []
    if src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return [str(src)]
    if src.is_dir():
        for child in sorted(src.rglob("*")):
            if child.is_file():
                rel_under = child.relative_to(src)
                target = dest / rel_under
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(child, target)
                # record as original repo-relative path
                try:
                    repo_rel = child.as_posix()
                except Exception:
                    repo_rel = str(child)
                copied.append(repo_rel)
    return copied


def snapshot(paths: list[str] | None = None) -> dict[str, Any]:
    """Copy key repo artifacts into a local offline cache."""
    targets = paths or list(DEFAULT_SNAPSHOT_PATHS)
    CACHE.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    missing: list[str] = []
    for rel in targets:
        src = Path(rel)
        if not src.exists():
            missing.append(rel)
            continue
        dest = CACHE / rel
        if src.is_dir():
            copied.extend(_copy_tree_or_file(src, dest))
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied.append(rel)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "copied": copied,
        "missing": missing,
        "cannot_control": list(CANNOT_CONTROL),
        "note": "Local offline cache only — no telephony/radio/satellite/hotspot control. Supported offline path for ELM369.",
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _cache_stats() -> dict[str, int]:
    file_count = 0
    total_bytes = 0
    if CACHE.exists():
        for p in CACHE.rglob("*"):
            if p.is_file():
                file_count += 1
                try:
                    total_bytes += p.stat().st_size
                except OSError:
                    pass
    return {"file_count": file_count, "bytes": total_bytes}


def _age_seconds(created_at: str | None) -> float | None:
    if not created_at:
        return None
    try:
        ts = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - ts).total_seconds())
    except ValueError:
        return None


def status() -> dict[str, Any]:
    base_cannot = {"cannot_control": list(CANNOT_CONTROL)}
    if not MANIFEST.exists():
        return {
            "ok": False,
            "error": "no_snapshot",
            **base_cannot,
            "file_count": 0,
            "bytes": 0,
            "snapshot_age_seconds": None,
        }
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stats = _cache_stats()
    age = _age_seconds(data.get("created_at"))
    return {
        **data,
        "ok": True,
        "snapshot_age_seconds": age,
        "file_count": stats["file_count"],
        "bytes": stats["bytes"],
        "cannot_control": list(CANNOT_CONTROL),
    }
