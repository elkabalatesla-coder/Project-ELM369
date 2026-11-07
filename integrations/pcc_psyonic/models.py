"""Versioned, immutable data models for the derived PCC ledger layer.

Coordinates are integers in microunits; JSON floating-point values are
prohibited in hashed payloads to avoid cross-runtime serialization ambiguity.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any, Mapping

BLOCK_SCHEMA_VERSION = 1
TRANSACTION_SCHEMA_VERSION = 1
_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")


def _validate_utc(value: str, field: str) -> None:
    if not isinstance(value, str) or not _UTC_RE.fullmatch(value):
        raise ValueError(f"{field} must be an RFC3339 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid timestamp") from exc
    if parsed.tzinfo != timezone.utc:
        raise ValueError(f"{field} must use UTC")


def _validate_json_value(value: Any, path: str = "payload") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise TypeError(f"floating-point values are not permitted at {path}; use scaled integers or strings")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"JSON object keys must be strings at {path}")
            _validate_json_value(item, f"{path}.{key}")
        return
    raise TypeError(f"unsupported JSON value at {path}: {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class Transaction:
    schema_version: int
    transaction_id: str
    created_at_utc: str
    issuer_id: str
    payload_json: str
    signature_hex: str = ""

    def __post_init__(self) -> None:
        if (isinstance(self.schema_version, bool)
                or not isinstance(self.schema_version, int)
                or self.schema_version != TRANSACTION_SCHEMA_VERSION):
            raise ValueError("unsupported transaction schema_version")
        if (not isinstance(self.transaction_id, str) or not self.transaction_id.strip()
                or not isinstance(self.issuer_id, str) or not self.issuer_id.strip()):
            raise ValueError("transaction_id and issuer_id must be non-empty strings")
        if not isinstance(self.payload_json, str):
            raise TypeError("payload_json must be a string")
        _validate_utc(self.created_at_utc, "created_at_utc")
        try:
            payload = json.loads(self.payload_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("payload_json must contain valid JSON") from exc
        _validate_json_value(payload)
        from .canonical import canonical_json
        if self.payload_json != canonical_json(payload):
            raise ValueError("payload_json must already be canonical JSON")
        if (not isinstance(self.signature_hex, str)
                or (self.signature_hex and (
                    len(self.signature_hex) % 2 != 0
                    or not re.fullmatch(r"[0-9a-fA-F]+", self.signature_hex)
                ))):
            raise ValueError("signature_hex must be even-length hexadecimal when provided")

    @classmethod
    def from_payload(cls, *, transaction_id: str, created_at_utc: str,
                     issuer_id: str, payload: Mapping[str, Any],
                     signature_hex: str = "") -> "Transaction":
        from .canonical import canonical_json
        materialized = dict(payload)
        _validate_json_value(materialized)
        return cls(
            schema_version=TRANSACTION_SCHEMA_VERSION,
            transaction_id=transaction_id,
            created_at_utc=created_at_utc,
            issuer_id=issuer_id,
            payload_json=canonical_json(materialized),
            signature_hex=signature_hex,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "transaction_id": self.transaction_id,
            "created_at_utc": self.created_at_utc,
            "issuer_id": self.issuer_id,
            "payload": json.loads(self.payload_json),
            "signature_hex": self.signature_hex,
        }


@dataclass(frozen=True, slots=True)
class Block:
    schema_version: int
    block_id: str
    height: int
    timestamp_utc: str
    previous_hash: str
    transactions: tuple[Transaction, ...]
    nonce: int = 0
    consensus_type: str = "permissioned-prototype"
    consensus_proof: str = "UNVERIFIED"
    x_microunits: int = 0
    y_microunits: int = 0
    z_microunits: int = 0
    w_microunits: int = 0
    evidence_refs: tuple[str, ...] = ()
    block_hash: str = ""

    def __post_init__(self) -> None:
        if (isinstance(self.schema_version, bool)
                or not isinstance(self.schema_version, int)
                or self.schema_version != BLOCK_SCHEMA_VERSION):
            raise ValueError("unsupported block schema_version")
        if not isinstance(self.block_id, str) or not self.block_id.strip():
            raise ValueError("block_id must be a non-empty string")
        for name in ("height", "nonce"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if (not isinstance(self.consensus_type, str) or not self.consensus_type
                or not isinstance(self.consensus_proof, str) or not self.consensus_proof):
            raise ValueError("consensus_type and consensus_proof must be non-empty strings")
        _validate_utc(self.timestamp_utc, "timestamp_utc")
        if not isinstance(self.previous_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", self.previous_hash):
            raise ValueError("previous_hash must be a 32-byte lowercase hexadecimal digest")
        if not isinstance(self.transactions, tuple) or not all(isinstance(t, Transaction) for t in self.transactions):
            raise TypeError("transactions must be a tuple of Transaction objects")
        if not isinstance(self.evidence_refs, tuple) or not all(isinstance(x, str) and x for x in self.evidence_refs):
            raise TypeError("evidence_refs must be a tuple of non-empty strings")
        for name in ("x_microunits", "y_microunits", "z_microunits", "w_microunits"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer in microunits")
        if self.block_hash and (
            not isinstance(self.block_hash, str)
            or not re.fullmatch(r"[0-9a-f]{64}", self.block_hash)
        ):
            raise ValueError("block_hash must be a 32-byte lowercase hexadecimal digest")

    def hash_material(self) -> dict[str, Any]:
        """Return every integrity-relevant field except the stored block hash."""
        return {
            "schema_version": self.schema_version,
            "block_id": self.block_id,
            "height": self.height,
            "timestamp_utc": self.timestamp_utc,
            "previous_hash": self.previous_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "nonce": self.nonce,
            "consensus_type": self.consensus_type,
            "consensus_proof": self.consensus_proof,
            "coordinates_microunits": {
                "x": self.x_microunits, "y": self.y_microunits,
                "z": self.z_microunits, "w": self.w_microunits,
            },
            "evidence_refs": list(self.evidence_refs),
        }
