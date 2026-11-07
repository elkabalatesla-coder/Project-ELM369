from dataclasses import replace
import unittest

from integrations.pcc_psyonic.canonical import canonical_json, hash_block, seal_block
from integrations.pcc_psyonic.models import Block, Transaction
from integrations.pcc_psyonic.validation import ZERO_HASH, validate_chain


def tx(txid="tx-1", payload=None):
    return Transaction.from_payload(
        transaction_id=txid,
        created_at_utc="2026-10-31T12:00:00Z",
        issuer_id="test-issuer",
        payload=payload or {"amount_units": 100, "asset": "PSYC-TEST"},
    )


def make_block(*, block_id="block-0", height=0, timestamp="2026-10-31T12:00:00Z",
               previous_hash=ZERO_HASH, transactions=None, **kwargs):
    return seal_block(Block(
        schema_version=1, block_id=block_id, height=height,
        timestamp_utc=timestamp, previous_hash=previous_hash,
        transactions=(tx(),) if transactions is None else transactions,
        **kwargs,
    ))


class ValidationHardeningTests(unittest.TestCase):
    def test_canonical_key_order_and_float_rejection(self):
        self.assertEqual(canonical_json({"b": 2, "a": 1}), canonical_json({"a": 1, "b": 2}))
        with self.assertRaises(TypeError):
            canonical_json({"nested": [0.1]})

    def test_hash_commits_all_integrity_fields(self):
        block = make_block(evidence_refs=("ev-1",))
        mutations = [
            {"block_id": "block-x"},
            {"height": 1},
            {"timestamp_utc": "2026-10-31T12:00:01Z"},
            {"previous_hash": "1" * 64},
            {"nonce": 1},
            {"consensus_type": "alternate"},
            {"consensus_proof": "changed"},
            {"x_microunits": 1},
            {"y_microunits": 1},
            {"z_microunits": 1},
            {"w_microunits": 1},
            {"evidence_refs": ("ev-2",)},
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                changed = replace(block, **mutation)
                result = validate_chain((changed,))
                self.assertFalse(result.valid)
                self.assertIn("content hash mismatch", " ".join(result.errors))

    def test_transaction_payload_tampering_is_detected(self):
        block = make_block()
        changed_tx = tx(payload={"amount_units": 101, "asset": "PSYC-TEST"})
        changed_block = replace(block, transactions=(changed_tx,))
        result = validate_chain((changed_block,))
        self.assertFalse(result.valid)
        self.assertIn("content hash mismatch", " ".join(result.errors))

    def test_valid_two_block_chain(self):
        first = make_block()
        second = make_block(
            block_id="block-1", height=1,
            timestamp="2026-10-31T12:00:01Z",
            previous_hash=first.block_hash,
            transactions=(tx("tx-2", {"amount_units": 250}),),
        )
        result = validate_chain((first, second))
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(result.blocks_checked, 2)
        self.assertEqual(result.transactions_checked, 2)

    def test_timestamp_order_uses_instants_not_lexical_strings(self):
        first = make_block(timestamp="2026-10-31T12:00:00.100Z")
        second = make_block(
            block_id="block-1", height=1,
            timestamp="2026-10-31T12:00:00Z",
            previous_hash=first.block_hash,
            transactions=(tx("tx-2"),),
        )
        result = validate_chain((first, second))
        self.assertFalse(result.valid)
        self.assertTrue(any("timestamp is earlier" in e for e in result.errors))

    def test_duplicate_block_id_is_rejected(self):
        first = make_block(block_id="same")
        second = make_block(
            block_id="same", height=1,
            timestamp="2026-10-31T12:00:01Z",
            previous_hash=first.block_hash,
            transactions=(tx("tx-2"),),
        )
        result = validate_chain((first, second))
        self.assertFalse(result.valid)
        self.assertIn("duplicate block_id: same", result.errors)

    def test_previous_hash_tampering_is_detected(self):
        first = make_block()
        second = make_block(
            block_id="block-1", height=1,
            timestamp="2026-10-31T12:00:01Z",
            previous_hash=first.block_hash,
            transactions=(tx("tx-2"),),
        )
        changed = replace(second, previous_hash=ZERO_HASH)
        result = validate_chain((first, changed))
        self.assertFalse(result.valid)

    def test_duplicate_transaction_id_is_rejected(self):
        first = make_block()
        second = make_block(
            block_id="block-1", height=1,
            timestamp="2026-10-31T12:00:01Z",
            previous_hash=first.block_hash,
            transactions=(tx("tx-1"),),
        )
        result = validate_chain((first, second))
        self.assertFalse(result.valid)
        self.assertTrue(any("duplicate transaction_id" in e for e in result.errors))

    def test_empty_chain_fails(self):
        self.assertFalse(validate_chain(()).valid)

    def test_boolean_schema_version_is_rejected(self):
        with self.assertRaises(ValueError):
            Transaction(
                schema_version=True, transaction_id="tx-bool",
                created_at_utc="2026-10-31T12:00:00Z",
                issuer_id="issuer", payload_json="{}",
            )
        with self.assertRaises(ValueError):
            Block(
                schema_version=True, block_id="block-bool", height=0,
                timestamp_utc="2026-10-31T12:00:00Z", previous_hash=ZERO_HASH,
                transactions=(),
            )

    def test_boolean_height_and_nonce_are_rejected(self):
        with self.assertRaises(ValueError):
            make_block(height=True)
        with self.assertRaises(ValueError):
            make_block(nonce=True)

    def test_non_string_transaction_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            Transaction.from_payload(
                transaction_id=7, created_at_utc="2026-10-31T12:00:00Z",
                issuer_id="issuer", payload={"amount_units": 1},
            )

    def test_malformed_hash_types_are_rejected(self):
        with self.assertRaises(ValueError):
            make_block(previous_hash=None)
        with self.assertRaises(ValueError):
            Block(
                schema_version=1, block_id="bad-hash", height=0,
                timestamp_utc="2026-10-31T12:00:00Z",
                previous_hash=ZERO_HASH, transactions=(), block_hash=7,
            )


if __name__ == "__main__":
    unittest.main()
