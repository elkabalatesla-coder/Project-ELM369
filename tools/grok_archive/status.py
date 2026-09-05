"""Multi-source vault status summary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.grok_archive.ingest import DEFAULT_VAULT


def vault_status(sources_root: Path | None = None) -> dict[str, Any]:
    base = sources_root or DEFAULT_VAULT
    sources: dict[str, Any] = {}
    if not base.is_dir():
        return {"ok": False, "error": "sources_missing", "path": str(base)}
    for src in sorted(p for p in base.iterdir() if p.is_dir()):
        raw_files = [p for p in (src / "raw").glob("*") if p.is_file()] if (src / "raw").is_dir() else []
        norm_msgs = 0
        if (src / "normalized").is_dir():
            for f in (src / "normalized").glob("*.jsonl"):
                norm_msgs += sum(1 for line in f.read_text(encoding="utf-8").splitlines() if line.strip())
        open_b = total_b = 0
        if (src / "extracted").is_dir():
            for f in (src / "extracted").glob("backlog-*.jsonl"):
                for line in f.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    total_b += 1
                    if item.get("status", "open") != "done":
                        open_b += 1
        indexed = (src / "extracted" / f"index-{src.name}.json").is_file()
        sources[src.name] = {
            "raw_files": len(raw_files),
            "normalized_messages": norm_msgs,
            "backlog_total": total_b,
            "backlog_open": open_b,
            "indexed": indexed,
        }
    return {
        "ok": True,
        "sources": sources,
        "totals": {
            "normalized_messages": sum(s["normalized_messages"] for s in sources.values()),
            "backlog_open": sum(s["backlog_open"] for s in sources.values()),
            "backlog_total": sum(s["backlog_total"] for s in sources.values()),
        },
    }
