"""File-backed DAX memory store (JSONL)."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PROJECT_ID = "ELM369_JMR08241978202646902"
ROOT = Path(__file__).resolve().parent
DEFAULT_STORE = ROOT / "data" / "memories.jsonl"
KINDS = {"fact", "state", "procedure", "connection", "note"}


@dataclass
class MemoryEntry:
    memory_id: str
    project_id: str
    kind: str
    content: str
    created_at: str
    provenance: dict[str, Any]
    tags: list[str] = field(default_factory=list)
    confidence: float = 1.0
    updated_at: str | None = None
    archived: bool = False


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def store(
    content: str,
    *,
    kind: str = "note",
    tags: Iterable[str] | None = None,
    confidence: float = 1.0,
    source: str = "cli",
    actor: str = "elkabalatesla-coder",
    path: Path | None = None,
) -> MemoryEntry:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {sorted(KINDS)}")
    if not content.strip():
        raise ValueError("content must be non-empty")
    conf = max(0.0, min(1.0, float(confidence)))
    entry = MemoryEntry(
        memory_id=str(uuid.uuid4()),
        project_id=PROJECT_ID,
        kind=kind,
        content=content.strip(),
        created_at=_now(),
        provenance={"source": source, "actor": actor},
        tags=[t.strip() for t in (tags or []) if t and t.strip()],
        confidence=conf,
    )
    _append(entry, path or DEFAULT_STORE)
    return entry


def list_entries(
    *,
    path: Path | None = None,
    include_archived: bool = False,
    kind: str | None = None,
    tag: str | None = None,
    limit: int | None = None,
) -> list[MemoryEntry]:
    rows = _read_all(path or DEFAULT_STORE)
    out: list[MemoryEntry] = []
    for row in rows:
        if not include_archived and row.archived:
            continue
        if kind and row.kind != kind:
            continue
        if tag and tag not in row.tags:
            continue
        out.append(row)
    if limit is not None:
        out = out[-limit:]
    return out


def recall(
    query: str,
    *,
    path: Path | None = None,
    limit: int = 10,
) -> list[MemoryEntry]:
    """Simple case-insensitive substring / tag recall."""
    q = query.strip().lower()
    if not q:
        return []
    scored: list[tuple[int, MemoryEntry]] = []
    for entry in list_entries(path=path, include_archived=False):
        hay = " ".join([entry.content, entry.kind, *entry.tags]).lower()
        if q in hay:
            # Prefer denser matches lightly
            score = hay.count(q) * 10 + (5 if q in entry.content.lower() else 0)
            scored.append((score, entry))
    scored.sort(key=lambda pair: (-pair[0], pair[1].created_at))
    return [e for _, e in scored[:limit]]


def organize(*, path: Path | None = None) -> dict[str, Any]:
    """Rewrite store sorted by created_at; drop exact duplicate contents (keep newest)."""
    store_path = path or DEFAULT_STORE
    rows = _read_all(store_path)
    seen: dict[str, MemoryEntry] = {}
    for row in rows:
        key = re.sub(r"\s+", " ", row.content.strip().lower())
        prev = seen.get(key)
        if prev is None or row.created_at >= prev.created_at:
            seen[key] = row
    ordered = sorted(seen.values(), key=lambda e: e.created_at)
    _rewrite(ordered, store_path)
    return {
        "before": len(rows),
        "after": len(ordered),
        "removed": len(rows) - len(ordered),
    }


def archive(memory_id: str, *, path: Path | None = None) -> MemoryEntry | None:
    store_path = path or DEFAULT_STORE
    rows = _read_all(store_path)
    found: MemoryEntry | None = None
    updated: list[MemoryEntry] = []
    for row in rows:
        if row.memory_id == memory_id:
            row.archived = True
            row.updated_at = _now()
            found = row
        updated.append(row)
    if found is None:
        return None
    _rewrite(updated, store_path)
    return found


def _append(entry: MemoryEntry, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")


def _rewrite(entries: list[MemoryEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")


def _read_all(path: Path) -> list[MemoryEntry]:
    if not path.exists():
        return []
    out: list[MemoryEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            out.append(
                MemoryEntry(
                    memory_id=data["memory_id"],
                    project_id=data.get("project_id", PROJECT_ID),
                    kind=data["kind"],
                    content=data["content"],
                    created_at=data["created_at"],
                    provenance=data.get("provenance") or {"source": "unknown"},
                    tags=list(data.get("tags") or []),
                    confidence=float(data.get("confidence", 1.0)),
                    updated_at=data.get("updated_at"),
                    archived=bool(data.get("archived", False)),
                )
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return out
