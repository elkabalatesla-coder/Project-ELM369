"""Immutable secondary spatial index for canonical PCC ledger blocks.

The index stores references (height, block_id, block_hash), never canonical
Block objects. Queries resolve references against the caller's canonical chain
and fail closed when the index no longer matches that chain.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from types import MappingProxyType
import re
from typing import Mapping, Sequence

from .models import Block

SpatialKey = tuple[int, int, int, int]
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class StaleSpatialIndexError(RuntimeError):
    """Raised when a secondary index no longer matches its canonical ledger."""


@dataclass(frozen=True, slots=True)
class SpatialReference:
    height: int
    block_id: str
    block_hash: str
    key: SpatialKey

    def __post_init__(self) -> None:
        if isinstance(self.height, bool) or not isinstance(self.height, int) or self.height < 0:
            raise ValueError("spatial reference height must be a non-negative integer")
        if not isinstance(self.block_id, str) or not self.block_id:
            raise ValueError("spatial reference block_id must be non-empty")
        if not isinstance(self.block_hash, str) or not _HASH_RE.fullmatch(self.block_hash):
            raise ValueError("spatial reference block_hash must be a 32-byte lowercase digest")
        if (not isinstance(self.key, tuple) or len(self.key) != 4
                or any(isinstance(v, bool) or not isinstance(v, int) for v in self.key)):
            raise ValueError("spatial reference key must contain four integers")


@dataclass(frozen=True, slots=True)
class SpatialIndex:
    bucket_size_microunits: int
    ledger_length: int
    buckets: Mapping[SpatialKey, tuple[SpatialReference, ...]]

    def __post_init__(self) -> None:
        size = self.bucket_size_microunits
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("bucket_size_microunits must be a positive integer")
        if isinstance(self.ledger_length, bool) or not isinstance(self.ledger_length, int) or self.ledger_length < 0:
            raise ValueError("ledger_length must be a non-negative integer")
        frozen = {}
        for key, refs in self.buckets.items():
            if (not isinstance(key, tuple) or len(key) != 4
                    or any(isinstance(v, bool) or not isinstance(v, int) for v in key)):
                raise ValueError("bucket keys must contain four integers")
            if not isinstance(refs, tuple) or not all(isinstance(ref, SpatialReference) for ref in refs):
                raise ValueError("bucket values must be tuples of SpatialReference")
            if any(ref.key != key for ref in refs):
                raise ValueError("each spatial reference must match its containing bucket key")
            frozen[key] = tuple(refs)
        object.__setattr__(self, "buckets", MappingProxyType(frozen))

    @staticmethod
    def _coordinates(block: Block) -> tuple[int, int, int, int]:
        return (
            block.x_microunits,
            block.y_microunits,
            block.z_microunits,
            block.w_microunits,
        )

    def key_for_coordinates(
        self, x_microunits: int, y_microunits: int,
        z_microunits: int, w_microunits: int,
    ) -> SpatialKey:
        values = (x_microunits, y_microunits, z_microunits, w_microunits)
        if any(isinstance(v, bool) or not isinstance(v, int) for v in values):
            raise TypeError("spatial coordinates must be integer microunits")
        size = self.bucket_size_microunits
        return tuple(v // size for v in values)  # type: ignore[return-value]

    @classmethod
    def build(
        cls, canonical_blocks: Sequence[Block],
        bucket_size_microunits: int = 1_000_000,
    ) -> "SpatialIndex":
        from .validation import validate_chain

        blocks = tuple(canonical_blocks)
        result = validate_chain(blocks)
        if not result.valid:
            raise ValueError("cannot index an invalid canonical chain: " + "; ".join(result.errors))

        size_probe = cls(
            bucket_size_microunits=bucket_size_microunits,
            ledger_length=len(blocks),
            buckets={},
        )
        mutable: dict[SpatialKey, list[SpatialReference]] = defaultdict(list)

        for block in blocks:
            key = size_probe.key_for_coordinates(*cls._coordinates(block))
            mutable[key].append(SpatialReference(
                height=block.height,
                block_id=block.block_id,
                block_hash=block.block_hash,
                key=key,
            ))

        return cls(
            bucket_size_microunits=bucket_size_microunits,
            ledger_length=len(blocks),
            buckets={key: tuple(refs) for key, refs in mutable.items()},
        )

    def references_for_key(self, key: SpatialKey) -> tuple[SpatialReference, ...]:
        if not isinstance(key, tuple) or len(key) != 4:
            raise TypeError("spatial key must be a four-integer tuple")
        if any(isinstance(v, bool) or not isinstance(v, int) for v in key):
            raise TypeError("spatial key components must be integers")
        return self.buckets.get(key, ())

    def assert_current(self, canonical_blocks: Sequence[Block]) -> bool:
        from .validation import validate_chain

        blocks = tuple(canonical_blocks)
        result = validate_chain(blocks)
        if not result.valid:
            raise StaleSpatialIndexError(
                "canonical chain failed integrity validation: " + "; ".join(result.errors)
            )
        if len(blocks) != self.ledger_length:
            raise StaleSpatialIndexError(
                f"ledger length changed: indexed={self.ledger_length}, current={len(blocks)}"
            )

        refs_by_height: dict[int, SpatialReference] = {}
        for bucket_key, refs in self.buckets.items():
            for ref in refs:
                if ref.key != bucket_key:
                    raise StaleSpatialIndexError("reference is stored under the wrong bucket key")
                if ref.height in refs_by_height:
                    raise StaleSpatialIndexError(f"duplicate spatial reference at height {ref.height}")
                refs_by_height[ref.height] = ref

        if len(refs_by_height) != self.ledger_length:
            raise StaleSpatialIndexError("spatial index is incomplete or contains extra references")

        for height, block in enumerate(blocks):
            ref = refs_by_height.get(height)
            if ref is None:
                raise StaleSpatialIndexError(f"missing spatial reference for height {height}")
            expected_key = self.key_for_coordinates(*self._coordinates(block))
            if (
                ref.block_id != block.block_id
                or ref.block_hash != block.block_hash
                or ref.key != expected_key
            ):
                raise StaleSpatialIndexError(f"spatial reference is stale at height {height}")

        return True

    def lookup_key(
        self, key: SpatialKey, canonical_blocks: Sequence[Block],
    ) -> tuple[Block, ...]:
        blocks = tuple(canonical_blocks)
        self.assert_current(blocks)
        refs = self.references_for_key(key)
        return tuple(blocks[ref.height] for ref in refs)

    def lookup_coordinates(
        self, x_microunits: int, y_microunits: int,
        z_microunits: int, w_microunits: int,
        canonical_blocks: Sequence[Block],
    ) -> tuple[Block, ...]:
        key = self.key_for_coordinates(
            x_microunits, y_microunits, z_microunits, w_microunits
        )
        return self.lookup_key(key, canonical_blocks)
