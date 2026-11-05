# ELM369 Master Execution Plan v1.0.0

Status: Planning baseline — implementation and production status require verification
Canonical identifier: JMR0824197846902
Companion identifier: JMR08241978202646902
Canonical reference: ELM369-JMR0824197846902-JMR08241978202646902

## Integrity rules
1. Preserve canonical and companion identifiers as separate provenance records. Any mapping must be explicit and versioned; never silently merge, swap, or overwrite them.
2. Treat main as the protected baseline. This plan is maintained on a separate work branch.
3. No destructive changes, merges, renames, or replacements without explicit authorization.
4. A plan, specification, generated code, passing unit test, integration-tested service, and production deployment are different evidence levels.
5. A task is complete only with acceptance evidence, test results, status, and timestamp.
6. Never claim a license, charter, registration, insurance status, financial relationship, or production deployment exists without authoritative evidence.
7. Do not commit secrets, credentials, personal financial data, or unnecessary personal information.

## Baseline assessment
The supplied master program is a proposed work breakdown, not proof that every listed subsystem is absent or present. Inventory repository code and history before implementation. Extend existing functional components instead of duplicating them.
The root README reports approximately 70% weighted completion for a different set of conceptual technology categories. This is not directly comparable to the supplied platform program's 12% estimate. Keep both measures distinct until scope and formulas are reconciled through an auditable decision.

## Delivery sequence
### Phase 0 — Inventory and integrity baseline
- Inventory tracked files, directories, branches, workflows, tests, dependencies, and recent commits.
- Locate existing identity, registry, event, database, API, media, and translator implementations.
- Use PASS, FAIL, PARTIAL, UNKNOWN, N/A, or ACCEPTED_RISK for task states.
- Detect identifier conflicts, inconsistent identity-role mappings, missing ignore rules, leaked secrets, and unverified completion claims.
- Save a baseline manifest and checksums without rewriting existing artifacts.
Exit gate: inventory is reproducible, existing components point to evidence, and conflicts are logged.

### Phase 1 — Minimum viable platform core
1. Python package structure and dependency management.
2. Configuration and environment validation; no committed secrets.
3. Identity registry with explicit canonical-to-companion mapping.
4. Immutable baseline and append-only audit events.
5. Project/artifact registry with schema validation and SHA-256 digests.
6. API health/readiness endpoints and database migrations.
7. Unit tests, integration tests, static checks, and CI.
8. Local development environment using Docker Compose only after current environment requirements are confirmed.
Exit gate: clean setup works, migrations apply, core API tests pass, and identity/audit invariants are tested.

### Phase 2 — Security and governance
- Separate authentication from authorization; use default-deny and least privilege.
- Require explicit human approval for high-risk actions.
- Add input validation, secret scanning, dependency review, threat model, and audit-integrity checks.
- Exercise backup/restore and rollback.
- Define retention and privacy rules before storing personal or financial records.
Exit gate: threat model, automated checks, authorization tests, and restore evidence.

### Phase 3 — Registries and event backbone
- Project, ownership, artifact, agent, engine, workflow, knowledge, deployment, research, skill, and audit registries.
- Versioned schema contracts.
- Idempotency, bounded retries, dead-letter handling, and replay controls.
- Add Kafka, Redis, graph, or vector stores only when a demonstrated use case justifies their operational cost; keep adapters replaceable.
Exit gate: schema validation, duplicate-event protection, replay tests, and provenance checks pass.

### Phase 4 — Knowledge and AI platform
- Source-ingestion pipeline with provenance.
- Search/retrieval interfaces and versioned knowledge records.
- Supervisor/planning/research/evaluation interfaces behind policy gates.
- Tool routing with allowlists, timeouts, quotas, and auditable decisions.
- Evaluation datasets and regression tests before autonomous actions.
Exit gate: reproducible evaluations, source attribution, prompt-injection tests, and unsafe actuation disabled by default.

### Phase 5 — Product modules
Deliver media, gaming, command-center UI, and specialized director agents as separately versioned modules. Do not make every planned product a prerequisite for the platform core.
Exit gate: each module has requirements, tests, threat model, API contracts, and release criteria.

### Phase 6 — Release readiness
- Reproducible builds, versioned releases, SBOM, vulnerability review, backup/restore evidence, monitoring, incident procedures, and rollback.
- Production deployment is a separate approval gate; local tests do not imply deployment.
Exit gate: release evidence reviewed and production approval recorded.

## Sprint 1 — Recommended order
1. Inventory repository and confirm existing implementation.
2. Verify ignore rules, including virtual environments, without deleting existing files.
3. Establish package/test/CI baseline.
4. Implement or extend identifier and artifact registries.
5. Add append-only audit events and hash-linked evidence.
6. Confirm current ORM/database choices before creating models and migrations.
7. Add authentication/authorization after threat model and identity boundaries are defined.
8. Build a minimal dashboard after API contracts stabilize.

## Definition of Done
- Acceptance criteria are explicit.
- Code is present on the task branch.
- Unit tests pass; integration/API tests pass where applicable.
- Static/security checks are recorded.
- Audit and provenance are verified.
- Documentation and migration/rollback notes are present.
- Both identifier records are validated without provenance collapse.
- Evidence links and exact commit SHA are attached.
- No claim exceeds the evidence.

## Reporting
Include as-of timestamp, baseline commit, branch, tasks changed, allowed status states, test commands/results/CI links, blockers, integrity anomalies, remediation, and next verifiable milestone.
Do not infer progress from task count alone. Use weighted, evidence-backed acceptance criteria and publish the formula.
