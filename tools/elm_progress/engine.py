"""Progress engine over the ELM369 tools registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = Path("data/registries/elm369_tools.json")


def load_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_REGISTRY
    return json.loads(p.read_text(encoding="utf-8"))


def summarize(reg: dict[str, Any] | None = None) -> dict[str, Any]:
    reg = reg or load_registry()
    tools = reg.get("tools") or []
    by_status: dict[str, int] = {}
    total_c = 0
    for t in tools:
        st = str(t.get("status") or "UNKNOWN")
        by_status[st] = by_status.get(st, 0) + 1
        total_c += float(t.get("completion") or 0)
    avg = round(total_c / len(tools), 1) if tools else 0.0
    return {
        "project_id": reg.get("project_id"),
        "tool_count": len(tools),
        "avg_completion": avg,
        "by_status": by_status,
        "tools": tools,
    }


def verify_paths(reg: dict[str, Any] | None = None, root: Path | None = None) -> dict[str, Any]:
    reg = reg or load_registry()
    base = root or Path(".")
    present = missing = 0
    details = []
    for t in reg.get("tools") or []:
        rp = t.get("repo_path")
        if not rp:
            details.append({"id": t["id"], "path": None, "exists": None})
            continue
        ok = (base / rp).exists()
        present += int(ok)
        missing += int(not ok)
        details.append({"id": t["id"], "path": rp, "exists": ok})
    return {"present": present, "missing": missing, "details": details}
