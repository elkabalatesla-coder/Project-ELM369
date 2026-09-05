"""Simple inverted index over normalized + backlog JSONL (O(1)/O(log n)-minded)."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in TOKEN.findall(text or "")}


def build_index(source: str = "grok", vault_root: Path | None = None) -> dict[str, Any]:
    from tools.grok_archive.ingest import DEFAULT_VAULT

    root = vault_root or DEFAULT_VAULT / source
    inv: dict[str, set[str]] = defaultdict(set)
    docs: dict[str, dict[str, Any]] = {}

    for folder, kind in (("normalized", "message"), ("extracted", "backlog")):
        d = root / folder
        if not d.is_dir():
            continue
        for f in d.glob("*.jsonl"):
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines()):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                doc_id = str(obj.get("item_id") or obj.get("record_id") or f"{f.name}:{i}")
                text = str(obj.get("text") or obj.get("content") or "")
                docs[doc_id] = {"kind": kind, "text": text, "meta": {k: obj.get(k) for k in ("role", "status", "source", "kind") if k in obj}}
                for tok in _tokens(text):
                    inv[tok].add(doc_id)

    out_dir = root / "extracted"
    out_dir.mkdir(parents=True, exist_ok=True)
    serial = {k: sorted(v) for k, v in inv.items()}
    index_path = out_dir / f"index-{source}.json"
    index_path.write_text(json.dumps({"docs": docs, "inv": serial}, ensure_ascii=False), encoding="utf-8")
    return {"tokens": len(serial), "docs": len(docs), "path": str(index_path)}


def search(query: str, *, source: str = "grok", vault_root: Path | None = None, limit: int = 20) -> list[dict[str, Any]]:
    from tools.grok_archive.ingest import DEFAULT_VAULT

    root = vault_root or DEFAULT_VAULT / source
    index_path = root / "extracted" / f"index-{source}.json"
    if not index_path.exists():
        build_index(source=source, vault_root=vault_root)
    data = json.loads(index_path.read_text(encoding="utf-8"))
    docs = data.get("docs") or {}
    inv = data.get("inv") or {}
    qtoks = _tokens(query)
    if not qtoks:
        return []
    scores: dict[str, int] = defaultdict(int)
    for tok in qtoks:
        for doc_id in inv.get(tok, []):
            scores[doc_id] += 1
    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:limit]
    out = []
    for doc_id, score in ranked:
        row = dict(docs.get(doc_id) or {})
        row["doc_id"] = doc_id
        row["score"] = score
        out.append(row)
    return out
