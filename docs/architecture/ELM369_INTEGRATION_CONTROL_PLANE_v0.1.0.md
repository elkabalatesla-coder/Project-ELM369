# ELM369 Integration Control Plane v0.1.0

**Status:** isolated development proposal on branch `copilot/elm369-integration-control-plane-v0-1`. This is not merged into `main` and does not replace existing files.

## Purpose

Provide a small, testable integration layer for identity resolution, dependency ordering, evidence-gated lifecycle transitions, append-only registry semantics, hash-linked audit events, and an adapter for the repository's existing artifact catalog. Existing subsystem implementations remain independent until adapter contracts and end-to-end tests are approved.

## Identity and provenance

- Canonical anchor: `JMR0824197846902`.
- Companion identifier: `JMR08241978202646902`.
- Both resolve to the canonical anchor for routing.
- Each record retains its submitted identifier, role, source record ID, and provenance.
- Provenance merging is explicitly disabled. Existing contradictory records are flagged for review rather than silently rewritten.

## Integration sequence

1. Inventory subsystem entry points and data contracts.
2. Validate schemas and identity/provenance records.
3. Build a dependency DAG and reject missing nodes/cycles.
4. Import existing artifact catalog metadata into the control-plane registry.
5. Register immutable artifact versions and content hashes.
6. Run lifecycle stages only with stage-specific evidence.
7. Require explicit authorization for canary, deploy, and promotion.
8. Record audit events in a verifiable hash chain.
9. Connect persistent storage and API adapters only after contracts are validated.
10. Run subsystem and end-to-end regression tests and produce an evidence-backed status report.

## Boundaries

- No production deployment, external filing, messaging, credentials, or device actuation.
- No edits to `main`, no merges, no destructive operations.
- Registry implementation is in-memory reference code; durable storage and concurrent transaction semantics remain future work.
- The catalog adapter registers metadata only and does not claim to hash each artifact's actual bytes.
- Hash chains detect modification relative to retained hashes; they do not by themselves provide trusted timestamps, digital signatures, or external tamper-proof storage.
- Unit tests cover only this package. They do not prove the entire ELM369 project is integrated.
