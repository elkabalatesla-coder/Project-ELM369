"""Dry-run model training planner for ELM369."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REGISTRY = Path("data/registries/elm369_model_training.json")
STORE = Path("tools/elm_model_training/data/plans.jsonl")
PROJECT_ID = "ELM369_JMR08241978202646902"
WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_registry(path: Path | None = None) -> dict[str, Any]:
    source = path or REGISTRY
    return json.loads(source.read_text(encoding="utf-8"))


def catalog(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    reg = registry or load_registry()
    profiles = reg.get("profiles") or []
    return {
        "project_id": PROJECT_ID,
        "registry_version": reg.get("version"),
        "lifecycle": reg.get("lifecycle") or [],
        "guardrails": reg.get("guardrails") or [],
        "profiles": [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "default_mode": p.get("default_mode"),
                "risk_tier_default": p.get("risk_tier_default"),
            }
            for p in profiles
        ],
        "training_enabled": False,
        "note": "Planner only — no live training, fine-tuning, deployment, or provider calls.",
        "watermark": WATERMARK,
    }


def plan(
    objective: str,
    *,
    profile: str = "rag_copilot",
    dataset: str = "unspecified",
    mode: str | None = None,
    owner: str = "ai_product_owner",
    risk_tier: str | None = None,
) -> dict[str, Any]:
    reg = load_registry()
    profiles = {str(p.get("id")): p for p in reg.get("profiles") or []}
    selected = profiles.get(profile)
    if not selected:
        return {
            "ok": False,
            "error": "unknown_profile",
            "profile": profile,
            "available_profiles": sorted(profiles),
            "training_enabled": False,
        }

    requested_mode = (mode or str(selected.get("default_mode") or "plan")).strip()
    plan_row = {
        "ok": True,
        "plan_id": str(uuid.uuid4()),
        "project_id": PROJECT_ID,
        "registry_version": reg.get("version"),
        "objective": (objective or "").strip(),
        "profile": selected.get("id"),
        "profile_name": selected.get("name"),
        "dataset": dataset,
        "owner": owner,
        "risk_tier": risk_tier or selected.get("risk_tier_default"),
        "mode": requested_mode,
        "lifecycle": list(reg.get("lifecycle") or []),
        "guardrails": list(reg.get("guardrails") or []),
        "required_artifacts": list(reg.get("required_artifacts") or []),
        "core_algorithms": list(selected.get("core_algorithms") or []),
        "evaluation_requirements": list(selected.get("evaluation_requirements") or []),
        "training_enabled": False,
        "deployment_enabled": False,
        "note": "Dry-run planning only. Use this output to prepare datasets, evaluations, and approvals before any future external training workflow.",
        "created_at": _now(),
        "watermark": WATERMARK,
    }
    _append(plan_row)
    return plan_row


def list_plans(limit: int = 20) -> list[dict[str, Any]]:
    if not STORE.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in STORE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _append(row: dict[str, Any]) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    with STORE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
