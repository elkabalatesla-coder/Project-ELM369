"""Identity normalization with explicit preservation of identifier provenance.

Both JMR identifiers resolve to the canonical project anchor for routing, but
the submitted identifier and its role are retained as separate evidence.
This module does not rewrite existing repository identity records.
"""
from typing import Any, Dict

CANONICAL_ANCHOR = "JMR0824197846902"
COMPANION_ANCHOR = "JMR08241978202646902"
ANCHOR_MAP = {
    CANONICAL_ANCHOR: CANONICAL_ANCHOR,
    COMPANION_ANCHOR: CANONICAL_ANCHOR,
}
IDENTITY_ROLES = {
    CANONICAL_ANCHOR: "canonical",
    COMPANION_ANCHOR: "companion",
}


def resolve_identity(identifier: str, *, source_record_id: str,
                     provenance: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve an accepted anchor without discarding its original provenance."""
    if not isinstance(identifier, str) or identifier not in ANCHOR_MAP:
        raise ValueError("unknown_project_identifier")
    if not isinstance(source_record_id, str) or not source_record_id.strip():
        raise ValueError("source_record_id_required")
    if not isinstance(provenance, dict) or not provenance:
        raise ValueError("provenance_required")
    return {
        "canonical_anchor": ANCHOR_MAP[identifier],
        "submitted_identifier": identifier,
        "identifier_role": IDENTITY_ROLES[identifier],
        "source_record_id": source_record_id,
        "provenance": dict(provenance),
        "provenance_merge_permitted": False,
    }
