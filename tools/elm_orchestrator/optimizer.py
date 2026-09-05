"""Performance / logarithmic optimizer suggestion scaffold."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools.elm_orchestrator.agents import PROJECT_ID


def suggest(workload: str) -> dict[str, Any]:
    text = (workload or "").lower()
    tips: list[str] = [
        "Prefer indexed lookups / maps over linear scans for hot paths",
        "Batch I/O and avoid N+1 remote calls",
        "Cache immutable config; invalidate explicitly",
    ]
    if any(k in text for k in ("search", "recall", "log", "jsonl")):
        tips.append("For JSONL recall, maintain an in-memory tag/inverted index (O(1)/O(log n) vs O(n))")
    if any(k in text for k in ("sort", "organize", "rank")):
        tips.append("Use timsort / heapselect; avoid repeated full sorts in loops")
    if any(k in text for k in ("http", "probe", "outage", "network")):
        tips.append("Parallelize independent probes with bounded concurrency; set strict timeouts")
    return {
        "agent": "ELM369-OPT-ENGINE-03",
        "project_id": PROJECT_ID,
        "workload": workload,
        "suggested_at": datetime.now(timezone.utc).isoformat(),
        "complexity_target": "O(log n) where practical",
        "suggestions": tips,
    }
