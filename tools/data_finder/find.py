"""Locate project data/files by name or content substring (DATA-FIND)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SKIP = {".git", "node_modules", "__pycache__", ".venv", ".mypy_cache", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".yaml", ".yml", ".py", ".txt", ".toml", ".csv"}

WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"
PROJECT_ID = "ELM369_JMR08241978202646902"
REGISTRY = Path("data/registries/elm369_tools.json")


def find(
    query: str,
    *,
    root: Path | None = None,
    limit: int = 50,
    name_only: bool = False,
    under: str | None = None,
) -> dict[str, Any]:
    base = root or Path(".")
    q = (query or "").lower().strip()
    hits: list[dict[str, Any]] = []
    prefix = Path(under) if under else None

    for p in base.rglob("*"):
        if any(part in SKIP for part in p.parts):
            continue
        if not p.is_file():
            continue
        if prefix is not None:
            try:
                p.relative_to(prefix if prefix.is_absolute() else base / prefix)
            except ValueError:
                continue
        name_hit = q in p.name.lower() if q else False
        content_hit = False
        if (
            not name_only
            and q
            and p.suffix.lower() in TEXT_SUFFIXES
            and p.stat().st_size < 2_000_000
        ):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                content_hit = q in text.lower()
            except OSError:
                content_hit = False
        if name_hit or content_hit:
            hits.append(
                {
                    "path": str(p).replace("\\", "/"),
                    "name_hit": name_hit,
                    "content_hit": content_hit,
                }
            )
            if len(hits) >= limit:
                break
    return {
        "project_id": PROJECT_ID,
        "query": query,
        "name_only": name_only,
        "under": under,
        "count": len(hits),
        "hits": hits,
        "watermark": WATERMARK,
    }


def find_registry(query: str) -> dict[str, Any]:
    """Search the tools registry by id/name/path/category."""
    q = (query or "").lower().strip()
    if not REGISTRY.is_file():
        return {"ok": False, "error": "registry_missing", "query": query}
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    matches = []
    for t in data.get("tools") or []:
        blob = " ".join(
            str(t.get(k) or "") for k in ("id", "name", "repo_path", "category", "status", "phase")
        ).lower()
        if q in blob:
            matches.append(t)
    return {
        "ok": True,
        "query": query,
        "count": len(matches),
        "matches": matches,
        "watermark": WATERMARK,
    }
