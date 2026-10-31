from dataclasses import replace
import unittest

from integrations.pcc_psyonic.canonical import canonical_json, hash_block, seal_block
from integrations.pcc_psyonic.models import Block, Transaction
from integrations.pcc_psyonic.provenance import ANCHOR_MAP, CANONICAL_ID, COMPANION_ID, IDENTIFIER_RECORDS
from integrations.pcc_psyonic.validation import ZERO_HASH, validate_chain


def tx(txid="tx-1", payload=None):
    return Transaction.from_payload(
        transaction_id=txid,
        created_at_utc="2026-10-31T12:00:00Z",
        issuer_id="test-issuer",
        payload=payload or {"amount_units": 100, "asset": "PSYC-TEST"},
    )


def genesis():
    return seal_block(Block(
        schema_version=1, block_id="block-0", height=0,
        timestamp_utc="2026-10-31T12:00:00Z", previous_hash=ZERO_HASH,
        transactions=(tx(),), nonce=0,
    ))


class CanonicalHashTests(unittest.TestCase):
    def test_key_order_does_not_change_canonical_json(self):
        self.assertEqual(canonical_json({"b": 2, "a": 1}), canonical_json({"a": 1, "b": 2}))

    def test_float_is_rejected(self):
        with self.assertRaises(TypeError):
            canonical_json({"unsafe": 0.1})

    def test_block_hash_is_deterministic(self):
        block = genesis()
        self.assertEqual(hash_block(block), block.block_hash)

    def test_coordinate_tampering_is_detected(self):
        block = genesis()
        changed = replace(block, x_microunits=1)
        result = validate_chain((changed,))
        self.assertFalse(result.valid)
        self.assertIn("content hash mismatch", " ".join(result.errors))

    def test_consensus_field_tampering_is_detected(self):
        block = genesis()
        changed = replace(block, consensus_proof="ALTERED")
        self.assertFalse(validate_chain((changed,)).valid)

    def test_valid_two_block_chain(self):
        first = genesis()
        second = seal_block(Block(
            schema_version=1, block_id="block-1", height=1,
            timestamp_utc="2026-10-31T12:00:01Z", previous_hash=first.block_hash,
            transactions=(tx("tx-2", {"amount_units": 250}),), nonce=7,
        ))
        result = validate_chain((first, second))
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(result.blocks_checked, 2)
        self.assertEqual(result.transactions_checked, 2)

    def test_previous_hash_tampering_is_detected(self):
        first = genesis()
        second = seal_block(Block(
            schema_version=1, block_id="block-1", height=1,
            timestamp_utc="2026-10-31T12:00:01Z", previous_hash=first.block_hash,
            transactions=(tx("tx-2"),),
        ))
        changed = replace(second, previous_hash=ZERO_HASH)
        self.assertFalse(validate_chain((first, changed)).valid)

    def test_duplicate_transaction_id_is_rejected(self):
        first = genesis()
        second = seal_block(Block(
            schema_version=1, block_id="block-1", height=1,
            timestamp_utc="2026-10-31T12:00:01Z", previous_hash=first.block_hash,
            transactions=(tx("tx-1"),),
        ))
        result = validate_chain((first, second))
        self.assertFalse(result.valid)
        self.assertTrue(any("duplicate transaction_id" in error for error in result.errors))

    def test_identifiers_have_separate_provenance_records(self):
        self.assertEqual(ANCHOR_MAP[CANONICAL_ID], CANONICAL_ID)
        self.assertEqual(ANCHOR_MAP[COMPANION_ID], CANONICAL_ID)
        self.assertNotEqual(IDENTIFIER_RECORDS[0].provenance_key, IDENTIFIER_RECORDS[1].provenance_key)


if __name__ == "__main__":
    unittest.main()
