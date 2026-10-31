"""Explicit ELM369 identifier records; mapping does not merge provenance."""
from dataclasses import dataclass

CANONICAL_ID = "JMR0824197846902"
COMPANION_ID = "JMR08241978202646902"


@dataclass(frozen=True, slots=True)
class IdentifierRecord:
    identifier: str
    role: str
    provenance_key: str


IDENTIFIER_RECORDS = (
    IdentifierRecord(CANONICAL_ID, "canonical_project_anchor", "provenance:canonical:JMR0824197846902"),
    IdentifierRecord(COMPANION_ID, "companion_tracking_identifier", "provenance:companion:JMR08241978202646902"),
)

# Explicit lookup association only. The two records above remain distinct.
ANCHOR_MAP = {
    CANONICAL_ID: CANONICAL_ID,
    COMPANION_ID: CANONICAL_ID,
}


def resolve_project_anchor(identifier: str) -> str:
    try:
        return ANCHOR_MAP[identifier]
    except KeyError as exc:
        raise ValueError(f"unknown ELM369 identifier: {identifier}") from exc
