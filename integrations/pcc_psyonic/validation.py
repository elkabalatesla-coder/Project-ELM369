"""Deterministic local chain-integrity checks (not a consensus implementation)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Sequence

from .canonical import hash_block
from .models import Block, Transaction, BLOCK_SCHEMA_VERSION, TRANSACTION_SCHEMA_VERSION

ZERO_HASH = "0" * 64
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class ChainValidation:
    valid: bool
    status: str
    errors: tuple[str, ...]
    blocks_checked: int
    transactions_checked: int


def _parse_utc(value: str) -> datetime:
    """Parse UTC-Z timestamps and compare instants, not lexical strings."""
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamp must be an RFC3339 UTC string ending in Z")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def validate_chain(blocks: Sequence[Block]) -> ChainValidation:
    """Validate chain structure and content hashes.

    PASS means structural/content integrity passed. It does not verify
    transaction signatures or implement a consensus protocol.
    """
    errors: list[str] = []
    tx_count = 0

    if not blocks:
        return ChainValidation(False, "FAIL", ("chain is empty",), 0, 0)

    seen_tx_ids: set[str] = set()
    seen_block_ids: set[str] = set()
    previous_timestamp: datetime | None = None
    previous_hash = ZERO_HASH

    for expected_height, block in enumerate(blocks):
        if not isinstance(block, Block):
            errors.append(f"item[{expected_height}] is not a Block")
            previous_hash = None
            previous_timestamp = None
            continue

        if (isinstance(block.schema_version, bool)
                or not isinstance(block.schema_version, int)
                or block.schema_version != BLOCK_SCHEMA_VERSION):
            errors.append(f"block[{expected_height}] unsupported schema version")

        if not isinstance(block.height, int) or isinstance(block.height, bool):
            errors.append(f"block[{expected_height}] height is not an integer")
        elif block.height != expected_height:
            errors.append(f"block[{expected_height}] height mismatch: found {block.height}")

        if not isinstance(block.block_id, str) or not block.block_id.strip():
            errors.append(f"block[{expected_height}] block_id is empty or invalid")
        elif block.block_id in seen_block_ids:
            errors.append(f"duplicate block_id: {block.block_id}")
        else:
            seen_block_ids.add(block.block_id)

        if not isinstance(block.previous_hash, str) or not _HASH_RE.fullmatch(block.previous_hash):
            errors.append(f"block[{expected_height}] previous_hash is malformed")
        if block.previous_hash != previous_hash:
            errors.append(f"block[{expected_height}] previous_hash mismatch")

        try:
            current_timestamp = _parse_utc(block.timestamp_utc)
        except (TypeError, ValueError):
            errors.append(f"block[{expected_height}] timestamp is invalid")
            current_timestamp = None

        if (current_timestamp is not None and previous_timestamp is not None
                and current_timestamp < previous_timestamp):
            errors.append(f"block[{expected_height}] timestamp is earlier than its predecessor")
        if current_timestamp is not None:
            previous_timestamp = current_timestamp

        if not isinstance(block.nonce, int) or isinstance(block.nonce, bool) or block.nonce < 0:
            errors.append(f"block[{expected_height}] nonce is invalid")

        if not block.block_hash:
            errors.append(f"block[{expected_height}] has no stored block_hash")
        elif not isinstance(block.block_hash, str) or not _HASH_RE.fullmatch(block.block_hash):
            errors.append(f"block[{expected_height}] stored block_hash is malformed")
        else:
            try:
                actual_hash = hash_block(block)
            except (TypeError, ValueError):
                errors.append(f"block[{expected_height}] hash material is invalid")
            else:
                if actual_hash != block.block_hash:
                    errors.append(f"block[{expected_height}] content hash mismatch")

        if not isinstance(block.transactions, tuple):
            errors.append(f"block[{expected_height}] transactions must be a tuple")
        else:
            for tx in block.transactions:
                if not isinstance(tx, Transaction):
                    errors.append(f"block[{expected_height}] contains a non-Transaction item")
                    continue
                tx_count += 1
                if (isinstance(tx.schema_version, bool)
                        or not isinstance(tx.schema_version, int)
                        or tx.schema_version != TRANSACTION_SCHEMA_VERSION):
                    errors.append(f"block[{expected_height}] transaction {tx.transaction_id} schema mismatch")
                if not isinstance(tx.transaction_id, str) or not tx.transaction_id:
                    errors.append(f"block[{expected_height}] transaction_id is invalid")
                elif tx.transaction_id in seen_tx_ids:
                    errors.append(f"duplicate transaction_id: {tx.transaction_id}")
                else:
                    seen_tx_ids.add(tx.transaction_id)

        previous_hash = block.block_hash if isinstance(block.block_hash, str) else None

    valid = not errors
    return ChainValidation(valid, "PASS" if valid else "FAIL",
                           tuple(errors), len(blocks), tx_count)
