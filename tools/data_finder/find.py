"""Locate project data/files by name or content substring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SKIP = {".git", "node_modules", "__pycache__", ".venv"}


def find(query: str, *, root: Path | None = None, limit: int = 50) -> dict[str, Any]:
    base = root or Path(".")
    q = (query or "").lower()
    hits = []
    for p in base.rglob("*"):
        if any(part in SKIP for part in p.parts):
            continue
        if not p.is_file():
            continue
        name_hit = q in p.name.lower()
        content_hit = False
        if p.suffix.lower() in {".md", ".json", ".jsonl", ".yaml", ".yml", ".py", ".txt"} and p.stat().st_size < 2_000_000:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                content_hit = q in text.lower()
            except OSError:
                content_hit = False
        if name_hit or content_hit:
            hits.append({"path": str(p), "name_hit": name_hit, "content_hit": content_hit})
            if len(hits) >= limit:
                break
    return {"query": query, "count": len(hits), "hits": hits}
