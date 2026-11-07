# ELM369 PCC / PSYONIC integration — v0.1.1

This package is a derived, non-destructive integration layer. It does not replace the original PCC source or alter the immutable ELM369 baseline.

## v0.1.1 integrity hardening

- Block and transaction schema versions remain explicitly versioned.
- Boolean values are rejected where integer schema, height, and nonce values are required.
- Transaction identity fields and consensus labels receive strict type validation.
- UTC chain chronology is checked as parsed timestamps, not lexicographically compared strings.
- Duplicate block identifiers and duplicate transaction identifiers are rejected.
- Tamper tests cover every block hash-material header field, transaction payload changes, previous-hash changes, timestamp regression, and malformed scalar types.

## Foundation carried forward from v0.1.0

- Frozen block and transaction models.
- Canonical JSON serialization with sorted keys, compact separators, UTF-8, and rejection of floating-point values.
- Domain-separated SHA3-256 transaction and block digests.
- Block hashing commits all integrity-relevant fields except the stored block_hash itself.
- Separate canonical and companion identifier provenance records with an explicit anchor lookup map.

## Explicit limitations

- PASS from validate_chain means structural and content-hash integrity only; it is not a consensus verdict.
- consensus_type and consensus_proof are committed into the block hash, but no consensus protocol or proof verifier is implemented.
- Transaction signatures are represented and hash-committed, but not cryptographically verified.
- The spatial index, AI-evidence attestation, quantum-simulation evidence, quantum-hardware evidence, Merkle checkpointing, witness controls, authority bridge, human-authorization gate, safety governor, and recovery controls remain unimplemented.
- Coordinates use integer microunits; no physical gyroscope interpretation or hardware stability certification is asserted.
- This is an integrity-focused prototype, not production cryptocurrency software.

## Run tests

From the repository root:

    python -m unittest discover -s integrations/pcc_psyonic/tests -v

## Identifier provenance

JMR0824197846902 is the canonical project anchor. JMR08241978202646902 is the companion tracking identifier. Both have separate immutable provenance keys. ANCHOR_MAP associates both with the canonical project anchor without merging their records.
