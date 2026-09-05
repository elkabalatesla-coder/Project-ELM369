"""Android diagnostics over a JSON inventory (issue #26). No root/ADB required."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SAMPLE = Path("tools/elmdx/data/sample_device.json")


def load_inventory(path: Path | None = None) -> dict[str, Any]:
    p = path or SAMPLE
    return json.loads(p.read_text(encoding="utf-8"))


def diagnose(inv: dict[str, Any] | None = None) -> dict[str, Any]:
    inv = inv or load_inventory()
    apps = inv.get("apps") or []
    by = {"ok": 0, "warn": 0, "error": 0, "other": 0}
    findings = []
    for app in apps:
        st = str(app.get("status") or "other")
        by[st] = by.get(st, 0) + 1 if st in by else by.get("other", 0) + 1
        if st == "other":
            by["other"] = by.get("other", 0) + 1
        if st in {"warn", "error"}:
            findings.append(
                {
                    "app": app.get("name"),
                    "label": app.get("label"),
                    "status": st,
                    "perms": app.get("perms"),
                    "advice": "Review permissions / update or remove" if st == "error" else "Review elevated permissions",
                }
            )
    return {
        "agent": "ELMDX",
        "project_id": inv.get("project_id"),
        "device": inv.get("device"),
        "counts": by,
        "findings": findings,
        "ok": by.get("error", 0) == 0,
        "disclaimer": "Analyzes provided inventory JSON only — does not modify a phone.",
    }
