"""Inverted index over DAX memories for faster recall."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from tools.dax_memory.store import DEFAULT_STORE

TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def build_index(store_path: Path | None = None) -> dict[str, Any]:
    path = store_path or DEFAULT_STORE
    inv: dict[str, set[str]] = defaultdict(set)
    docs: dict[str, dict[str, Any]] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            mid = str(obj.get("memory_id") or obj.get("id") or "")
            if not mid:
                continue
            text = str(obj.get("content") or "")
            docs[mid] = {
                "content": text,
                "kind": obj.get("kind"),
                "tags": obj.get("tags") or [],
                "archived": bool(obj.get("archived")),
            }
            for tok in TOKEN.findall(text):
                inv[tok.lower()].add(mid)
            for tag in obj.get("tags") or []:
                inv[str(tag).lower()].add(mid)
    out = path.parent / "index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"docs": docs, "inv": {k: sorted(v) for k, v in inv.items()}}, ensure_ascii=False),
        encoding="utf-8",
    )
    return {"docs": len(docs), "tokens": len(inv), "path": str(out)}


def indexed_recall(query: str, *, store_path: Path | None = None, limit: int = 10) -> list[dict[str, Any]]:
    path = store_path or DEFAULT_STORE
    index_path = path.parent / "index.json"
    if not index_path.exists():
        build_index(path)
    data = json.loads(index_path.read_text(encoding="utf-8"))
    docs = data.get("docs") or {}
    inv = data.get("inv") or {}
    qtoks = {t.lower() for t in TOKEN.findall(query)}
    if not qtoks:
        return []
    scores: dict[str, int] = defaultdict(int)
    for tok in qtoks:
        for mid in inv.get(tok, []):
            scores[mid] += 1
    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    out = []
    for mid, score in ranked:
        doc = docs.get(mid) or {}
        if doc.get("archived"):
            continue
        row = {"id": mid, "score": score, **doc}
        out.append(row)
        if len(out) >= limit:
            break
    return out
