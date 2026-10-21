# ELM369 Integration Control Plane v0.1.0

**Status:** isolated development proposal on branch `copilot/elm369-integration-control-plane-v0-1`. This is not merged into `main` and does not replace existing files.

## Purpose

Provide a small, testable integration layer for identity resolution, dependency ordering, evidence-gated lifecycle transitions, append-only registry semantics, and hash-linked audit events. Existing subsystem implementations remain independent until adapter contracts and end-to-end tests are approved.

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
4. Register immutable artifact versions and content hashes.
5. Run lifecycle stages only with stage-specific evidence.
6. Require explicit authorization for canary, deploy, and promotion.
7. Record audit events in a verifiable hash chain.
8. Connect persistence/API adapters only after contracts are validated.
9. Run subsystem and end-to-end regression tests.
10. Produce a signed-off evidence report; do not mark complete based on documentation claims alone.

## Boundaries

- No production deployment, external filing, messaging, credentials, or device actuation.
- No edits to `main`, no merges, no destructive operations.
- Registry implementation in this package is in-memory reference code; durable storage and concurrent transaction semantics remain future work.
- Hash chains detect modification relative to retained hashes; they do not by themselves provide trusted timestamps, digital signatures, or external tamper-proof storage.
- Unit tests cover only this package. They do not prove the entire ELM369 project is integrated.
