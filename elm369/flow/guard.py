"""ELM369 Flow - Continuity Guard (Tool 6, built first).

Local-only. No network. No credentials. No destructive ops.
Human gate required - never auto-approves.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

IDENTITY_THRESHOLD = 0.82
STYLE_THRESHOLD = 0.85
MOTION_THRESHOLD = 0.05
LIP_SYNC_MAX_MS = 40

def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def guard_hash_manifest(artifacts: list[str | Path]) -> dict:
    """Tool 6 - hash every artifact for provenance."""
    entries = []
    for a in artifacts:
        p = Path(a)
        entries.append({
            "path": str(p),
            "exists": p.exists(),
            "sha256": sha256_file(p) if p.exists() else None,
        })
    return {
        "tool": "ELM369 Continuity Guard",
        "version": "0.1.0",
        "count": len(entries),
        "entries": entries,
    }

def guard_check_all(report: dict) -> dict:
    """Check identity / style / motion drift. Pure math, no model needed."""
    identity = float(report.get("identity_score", 1.0))
    style = float(report.get("style_score", 1.0))
    motion = float(report.get("motion_deviation", 0.0))
    lip_ms = float(report.get("lip_sync_error_ms", 0))

    checks = {
        "identity": {"score": identity, "threshold": IDENTITY_THRESHOLD, "pass": identity >= IDENTITY_THRESHOLD},
        "style": {"score": style, "threshold": STYLE_THRESHOLD, "pass": style >= STYLE_THRESHOLD},
        "motion": {"score": motion, "threshold": MOTION_THRESHOLD, "pass": motion <= MOTION_THRESHOLD},
        "lip_sync": {"score_ms": lip_ms, "threshold_ms": LIP_SYNC_MAX_MS, "pass": lip_ms <= LIP_SYNC_MAX_MS},
    }
    failed = [k for k, v in checks.items() if not v["pass"]]
    return {
        "tool": "guard_check_all",
        "status": "PENDING_REVIEW" if not failed else "NOT_GRANTED",
        "failed_checks": failed,
        "checks": checks,
        "reason": "All checks passed - awaiting human gate." if not failed else f"Drift detected: {', '.join(failed)} - HUMAN_REVIEW_REQUIRED",
    }

def guard_human_gate(guard_report: dict, human_decision: str = "PENDING") -> dict:
    """Never auto-approve. Human must explicitly say APPROVED."""
    decision = human_decision.strip().upper()
    if guard_report.get("status") == "NOT_GRANTED":
        final = "NOT_GRANTED"
    elif decision == "APPROVED":
        final = "APPROVED"
    else:
        final = "PENDING_REVIEW"
    return {
        "tool": "guard_human_gate",
        "guard_status": guard_report.get("status"),
        "human_decision": decision,
        "final": final,
        "note": "ELM369 requires human review. No auto-approve.",
    }

def guard_full_run(artifacts: list[str | Path], scores: dict | None = None, human_decision: str = "PENDING") -> dict:
    manifest = guard_hash_manifest(artifacts)
    check = guard_check_all(scores or {})
    gate = guard_human_gate(check, human_decision)
    return {"manifest": manifest, "check": check, "gate": gate}

if __name__ == "__main__":
    demo = guard_full_run([], {"identity_score": 0.91, "style_score": 0.88, "motion_deviation": 0.02, "lip_sync_error_ms": 12})
    print(json.dumps(demo, indent=2))
