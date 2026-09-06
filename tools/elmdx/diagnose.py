"""Android diagnostics over a JSON inventory (issue #26).

Analyzes a *provided* device inventory JSON. Does not root devices, run ADB,
or mutate phones. Live device control is an intentional non-goal.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SAMPLE = Path("tools/elmdx/data/sample_device.json")
PROJECT_ID = "ELM369_JMR08241978202646902"
WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"

SEVERITY_WEIGHT = {"ok": 0, "warn": 1, "error": 3, "other": 1}


def load_inventory(path: Path | None = None) -> dict[str, Any]:
    p = path or SAMPLE
    return json.loads(p.read_text(encoding="utf-8"))


def _patch_age_days(security_patch: str | None) -> int | None:
    if not security_patch:
        return None
    try:
        # Accept YYYY-MM-DD
        d = date.fromisoformat(str(security_patch)[:10])
        return max(0, (date.today() - d).days)
    except ValueError:
        return None


def _device_health(device: dict[str, Any]) -> dict[str, Any]:
    sdk = int(device.get("sdk") or 0)
    encrypted = bool(device.get("encrypted"))
    patch = device.get("security_patch")
    age = _patch_age_days(str(patch) if patch else None)
    issues: list[str] = []
    score = 100
    if sdk and sdk < 31:
        issues.append("sdk_below_31")
        score -= 20
    if not encrypted:
        issues.append("not_encrypted")
        score -= 30
    if age is not None and age > 180:
        issues.append("stale_security_patch")
        score -= 15
    if age is not None and age > 365:
        issues.append("very_stale_security_patch")
        score -= 15
    return {
        "sdk": sdk or None,
        "encrypted": encrypted,
        "security_patch": patch,
        "patch_age_days": age,
        "score": max(0, score),
        "issues": issues,
    }


def diagnose(inv: dict[str, Any] | None = None) -> dict[str, Any]:
    """Score inventory apps + device posture. Never touches a live device."""
    inv = inv or load_inventory()
    apps = inv.get("apps") or []
    by = {"ok": 0, "warn": 0, "error": 0, "other": 0}
    findings: list[dict[str, Any]] = []
    severity = 0
    for app in apps:
        raw = str(app.get("status") or "other").lower()
        st = raw if raw in by else "other"
        by[st] += 1
        severity += SEVERITY_WEIGHT.get(st, 1)
        perms = int(app.get("perms") or 0)
        if st in {"warn", "error"} or perms >= 40:
            advice = "Review permissions / update or remove" if st == "error" else "Review elevated permissions"
            if perms >= 40 and st == "ok":
                advice = "High permission count — review least-privilege"
                st = "warn"
            findings.append(
                {
                    "app": app.get("name"),
                    "label": app.get("label"),
                    "status": st,
                    "perms": perms,
                    "advice": advice,
                }
            )
    device = inv.get("device") or {}
    dhealth = _device_health(device if isinstance(device, dict) else {})
    app_score = 100
    if apps:
        app_score = max(0, 100 - (by["error"] * 20 + by["warn"] * 8 + by["other"] * 5))
    overall = round((app_score * 0.6) + (dhealth["score"] * 0.4), 1)
    return {
        "agent": "ELMDX",
        "project_id": inv.get("project_id") or PROJECT_ID,
        "device": device,
        "device_health": dhealth,
        "counts": by,
        "app_count": len(apps),
        "findings": findings,
        "severity_points": severity,
        "scores": {"apps": app_score, "device": dhealth["score"], "overall": overall},
        "ok": by["error"] == 0 and "not_encrypted" not in dhealth["issues"],
        "disclaimer": "Analyzes provided inventory JSON only — does not modify a phone, root, or run ADB.",
        "watermark": WATERMARK,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
