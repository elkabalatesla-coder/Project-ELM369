# ELM369 Integration Findings v0.1.0

**Scope:** read-only review of existing repository records plus isolated control-plane development. This report does not modify or adjudicate the existing identity records.

## Identity/provenance findings

The inspected repository documents contain identifier roles that conflict with the canonical mapping specified for this integration work:

| Source | Repository text | Finding |
|---|---|---|
| `docs/ELM369_IDENTITY.md` | Operator id is `JMR08241978202646902` | Conflicts with the project canonical mapping |
| `docs/ELM369_COMPLETION_CERTIFICATE.json` | `project_id` uses `JMR08241978202646902`; `companion_vault` uses `JMR0824197846902` | Identifier roles appear reversed |
| `tools/elm_translator/README.md` | Vault uses `JMR08241978202646902`; companion uses `JMR0824197846902` | Identifier roles appear reversed |

Integration mapping for new records only:
- Canonical anchor: `JMR0824197846902`.
- Companion/alias: `JMR08241978202646902`.
- Both may route to the canonical anchor, but their submitted identifiers, roles, source-record IDs, and provenance must remain separate.
- No existing record is silently rewritten, merged, or deleted.

These findings are conflict flags, not a claim that the source documents have been corrected or that the records' authorship has been independently established.

## Registry implementation status

The control-plane registry currently provides in-memory registration, duplicate-ID rejection, content hashing, and verification. This iteration detaches nested JSON values on registration and retrieval to prevent caller mutation from silently changing stored records. It is not yet a persistent database-backed registry and does not provide concurrent transaction guarantees.

## Integration boundary

The control plane has unit tests and its own CI workflow. Existing subsystem tools are not yet connected through production adapters. Full project integration remains unverified until subsystem contracts, database persistence, API endpoints, translator STT/TTS, and end-to-end tests are implemented and passed.
