"""Load auto-evolution policy from schemas/evolution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_POLICY = Path("schemas/evolution/auto-evolution-policy.json")

LIFECYCLE = [
    "DISCOVERED",
    "PROPOSED",
    "SANDBOX",
    "TESTING",
    "VALIDATING",
    "CANARY",
    "APPROVED",
    "DEPLOYED",
    "MONITORED",
    "PROMOTED",
]

# Terminal / failure states from the spec
FAILURE_STATES = {"REJECTED", "QUARANTINED", "ROLLED_BACK", "DEPRECATED", "ARCHIVED"}

# Stages that require explicit authorization before advancement
AUTH_REQUIRED_FROM = {"VALIDATING", "CANARY", "APPROVED"}


def load_policy(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_POLICY
    if not p.is_file():
        return {
            "policy_id": "ELM369-POL-AUTO-EVOLUTION-001",
            "project_id": "ELM369_JMR08241978202646902",
            "gates": [
                "snapshot",
                "schema_validation",
                "unit_tests",
                "security_validation",
                "safety_validation",
                "provenance",
                "rollback_available",
                "authorization",
            ],
            "lifecycle": LIFECYCLE,
            "safety_boundary": {
                "production_mutation": "gated",
                "destructive_change": "authorized_only",
                "credential_change": "authorized_only",
            },
        }
    return json.loads(p.read_text(encoding="utf-8"))
