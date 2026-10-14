# ELM369 Evidence-Based Status Model v1.0.0

## Allowed states
- PASS — acceptance criteria satisfied with inspectable evidence.
- FAIL — a check ran and did not satisfy its criterion.
- PARTIAL — some criteria are satisfied; remaining criteria are listed.
- UNKNOWN — not verified or evidence unavailable.
- N/A — not applicable, with rationale.
- ACCEPTED_RISK — authorized acceptance of a documented risk until a review date.

## Evidence record
Every task record includes task ID/title, status/rationale, acceptance criteria, evidence links or hashes, repository/branch/commit SHA, test command/result/timestamp/failure output, reviewer and authorization reference where required, dependencies/blockers, last verified timestamp, and next review date.

## Progress calculation
Progress = sum(weights of PASS criteria) / sum(weights of applicable criteria) × 100
Only verified PASS criteria count as complete. UNKNOWN, FAIL, and PARTIAL do not count as fully complete. N/A is excluded only with rationale. ACCEPTED_RISK is not PASS.
Report separate measures for architecture/specification, implementation, automated verification, security, and release readiness. Do not combine incomparable README estimates without documented reconciliation.

## Integrity anomaly policy
1. Preserve original claims and source references.
2. Record the conflict and detection timestamp.
3. Identify authoritative evidence required to resolve it.
4. Do not silently normalize identifiers, ownership roles, dates, or progress.
5. Record resolutions as new, versioned decisions.
