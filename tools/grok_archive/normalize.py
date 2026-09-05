"""Normalize heterogeneous chat exports into ELM conversation JSONL."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


PROJECT_ID = "ELM369_JMR08241978202646902"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def iter_json_records(path: Path) -> Iterator[Any]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return
    if path.suffix.lower() == ".jsonl":
        for line in text.splitlines():
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
        return
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return
    if isinstance(data, list):
        for item in data:
            yield item
    else:
        yield data


def normalize_record(obj: Any, *, source: str, origin: str) -> list[dict[str, Any]]:
    """Best-effort normalize common Grok/ChatGPT-like shapes into message rows."""
    rows: list[dict[str, Any]] = []

    def add(role: str, content: str, **extra: Any) -> None:
        content = (content or "").strip()
        if not content:
            return
        rows.append(
            {
                "record_id": str(uuid.uuid4()),
                "project_id": PROJECT_ID,
                "source": source,
                "origin_file": origin,
                "role": role,
                "content": content,
                "ingested_at": _now(),
                **extra,
            }
        )

    if not isinstance(obj, dict):
        add("unknown", str(obj))
        return rows

    # Easy Grok Chat Exporter / JSONL message lines
    if "message" in obj and ("sender" in obj or "role" in obj):
        role = str(obj.get("sender") or obj.get("role") or "unknown")
        add(role, str(obj.get("message")), model=obj.get("model"), thinking=obj.get("thinking"))
        return rows

    # Conversation with messages[]
    messages = obj.get("messages") or obj.get("conversation") or obj.get("turns")
    title = obj.get("title") or obj.get("name")
    conv_id = obj.get("id") or obj.get("conversation_id")
    if isinstance(messages, list):
        for msg in messages:
            if not isinstance(msg, dict):
                add("unknown", str(msg), conversation_id=conv_id, title=title)
                continue
            role = str(msg.get("role") or msg.get("sender") or msg.get("author") or "unknown")
            content = msg.get("content") or msg.get("message") or msg.get("text") or ""
            if isinstance(content, list):
                # OpenAI-ish content parts
                parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("text"):
                        parts.append(str(part["text"]))
                    else:
                        parts.append(str(part))
                content = "\n".join(parts)
            add(role, str(content), conversation_id=conv_id, title=title)
        return rows

    # Nested mapping of conversations
    for key in ("conversations", "chats", "items", "data"):
        nested = obj.get(key)
        if isinstance(nested, list):
            for item in nested:
                rows.extend(normalize_record(item, source=source, origin=origin))
            return rows

    # Fallback: stringify interesting fields
    blob = obj.get("text") or obj.get("body") or obj.get("prompt")
    if blob:
        add("unknown", str(blob), title=obj.get("title"))
    return rows


DESIGN_PATTERNS = [
    re.compile(r"\b(design|architect|schema|spec)\b", re.I),
    re.compile(r"\b(implement|develop|build|code|api|cli)\b", re.I),
    re.compile(r"\b(TODO|FIXME|next step|we should|need to)\b", re.I),
    re.compile(r"\b(vault|qbit|dax|liquid.?3d|outage|automation)\b", re.I),
]


def extract_backlog(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in rows:
        content = row.get("content") or ""
        if not any(p.search(content) for p in DESIGN_PATTERNS):
            continue
        # Split on newlines / bullets for actionable fragments
        for line in re.split(r"[\n\r]+", content):
            line = line.strip(" -*\t")
            if len(line) < 24:
                continue
            if not any(p.search(line) for p in DESIGN_PATTERNS):
                continue
            kind = "design" if re.search(r"design|architect|schema|spec", line, re.I) else "develop"
            items.append(
                {
                    "item_id": str(uuid.uuid4()),
                    "kind": kind,
                    "text": line[:500],
                    "source_record_id": row.get("record_id"),
                    "source": row.get("source"),
                    "origin_file": row.get("origin_file"),
                    "extracted_at": _now(),
                }
            )
    # de-dupe by normalized text
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        key = re.sub(r"\s+", " ", item["text"].lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
