"""Identity resolution + security registry scaffold for Project ELM369."""

from __future__ import annotations

import json
from hashlib import sha256
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ID = "ELM369_JMR08241978202646902"
PROJECT_NAME = "ELM369"
CANONICAL_ID = "JMR0824197846902"
COMPANION_ID = "JMR08241978202646902"
RELATIONSHIP = "companion -> project"
REGISTRY = Path(__file__).resolve().parents[2] / "data/registries/elm369_security_tools.json"
OBJECT_TYPES = [
    "Identity",
    "Asset",
    "User",
    "Device",
    "Service",
    "Repository",
    "Package",
    "Dependency",
    "Artifact",
    "Model",
    "Dataset",
    "Prompt",
    "Agent",
    "Tool",
    "Credential",
    "NetworkFlow",
    "Event",
    "Alert",
    "Vulnerability",
    "Threat",
    "Control",
    "Policy",
    "Finding",
    "Incident",
    "Evidence",
    "Authorization",
    "Remediation",
    "ProvenanceRecord",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_identifier(value: str) -> str:
    return "".join(str(value or "").split()).upper()


def load_registry(path: Path | None = None) -> dict[str, Any]:
    target = path or REGISTRY
    return json.loads(target.read_text(encoding="utf-8"))


def _capability_key(value: str) -> str:
    return str(value or "").strip().lower()


def _filter_security_tools(
    data: dict[str, Any],
    *,
    required_for: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    required_key = _capability_key(required_for or "")
    category_key = str(category or "").strip().lower()
    rows: list[dict[str, Any]] = []
    for row in data.get("tools") or []:
        reqs = [_capability_key(item) for item in row.get("required_for") or []]
        row_category = str(row.get("category") or "").lower()
        if required_key and required_key not in reqs:
            continue
        if category_key and category_key != row_category:
            continue
        normalized = dict(row)
        normalized["required_for"] = reqs
        rows.append(normalized)
    return rows


def _registry_summary_from_data(data: dict[str, Any]) -> dict[str, Any]:
    tools = data.get("tools") or []
    categories: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for row in tools:
        categories[row.get("category") or "unknown"] = categories.get(row.get("category") or "unknown", 0) + 1
        by_status[row.get("status") or "unknown"] = by_status.get(row.get("status") or "unknown", 0) + 1
    return {
        "project_id": data.get("project_id") or PROJECT_ID,
        "security_object_types": data.get("security_object_types") or OBJECT_TYPES,
        "tool_count": len(tools),
        "categories": categories,
        "by_status": by_status,
        "identity": data.get("identity") or {},
        "ok": bool(tools),
    }


def _identity_record(identifier: str, *, role: str, observed_at: str, source: str) -> dict[str, Any]:
    return {
        "object_id": f"{PROJECT_NAME}-IDENTITY-{role.upper()}",
        "object_type": "Identity",
        "object_type_allowed": "Identity" in OBJECT_TYPES,
        "owner": PROJECT_NAME,
        "source": source,
        "source_timestamp": observed_at,
        "observed_timestamp": observed_at,
        "confidence": 1.0,
        "integrity_hash": f"sha256:{sha256(identifier.encode('utf-8')).hexdigest()}",
        "parent_id": PROJECT_ID,
        "dependencies": [],
        "classification": role,
        "risk": "low",
        "status": "VERIFIED",
        "provenance": {
            "record_id": f"prov:{PROJECT_NAME.lower()}:{role}",
            "identifier": identifier,
            "relationship": RELATIONSHIP if role == "companion" else "canonical_anchor",
            "merge": "forbidden_unless_explicitly_authorized",
        },
        "authorization_state": "required_for_merge",
    }


def resolve_identity(
    identifiers: list[str] | tuple[str, ...] | None = None,
    *,
    project_id: str = PROJECT_ID,
    source: str = "elm_security",
    observed_at: str | None = None,
) -> dict[str, Any]:
    timestamp = observed_at or _now()
    provided = list(identifiers or [CANONICAL_ID, COMPANION_ID])
    normalized = [_normalize_identifier(value) for value in provided if str(value or "").strip()]

    canonical_present = CANONICAL_ID in normalized
    companion_present = COMPANION_ID in normalized
    conflated = CANONICAL_ID == COMPANION_ID
    provenance_map = {
        "canonical": _identity_record(CANONICAL_ID, role="canonical", observed_at=timestamp, source=source),
        "companion": _identity_record(COMPANION_ID, role="companion", observed_at=timestamp, source=source),
    }
    distinct_provenance = (
        provenance_map["canonical"]["provenance"]["record_id"]
        != provenance_map["companion"]["provenance"]["record_id"]
    )
    ok = canonical_present and companion_present and distinct_provenance and not conflated

    return {
        "project_id": project_id,
        "identity_function": "IDENTITY_RESOLUTION",
        "input": {"project_id": project_id, "identifiers": provided},
        "resolved_identity": {
            "project": PROJECT_NAME,
            "canonical": CANONICAL_ID,
            "companion": COMPANION_ID,
            "relationship": RELATIONSHIP,
            "merge": "forbidden unless explicitly authorized",
        },
        "anchor_map": {
            "canonical_anchor": CANONICAL_ID,
            "companion_id": COMPANION_ID,
            "project_id": project_id,
        },
        "provenance_map": provenance_map,
        "integrity_status": {
            "ok": ok,
            "canonical_identifier_exists": canonical_present,
            "companion_identifier_exists": companion_present,
            "identifiers_silently_conflated": conflated,
            "provenance_distinct": distinct_provenance,
        },
    }


def list_security_tools(
    *,
    required_for: str | None = None,
    category: str | None = None,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    return _filter_security_tools(load_registry(path), required_for=required_for, category=category)


def registry_summary(*, path: Path | None = None) -> dict[str, Any]:
    return _registry_summary_from_data(load_registry(path))


def build_security_posture(*, registry_path: Path | None = None) -> dict[str, Any]:
    data = load_registry(registry_path)
    registry = _registry_summary_from_data(data)
    identity = resolve_identity()
    tools = _filter_security_tools(data)
    required_for = sorted(
        {
            capability
            for tool in tools
            for capability in (tool.get("required_for") or [])
        }
    )
    return {
        "project_id": PROJECT_ID,
        "checked_at": _now(),
        "ok": bool(registry.get("ok")) and bool(identity.get("integrity_status", {}).get("ok")),
        "identity": identity,
        "registry": registry,
        "required_capabilities": required_for,
    }


def safe_security_posture(*, registry_path: Path | None = None) -> dict[str, Any]:
    try:
        return build_security_posture(registry_path=registry_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "project_id": PROJECT_ID,
            "checked_at": _now(),
            "ok": False,
            "error": str(exc),
            "identity": resolve_identity(),
            "registry": {
                "project_id": PROJECT_ID,
                "security_object_types": OBJECT_TYPES,
                "tool_count": 0,
                "categories": {},
                "by_status": {},
                "identity": {},
                "ok": False,
            },
            "required_capabilities": [],
        }
