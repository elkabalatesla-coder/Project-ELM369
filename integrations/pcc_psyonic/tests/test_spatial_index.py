from dataclasses import replace
import unittest

from integrations.pcc_psyonic.canonical import seal_block
from integrations.pcc_psyonic.models import Block, Transaction
from integrations.pcc_psyonic.spatial_index import (
    SpatialIndex, SpatialReference, StaleSpatialIndexError,
)
from integrations.pcc_psyonic.validation import ZERO_HASH


def make_tx(txid):
    return Transaction.from_payload(
        transaction_id=txid,
        created_at_utc="2026-10-31T12:00:00Z",
        issuer_id="spatial-test",
        payload={"value": 1},
    )


def make_block(height, previous_hash, txid, *, x=0, y=0, z=0, w=0, block_id=None):
    return seal_block(Block(
        schema_version=1,
        block_id=block_id or f"block-{height}",
        height=height,
        timestamp_utc=f"2026-10-31T12:00:{height:02d}Z",
        previous_hash=previous_hash,
        transactions=(make_tx(txid),),
        x_microunits=x,
        y_microunits=y,
        z_microunits=z,
        w_microunits=w,
    ))


def valid_chain():
    first = make_block(0, ZERO_HASH, "tx-0", x=100, y=100, z=0, w=0)
    second = make_block(1, first.block_hash, "tx-1", x=150, y=190, z=0, w=0)
    third = make_block(2, second.block_hash, "tx-2", x=1200, y=100, z=0, w=0)
    return (first, second, third)


class SpatialIndexTests(unittest.TestCase):
    def test_bucket_collisions_keep_all_references(self):
        chain = valid_chain()
        index = SpatialIndex.build(chain, bucket_size_microunits=1000)
        key = index.key_for_coordinates(100, 100, 0, 0)
        refs = index.references_for_key(key)
        self.assertEqual(len(refs), 2)
        self.assertTrue(all(isinstance(ref, SpatialReference) for ref in refs))
        self.assertEqual([ref.height for ref in refs], [0, 1])

    def test_lookup_resolves_original_canonical_records(self):
        chain = valid_chain()
        index = SpatialIndex.build(chain, bucket_size_microunits=1000)
        found = index.lookup_coordinates(100, 100, 0, 0, chain)
        self.assertEqual(len(found), 2)
        self.assertIs(found[0], chain[0])
        self.assertIs(found[1], chain[1])

    def test_index_stores_references_not_block_records(self):
        chain = valid_chain()
        index = SpatialIndex.build(chain, bucket_size_microunits=1000)
        flattened = [ref for bucket in index.buckets.values() for ref in bucket]
        self.assertEqual(len(flattened), len(chain))
        self.assertTrue(all(not hasattr(ref, "transactions") for ref in flattened))

    def test_append_makes_index_stale(self):
        chain = valid_chain()
        index = SpatialIndex.build(chain, bucket_size_microunits=1000)
        fourth = make_block(3, chain[-1].block_hash, "tx-3", x=2000)
        with self.assertRaises(StaleSpatialIndexError):
            index.lookup_coordinates(100, 100, 0, 0, chain + (fourth,))

    def test_modified_canonical_record_makes_index_stale(self):
        chain = valid_chain()
        index = SpatialIndex.build(chain, bucket_size_microunits=1000)
        changed = replace(chain[0], x_microunits=999)
        with self.assertRaises(StaleSpatialIndexError):
            index.lookup_coordinates(100, 100, 0, 0, (changed,) + chain[1:])

    def test_invalid_chain_cannot_be_indexed(self):
        chain = valid_chain()
        changed = replace(chain[0], x_microunits=101)
        with self.assertRaises(ValueError):
            SpatialIndex.build((changed,) + chain[1:])

    def test_negative_coordinates_use_floor_buckets(self):
        index = SpatialIndex(bucket_size_microunits=10, ledger_length=0, buckets={})
        self.assertEqual(index.key_for_coordinates(-1, -10, -11, 0), (-1, -1, -2, 0))

    def test_bucket_size_must_be_positive_integer(self):
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    SpatialIndex(bucket_size_microunits=value, ledger_length=0, buckets={})

    def test_bucket_mapping_is_immutable(self):
        index = SpatialIndex.build(valid_chain(), bucket_size_microunits=1000)
        key = next(iter(index.buckets))
        with self.assertRaises(TypeError):
            index.buckets[key] = ()


if __name__ == "__main__":
    unittest.main()
