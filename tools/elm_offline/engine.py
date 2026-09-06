"""Offline snapshot cache for ELM369 local access (issue #14).

Supported offline path for ELM369 — local file cache only.
Does not control telephony, radio, satellite, or hotspot hardware.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CACHE = Path("tools/elm_offline/data/cache")
MANIFEST = Path("tools/elm_offline/data/manifest.json")

CANNOT_CONTROL = ["telephony", "radio", "satellite", "hotspot"]
WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"
PROJECT_ID = "ELM369_JMR08241978202646902"

DEFAULT_SNAPSHOT_PATHS = [
    "docs/REPO_MAP.md",
    "docs/ELM369_IDENTITY.md",
    "docs/STATUS.md",
    "docs/BACKLOG.md",
    "docs/policy",
    "docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md",
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
                copied.append(child.as_posix())
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
        "project_id": PROJECT_ID,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "copied": copied,
        "missing": missing,
        "cannot_control": list(CANNOT_CONTROL),
        "note": "Local offline cache only — no telephony/radio/satellite/hotspot control. Supported offline path for ELM369.",
        "watermark": WATERMARK,
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
    base_cannot = {"cannot_control": list(CANNOT_CONTROL), "watermark": WATERMARK, "project_id": PROJECT_ID}
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
        "watermark": WATERMARK,
        "project_id": PROJECT_ID,
    }


def list_cached(limit: int = 200) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    if CACHE.exists():
        for p in sorted(CACHE.rglob("*")):
            if p.is_file():
                rel = p.relative_to(CACHE).as_posix()
                files.append({"path": rel, "bytes": p.stat().st_size})
                if len(files) >= limit:
                    break
    return {
        "ok": True,
        "count": len(files),
        "files": files,
        "cannot_control": list(CANNOT_CONTROL),
        "watermark": WATERMARK,
    }


def _sha256(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def verify(limit: int = 50) -> dict[str, Any]:
    """Compare cached files to live repo counterparts (hash match)."""
    if not CACHE.exists():
        return {"ok": False, "error": "no_cache", "cannot_control": list(CANNOT_CONTROL)}
    checked = 0
    mismatched: list[dict[str, str]] = []
    missing_source: list[str] = []
    for p in sorted(CACHE.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(CACHE).as_posix()
        src = Path(rel)
        checked += 1
        if not src.is_file():
            missing_source.append(rel)
        else:
            a, b = _sha256(p), _sha256(src)
            if a and b and a != b:
                mismatched.append({"path": rel, "cache": a[:12], "source": b[:12]})
        if checked >= limit:
            break
    return {
        "ok": not mismatched and not missing_source,
        "checked": checked,
        "mismatched": mismatched,
        "missing_source": missing_source,
        "cannot_control": list(CANNOT_CONTROL),
        "watermark": WATERMARK,
    }
