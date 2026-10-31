# ELM369 PCC / PSYONIC integration — v0.1.0

This package is a derived, non-destructive integration layer. It does not replace the original PCC source or alter the ELM369 baseline.

## Implemented in v0.1.0

- Versioned, frozen block and transaction data models.
- Canonical JSON serialization with sorted keys, compact separators, UTF-8, and rejection of floating-point values.
- Domain-separated SHA3-256 transaction and block digests.
- Block hashing covers all integrity-relevant fields except the stored \`block_hash\` itself.
- Local chain checks for schema version, height, previous-hash linkage, timestamp order, stored content hash, and duplicate transaction IDs.
- Separate canonical and companion identifier provenance records with an explicit project-anchor lookup map.

## Explicit limitations

- \`consensus_type\` and \`consensus_proof\` are committed into the block hash, but no consensus protocol or proof verifier is implemented in this version.
- Transaction signatures are represented but not cryptographically verified.
- No wallet, token issuance, network, mining, economic model, Merkle tree, spatial index, AI model attestation, quantum simulator, or quantum hardware integration is implemented.
- Coordinates use integer microunits; no physical gyroscope interpretation is asserted.
- This is an integrity-focused prototype, not production cryptocurrency software.

## Run tests

From the repository root:

\`\`\`bash
python -m unittest discover -s integrations/pcc_psyonic/tests -v
\`\`\`

## Identifier provenance

\`JMR0824197846902\` is the canonical anchor. \`JMR08241978202646902\` is a companion tracking identifier. Both have separate immutable provenance keys. \`ANCHOR_MAP\` associates both with the canonical project anchor without merging their records.
