"""Evolution change proposals with QBIT gating and lifecycle advancement."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.elm_evolution.policy import AUTH_REQUIRED_FROM, FAILURE_STATES, LIFECYCLE, load_policy
from tools.qbit import compute_qstate, recommend

STORE = Path("tools/elm_evolution/data/changes.jsonl")
PROJECT_ID = "ELM369_JMR08241978202646902"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover(root: Path | None = None) -> dict[str, Any]:
    """DISCOVER: inventory key artifacts / tools present in the repo."""
    base = root or Path(".")
    findings = {
        "tools": sorted(p.name for p in (base / "tools").iterdir() if p.is_dir()) if (base / "tools").is_dir() else [],
        "schemas_evolution": (base / "schemas/evolution").is_dir(),
        "openapi": (base / "openapi/elm369-orchestrator.openapi.yaml").is_file(),
        "repo_map": (base / "docs/REPO_MAP.md").is_file(),
        "vault_grok": (base / "vault/ELM369/JMR08241978202646902/sources/grok").is_dir(),
        "policy": (base / "schemas/evolution/auto-evolution-policy.json").is_file(),
    }
    return {
        "stage": "DISCOVERED",
        "project_id": PROJECT_ID,
        "discovered_at": _now(),
        "findings": findings,
        "ok": bool(findings["tools"]) and findings["policy"],
    }


def _score(summary: str, operation: str) -> dict[str, Any]:
    text = f"{summary} {operation}".lower()
    L = 0.7
    M = 0.6 if any(k in text for k in ("test", "ci", "schema", "lint")) else 0.45
    R = 0.8 if operation in {"correct", "organize", "amend"} else 0.55
    H = 0.25 if any(k in text for k in ("delete", "credential", "force", "prod")) else 0.5
    hard = any(k in text for k in ("credential", "secret", "password", "physical"))
    q = compute_qstate(L, M, R, H)
    rec = recommend(q, hard_block=hard, needs_authorization=True)
    return {"L": L, "M": M, "R": R, "H": H, "qstate": q, "recommendation": rec, "hard_block": hard}


def propose(
    summary: str,
    *,
    operation: str = "amend",
    artifact: str = "",
) -> dict[str, Any]:
    """PROPOSE a versioned change — never mutates production."""
    policy = load_policy()
    ops = policy.get("operations") or {}
    if operation not in ops and ops:
        # still allow known ops from policy keys
        pass
    change_id = str(uuid.uuid4())
    scored = _score(summary, operation)
    change = {
        "change_id": change_id,
        "project_id": PROJECT_ID,
        "policy_id": policy.get("policy_id"),
        "operation": operation,
        "summary": summary,
        "artifact": artifact,
        "lifecycle": "PROPOSED",
        "gates_passed": ["snapshot", "provenance"],
        "gates_pending": [g for g in (policy.get("gates") or []) if g not in {"snapshot", "provenance"}],
        "qbit": scored,
        "auto_deploy": False,
        "production_mutation": False,
        "created_at": _now(),
        "updated_at": _now(),
        "history": [{"at": _now(), "to": "PROPOSED", "note": "created"}],
    }
    _append(change)
    return change


def list_changes(limit: int = 20) -> list[dict[str, Any]]:
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
    # latest record per change_id
    latest: dict[str, dict[str, Any]] = {}
    for r in rows:
        latest[str(r.get("change_id"))] = r
    return list(latest.values())[-limit:]


def advance(change_id: str, *, authorize: bool = False, reject: bool = False) -> dict[str, Any]:
    """Advance one lifecycle step (or reject). Never auto-deploys to production."""
    rows = _all_rows()
    match = next((r for r in reversed(rows) if r.get("change_id") == change_id), None)
    if not match:
        return {"ok": False, "error": "not_found", "change_id": change_id}
    if match.get("lifecycle") in FAILURE_STATES:
        return {"ok": False, "error": "terminal_state", "lifecycle": match["lifecycle"]}
    if reject:
        match = dict(match)
        match["lifecycle"] = "REJECTED"
        match["updated_at"] = _now()
        match.setdefault("history", []).append({"at": _now(), "to": "REJECTED", "note": "rejected"})
        match["production_mutation"] = False
        _append(match)
        return {"ok": True, "change": match}

    if match.get("qbit", {}).get("hard_block"):
        match = dict(match)
        match["lifecycle"] = "QUARANTINED"
        match["updated_at"] = _now()
        match.setdefault("history", []).append({"at": _now(), "to": "QUARANTINED", "note": "hard_block"})
        _append(match)
        return {"ok": False, "error": "hard_block", "change": match}

    cur = match.get("lifecycle", "PROPOSED")
    try:
        idx = LIFECYCLE.index(cur)
    except ValueError:
        return {"ok": False, "error": "unknown_lifecycle", "lifecycle": cur}

    if idx >= len(LIFECYCLE) - 1:
        return {"ok": True, "change": match, "note": "already_terminal_success"}

    nxt = LIFECYCLE[idx + 1]

    # Never silently enter DEPLOYED/PROMOTED without authorize
    if cur in AUTH_REQUIRED_FROM or nxt in {"DEPLOYED", "MONITORED", "PROMOTED", "APPROVED", "CANARY"}:
        if not authorize:
            return {
                "ok": False,
                "error": "authorization_required",
                "from": cur,
                "would_become": nxt,
                "hint": "Pass --authorize to advance past gated stages. Still records intent only; no file deploy.",
                "auto_deploy": False,
            }

    # Simulate gate checks for sandbox/testing stages
    match = dict(match)
    gates = list(match.get("gates_passed") or [])
    if nxt == "SANDBOX" and "schema_validation" not in gates:
        gates.append("schema_validation")
    if nxt == "TESTING" and "unit_tests" not in gates:
        gates.append("unit_tests")
    if nxt == "VALIDATING":
        for g in ("security_validation", "safety_validation", "rollback_available"):
            if g not in gates:
                gates.append(g)
    if authorize and "authorization" not in gates:
        gates.append("authorization")

    match["gates_passed"] = gates
    policy_gates = load_policy().get("gates") or []
    match["gates_pending"] = [g for g in policy_gates if g not in gates]
    match["lifecycle"] = nxt
    match["updated_at"] = _now()
    match["production_mutation"] = False  # this scaffold never mutates prod files
    match.setdefault("history", []).append({"at": _now(), "to": nxt, "note": "advanced", "authorized": authorize})
    if nxt in {"DEPLOYED", "PROMOTED"}:
        match["deploy_note"] = "Recorded lifecycle only — no production files were modified by this tool."
    _append(match)
    return {"ok": True, "change": match}


def _all_rows() -> list[dict[str, Any]]:
    if not STORE.exists():
        return []
    out = []
    for line in STORE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _append(row: dict[str, Any]) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    with STORE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
