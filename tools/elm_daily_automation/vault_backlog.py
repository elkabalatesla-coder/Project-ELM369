"""Count design/dev backlog items across multi-source vaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_SOURCES = Path("vault/ELM369/JMR08241978202646902/sources")


def backlog_report(sources_root: Path | None = None) -> dict[str, Any]:
    root = sources_root or DEFAULT_SOURCES
    by_source: dict[str, dict[str, int]] = {}
    total = 0
    open_total = 0
    if not root.is_dir():
        return {
            "status": "noted",
            "detail": "vault sources missing",
            "total": 0,
            "open": 0,
            "by_source": {},
        }
    for src_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        extracted = src_dir / "extracted"
        design = develop = other = open_n = 0
        if extracted.is_dir():
            for f in extracted.glob("backlog-*.jsonl"):
                for line in f.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    total += 1
                    kind = str(item.get("kind") or "other")
                    status = str(item.get("status") or "open")
                    if status != "done":
                        open_n += 1
                        open_total += 1
                    if kind == "design":
                        design += 1
                    elif kind == "develop":
                        develop += 1
                    else:
                        other += 1
        by_source[src_dir.name] = {
            "design": design,
            "develop": develop,
            "other": other,
            "open": open_n,
            "total": design + develop + other,
        }
    return {
        "status": "ok" if total else "noted",
        "detail": f"{open_total} open / {total} backlog items across {len(by_source)} sources",
        "total": total,
        "open": open_total,
        "by_source": by_source,
    }
