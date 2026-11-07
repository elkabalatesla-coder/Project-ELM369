"""Non-destructive ELM369 PCC / PSYONIC integration package."""

from .canonical import canonical_json, hash_block, hash_transaction, seal_block
from .models import Block, Transaction
from .spatial_index import SpatialIndex, SpatialReference, StaleSpatialIndexError
from .validation import ChainValidation, validate_chain

__all__ = [
    "Block", "Transaction", "ChainValidation", "SpatialIndex",
    "SpatialReference", "StaleSpatialIndexError", "canonical_json",
    "hash_block", "hash_transaction", "seal_block", "validate_chain",
]

__version__ = "0.2.0"
