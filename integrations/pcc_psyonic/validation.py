"""Deterministic local chain-integrity checks (not a consensus implementation)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .canonical import hash_block
from .models import Block, BLOCK_SCHEMA_VERSION, TRANSACTION_SCHEMA_VERSION

ZERO_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class ChainValidation:
    valid: bool
    status: str
    errors: tuple[str, ...]
    blocks_checked: int
    transactions_checked: int


def validate_chain(blocks: Sequence[Block]) -> ChainValidation:
    errors: list[str] = []
    tx_count = 0
    if not blocks:
        return ChainValidation(False, "FAIL", ("chain is empty",), 0, 0)

    seen_tx_ids: set[str] = set()
    previous_timestamp = ""
    previous_hash = ZERO_HASH
    for expected_height, block in enumerate(blocks):
        if not isinstance(block, Block):
            errors.append(f"item[{expected_height}] is not a Block")
            continue
        if block.schema_version != BLOCK_SCHEMA_VERSION:
            errors.append(f"block[{expected_height}] unsupported schema version")
        if block.height != expected_height:
            errors.append(f"block[{expected_height}] height mismatch: found {block.height}")
        if block.previous_hash != previous_hash:
            errors.append(f"block[{expected_height}] previous_hash mismatch")
        if previous_timestamp and block.timestamp_utc < previous_timestamp:
            errors.append(f"block[{expected_height}] timestamp is earlier than its predecessor")
        previous_timestamp = block.timestamp_utc
        if not block.block_hash:
            errors.append(f"block[{expected_height}] has no stored block_hash")
        elif hash_block(block) != block.block_hash:
            errors.append(f"block[{expected_height}] content hash mismatch")
        for tx in block.transactions:
            tx_count += 1
            if tx.schema_version != TRANSACTION_SCHEMA_VERSION:
                errors.append(f"block[{expected_height}] transaction {tx.transaction_id} schema mismatch")
            if tx.transaction_id in seen_tx_ids:
                errors.append(f"duplicate transaction_id: {tx.transaction_id}")
            seen_tx_ids.add(tx.transaction_id)
        previous_hash = block.block_hash
    valid = not errors
    return ChainValidation(valid, "PASS" if valid else "FAIL", tuple(errors), len(blocks), tx_count)
