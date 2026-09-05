"""QBIT-gated self-heal proposals (never auto-apply to production)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.elm_orchestrator.agents import PROJECT_ID, vault_log
from tools.qbit import compute_qstate, recommend

STORE = Path("tools/elm_orchestrator/data/heal_proposals.jsonl")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _score_issue(issue: str) -> dict[str, Any]:
    """Heuristic evidence scores — explicit, inspectable, never override hard gates."""
    text = (issue or "").lower()
    # Likelihood of safe additive fix
    L = 0.75
    # Measured evidence present
    M = 0.55 if any(k in text for k in ("test", "fail", "ci", "error", "missing")) else 0.4
    # Reversibility / additive
    R = 0.85 if any(k in text for k in ("add", "doc", "scaffold", "test", "coverage")) else 0.5
    # Harm if wrong
    H = 0.2 if any(k in text for k in ("delete", "credential", "secret", "prod", "force")) else 0.55
    hard_block = any(k in text for k in ("credential", "secret", "password", "token rotate bypass"))
    needs_auth = True  # heal always needs authorization
    q = compute_qstate(L, M, R, H)
    rec = recommend(q, hard_block=hard_block, needs_authorization=needs_auth)
    return {
        "L": L,
        "M": M,
        "R": R,
        "H": H,
        "qstate": q,
        "recommendation": rec,
        "hard_block": hard_block,
    }


def propose(issue: str) -> dict[str, Any]:
    scored = _score_issue(issue)
    proposal_id = str(uuid.uuid4())
    proposal = {
        "proposal_id": proposal_id,
        "agent": "ELM369-QBIT-REPAIR-02",
        "project_id": PROJECT_ID,
        "issue": issue,
        "proposed_at": _now(),
        "qbit": scored,
        "actions": [
            "snapshot current state",
            "generate additive patch candidate",
            "run unit tests in sandbox",
            "REQUEST_AUTHORIZATION before apply",
        ],
        "auto_apply": False,
        "safety": "authorized_only",
        "status": "proposed",
    }
    STORE.parent.mkdir(parents=True, exist_ok=True)
    with STORE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(proposal, ensure_ascii=False) + "\n")
    vault_log("heal_proposal", {"proposal_id": proposal_id, "issue": issue, "qbit": scored})
    return proposal


def list_proposals(limit: int = 20) -> list[dict[str, Any]]:
    if not STORE.exists():
        return []
    rows = []
    for line in STORE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def simulate_apply(proposal_id: str, *, authorize: bool = False) -> dict[str, Any]:
    """Dry-run apply: records intent only. Never mutates production files."""
    rows = list_proposals(limit=10_000)
    match = next((r for r in reversed(rows) if r.get("proposal_id") == proposal_id), None)
    if not match:
        return {"ok": False, "error": "proposal_not_found", "proposal_id": proposal_id}
    if match.get("qbit", {}).get("hard_block"):
        return {"ok": False, "error": "hard_block", "proposal_id": proposal_id, "auto_apply": False}
    if not authorize:
        return {
            "ok": False,
            "error": "authorization_required",
            "proposal_id": proposal_id,
            "hint": "Pass --authorize for dry-run simulation only; still does not mutate production.",
            "auto_apply": False,
        }
    result = {
        "ok": True,
        "proposal_id": proposal_id,
        "status": "simulated_apply",
        "applied_at": _now(),
        "mutated_production": False,
        "note": "Dry-run only — no files changed. Real apply remains human-gated.",
        "issue": match.get("issue"),
        "qbit": match.get("qbit"),
    }
    vault_log("heal_simulate_apply", result)
    return result
