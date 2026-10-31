"""Canonical serialization and domain-separated SHA3-256 hashing."""
from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Any

BLOCK_HASH_DOMAIN = b"ELM369:PCC:BLOCK:v1\x00"
TRANSACTION_HASH_DOMAIN = b"ELM369:PCC:TRANSACTION:v1\x00"


def _reject_floats(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise TypeError(f"floating-point value prohibited in canonical material at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise TypeError(f"non-string object key at {path}")
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")
    elif value is not None and not isinstance(value, (str, bool, int)):
        raise TypeError(f"unsupported canonical value {type(value).__name__} at {path}")


def canonical_json(value: Any) -> str:
    """Serialize JSON-compatible data deterministically; floats are forbidden."""
    _reject_floats(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(domain: bytes, value: Any) -> str:
    encoded = canonical_json(value).encode("utf-8")
    return hashlib.sha3_256(domain + encoded).hexdigest()


def hash_transaction(transaction: Any) -> str:
    return _digest(TRANSACTION_HASH_DOMAIN, transaction.to_dict())


def hash_block(block: Any) -> str:
    return _digest(BLOCK_HASH_DOMAIN, block.hash_material())


def seal_block(block: Any):
    """Return a new immutable block with its content hash; never mutate input."""
    return replace(block, block_hash=hash_block(block))
