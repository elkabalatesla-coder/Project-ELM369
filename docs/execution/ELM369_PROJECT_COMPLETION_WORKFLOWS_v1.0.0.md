# Project ELM369 — Project Completion Workflows v1.0.0

**Status:** Additive execution plan; no production or baseline changes  
**Review date:** 2026-11-11  
**Repository:** `elkabalatesla-coder/Project-ELM369`  
**Reviewed main:** `8b8fbfa95ed8b4ccbb7f1a39e2cdb670bc68dfd5`  
**Frozen baseline ref:** `baseline/jmr0824197846902`  
**Baseline commit:** `0812407e40b8d06fdee351f25be7ca96b0048ad1`  
**Canonical identifier:** `JMR0824197846902`  
**Companion identifier:** `JMR08241978202646902`

## 1. Purpose and change boundary

This plan consolidates the ELM369 discussions and the live GitHub repository into an ordered, evidence-driven completion program. It is designed to finish existing work before creating duplicate systems.

This document is an additive planning artifact. It does not modify `main`, the frozen baseline, historical vault records, identifiers, or existing workflows. It does not merge pull requests, deploy software, connect hardware, transmit data, or authorize financial, legal, credential, or physical actions.

The two JMR identifiers remain distinct provenance lineages. The crosswalk may associate them with one project for navigation; it must not merge their source histories or silently rewrite historical records.

## 2. Evidence rules

Use these states consistently:

- **VERIFIED:** directly confirmed by repository/API evidence or a reproducible test result.
- **IMPLEMENTED:** source/configuration exists, but runtime validation may still be pending.
- **TESTED:** named tests actually executed; preserve command, environment, commit, and result.
- **PARTIAL:** some acceptance criteria are satisfied.
- **PROPOSED:** design or plan only.
- **REPORTED:** a document or commit message claims completion, but independent evidence is absent.
- **UNKNOWN:** evidence is unavailable or insufficient.
- **ACCEPTED_RISK:** an authorized, documented decision to retain a known risk.
- **NOT_APPLICABLE:** explicitly outside the approved scope.

A branch name, commit message, completion percentage, manifest entry, passing unit test, or sandbox closeout statement is not by itself proof of production readiness. In particular, lifecycle advancement must never create evidence or mark a test passed unless the validator actually ran.

## 3. Repository review snapshot

### Verified GitHub facts

- Repository is public; default branch is `main`.
- The reviewed `main` commit is `8b8fbfa95ed8b4ccbb7f1a39e2cdb670bc68dfd5`.
- The frozen baseline branch points to `0812407e40b8d06fdee351f25be7ca96b0048ad1`; `main` is 78 commits ahead of it and has no reported commits behind it.
- The main tree contains 606 entries, 26 Python tool package directories, 26 test directories, and 18 GitHub Actions workflow files.
- The branch search returned 122 branch names across two pages.
- The repository contains separate vault directories for both JMR identifiers.
- The main branch includes Python tools for outage monitoring, daily automation, archive snapshots, artifacts, dashboard/status, evolution, orchestration, policy, memory, translation glossary, QBIT/QSTATE, offline operation, vault intake, and related functions.
- The integration-review branch `copilot/elm369-integration-review-2026-11` exists, but its inspected head is a November 5 completion-manifest commit; that commit is reported unsigned.
- The baseline branch and `main` are both reported unprotected. Required status checks are disabled on the inspected branch metadata.
- Issue #155 remains open. Issues #147, #148, #149, and #122 also remain open.

### Current limitations and inconsistencies

1. `README.md` reports approximately 70% overall completion without a reproducible calculation.
2. `docs/STATUS.md` is dated 2026-09-25 and reports a different registry-based measure (25 DONE, 1 SCAFFOLD, 88.3% average).
3. `docs/BACKLOG.md` is dated 2026-09-06 and does not reflect the current open workstream set.
4. Sandbox closure at 100%, tool-registry completion, implementation completion, and product/release readiness are separate measures. They must not be combined into one project percentage.
5. The current artifact verifier checks runnable-path existence and gallery existence; it does not verify file hashes, manifest byte counts, full file inventories, or archive integrity.
6. The archive snapshot utility's default paths do not include the vault tree and do not produce a per-file SHA-256 inventory. It is a selected-path snapshot, not a complete archive proof.
7. The current evolution engine can append gate names such as schema validation, unit tests, security validation, safety validation, and rollback availability during lifecycle advancement without executing those validators. Its proposal path also does not reject an unknown operation. It can label a lifecycle DEPLOYED/PROMOTED while explicitly recording that no production mutation occurred.
8. The evolution engine, identity documents, completion certificate, and vault README files contain inconsistent identifier-role labels. The explicit crosswalk exists on an open draft PR, not on `main`.
9. The public repository contains unnecessary personal identifying details in documentation and dated closeout material. Conduct a privacy exposure review. Do not quote, reproduce, or copy those details into new files. Any history remediation requires a separately authorized plan because Git history and public clones may retain prior content.
10. The fixed 13:00 UTC daily automation cron corresponds to different local clock times during daylight and standard time; its comments/status documentation should state the actual UTC schedule and seasonal local-time effect.
11. `pyproject.toml` declares Python >=3.8, while compatibility across the declared range has not been demonstrated. Select and test a supported matrix before changing the declaration.
12. The root Node package has no lockfile on `main`; reproducible Node dependency installation is therefore not established on the reviewed branch.

## 4. Priority findings

### P0 — Governance and safety

- Configure protection for `main` and the frozen baseline. Require pull requests, successful named CI checks, review, conversation resolution, and block force-push/deletion. The baseline should be stricter than normal development branches.
- Suspend or disable automatic merging until branch rules and required checks are active. The current `enable-automerge.yml` uses `pull_request_target`, grants pull-request write permission, and enables auto-merge for Dependabot or labelled PRs. Its current safety depends on branch protections that are not active in the inspected metadata.
- Correct evolution gate semantics: validators create evidence; the state machine only consumes evidence. Unknown or disabled operations must fail closed. A caller-supplied boolean must not be treated as proof of authenticated human authorization.
- Separate proposal, approval, deployment, monitoring, and promotion states. Do not label a simulated transition as a real deployment.
- Adopt the versioned identifier crosswalk as the rule for new records. Preserve conflicting historical records and append explicit amendments; do not rename or merge vault directories.
- Conduct privacy review of public repository content before publishing more archive material.

### P1 — Repository reliability and archive integrity

- Reconcile the overlapping CI and maintenance PRs (#115, #146, #153, #152) into one canonical CI design.
- Bring all active PR branches up to date with current `main` through reviewed rebase/cherry-pick; do not merge stale branches wholesale.
- Replace shallow artifact checks with canonical manifest validation and SHA-256 verification.
- Reconcile every archive and sandbox item against a complete inventory. Issue #155 stays open until its acceptance criteria are supported by evidence.
- Regenerate current status and backlog reports from repository facts and actual test results; retain historical snapshots unchanged.
- Validate packaging, Python support range, Node build/test/lint, and clean-install procedures.

### P2 — Core platform modules

- Complete AUDIO-TX with optional local STT/TTS adapters, glossary preservation, explicit no-network defaults, offline fallback, format validation, and device-specific tests.
- Consolidate motion/QBIT work around one engine-independent core; keep Godot/Unreal/device adapters separate.
- Implement ambient audio capture only after the complete recorder source and explicit device/privacy requirements are available.
- Stabilize the orchestrator, registry, event contracts, and audit/event backbone before adding more agent or UI layers.

### P3 — Product and research domains

- Treat facial recognition, audio recognition, multimodal sensor fusion, AR/VR/hologram projection, Unreal Qbit engines, the Unified AI Studio UI, and financial compliance as separate workstreams with their own specifications and acceptance tests.
- Keep quantum-inspired arithmetic and simulation explicitly distinct from execution on quantum hardware.
- Treat financial, licensing, regulatory, and charity-allocation logic as simulation/readiness features until reviewed against authoritative requirements and authorized integrations.

## 5. Workflows to finish ELM369

### WF-00 — Inventory and evidence baseline

**Inputs:** current main SHA, baseline SHA, all branches, open issues/PRs, repository tree, workflows, package manifests, registries, archives, sandbox manifests.

**Steps:**
1. Capture the exact commit SHA and UTC timestamp.
2. Inventory tracked files, directories, modules, tests, schemas, workflows, package manifests, branches, tags, issues, PRs, and releases.
3. Classify each asset by domain, identifier lineage, version, source, owner, dependencies, risk, and evidence status.
4. Compare manifests with actual tree entries; report missing and unregistered files.
5. Record conflicts as separate findings. Never silently normalize them.
6. Save a read-only inventory and hash manifest on a dedicated work branch.

**Exit criteria:** repeatable inventory; every discovered asset has a status; unknowns and conflicts are visible; no baseline changes.

### WF-01 — Identity, provenance, and authorization

**Steps:**
1. Adopt the explicit canonical/companion crosswalk for new records.
2. Preserve each source record's original identifier and lineage.
3. Add schema fields for canonical project ID, record ID, identifier role, source system, source record ID, artifact version, timestamps, content SHA-256, and authorization reference.
4. Require append-only amendments for historical corrections.
5. Separate identity authentication, role authorization, and human approval.
6. Require human approval for destructive, external, financial, credential, production, or physical actions.

**Tests:** duplicate-ID prevention; crosswalk round-trip; provenance retention; unauthorized operation denial; historical record immutability.

**Exit criteria:** conflicting identifiers are documented and navigable without history collapse; authorization is evidence-backed.

### WF-02 — GitHub branch and pull-request control

**Steps:**
1. Protect `main` and `baseline/jmr0824197846902`; do not use either as a work branch.
2. Require PR review and unique required status checks.
3. Require current-base validation before merge.
4. Disable auto-merge until the rules are active and verified.
5. Inventory branches into active, dependency, release, archival, superseded, or unknown.
6. Review PRs by dependency order; rebase/cherry-pick only after diff review.
7. Close a PR only with a reason and linked successor; do not delete branches automatically.

**Exit criteria:** every open PR has an owner/status/decision; no overlapping CI or module implementation is merged twice; main stays green.

### WF-03 — Unified CI, test, and packaging

**Python checks:**
- Determine supported Python versions from actual source and dependencies.
- Run compile checks, complete test discovery, schema/JSON validation, package installation, and CLI smoke tests.
- Execute all tool test directories, not only selected packages.
- Publish coverage and test artifacts with commit SHA and environment metadata.

**Node/TypeScript checks:**
- Add and verify a lockfile before using `npm ci`.
- Run build, lint, Jest, package smoke tests, and dependency audit on a documented Node matrix.

**Cross-project checks:**
- Validate OpenAPI and JSON schemas.
- Verify artifact manifests and SHA-256 digests.
- Test clean installation from a fresh environment.
- Fail closed if no tests are discovered or if a required check is skipped unexpectedly.

**Exit criteria:** one canonical CI policy; all required checks execute on PRs; merge is blocked on failure.

### WF-04 — Security and supply-chain controls

1. Set default workflow permissions to read-only and grant job-specific write scopes only when required.
2. Pin third-party actions to verified full commit SHAs or use verified dependency lockfiles.
3. Review every `pull_request_target` workflow and ensure untrusted PR code is never executed with privileged tokens.
4. Add CodeQL for supported languages, dependency review, Dependabot, secret scanning, and push protection where available.
5. Generate an SBOM for release packages.
6. Generate artifact attestations for release binaries/packages and verify attestations before publication.
7. Maintain threat models for AI tool routing, prompt/RAG inputs, archive ingestion, APIs, and device adapters.
8. Record findings and remediation evidence; do not describe an unconfigured security feature as active.

**Exit criteria:** least privilege, pinned workflow dependencies, vulnerability/dependency review, secret controls, SBOM, and release provenance are inspectable.

### WF-05 — Archive, vault, and sandbox reconciliation

**Steps:**
1. Inventory every path under `artifacts/`, `vault/`, `docs/grok_closeouts/`, and other archive locations.
2. Compare all files with `artifacts/sandboxes/manifest.json`, `ELM369_ARTIFACT_MANIFEST.json`, dated closeout manifests, and Git history.
3. Classify each item as source, derived artifact, runnable demo, test fixture, report, duplicate candidate, external dependency, or unknown.
4. Compute SHA-256 for every included file; store path, size, digest, version, source, and lineage.
5. Verify every referenced file exists and every manifest entry resolves.
6. Run safe artifact checks in an isolated environment; do not execute untrusted archive content automatically.
7. Mark duplicates as candidates only. Preserve originals unless a separately authorized disposition is recorded.
8. Update issue #155 only after every archive and sandbox item has a disposition and evidence.

**Exit criteria:** complete inventory; no hidden unclassified items; every hash verifies; issue #155 acceptance criteria are met or remaining external dependencies are explicitly listed.

### WF-06 — Evolution engine and controlled automation

**Required changes:**
- Reject unknown/disabled operations.
- Do not create `gates_passed` during state advancement.
- Require validator-produced evidence records with validator name/version, input commit/hash, timestamp, result, and evidence URI.
- Treat absent evidence as UNKNOWN/PENDING.
- Verify authorization references rather than accepting a bare boolean.
- Separate simulation status from actual deployment status.
- Make JSONL corruption visible; do not silently skip malformed records.
- Use stable paths independent of caller working directory.
- Add rollback proof and replay tests.

**Tests:** unknown operation; disabled operation; missing evidence; forged evidence; stale evidence; altered evidence; unauthorized deployment; malformed log line; replay; rollback.

**Exit criteria:** no lifecycle transition can manufacture a passing gate or imply a deployment that did not happen.

### WF-07 — AUDIO-TX

**Current main status:** phrase glossary only; no STT/TTS modules are present on main.

**Branch evidence:** PR #117 contains a more developed optional Vosk STT adapter and transcript-sidecar fallback. PR #125 contains a smaller adapter scaffold and execution plan. Both branches are behind current main and must not be merged as-is.

**Steps:**
1. Reconcile #117 and #125 into one reviewed implementation branch.
2. Keep glossary translation as the deterministic core.
3. Add optional local STT provider adapters; default to sidecar/manual transcript when no model is installed.
4. Add optional local TTS adapter; report text-only fallback explicitly and never claim audio was generated when it was not.
5. Add file-type, duration, size, sample-rate, channel-count, and language validation.
6. Add licensed audio fixtures and deterministic fake-provider tests.
7. Benchmark latency, accuracy, and memory on approved Android/Termux and Chromebook environments.
8. Keep cloud providers disabled unless separately authorized.

**Exit criteria:** offline tests pass; real provider tests are separately identified; glossary terms remain intact; no hidden network calls; no SMS/telephony.

### WF-08 — Motion, camera, and sensor fusion

**Branch evidence:** PR #141 contains a Python motion core and Godot 4 prototype; Godot parsing and on-device sensor behavior are not yet verified. PR #121 contains a separate simulation-only gyro matrix. PR #150 is a hardening branch based on the motion-core branch, not main.

**Steps:**
1. Consolidate motion math into a hardware-independent Python core.
2. Validate 4×4 transforms, quaternion integration, coordinate frames, units, timestamp handling, fixed-step replay, and numerical bounds.
3. Keep camera pose controls separate from camera capture.
4. Add sensor adapters for gyroscope, accelerometer, magnetometer, Hall sensor, and AprilTag only after interface contracts are defined.
5. Add calibration, drift, dropped-frame, stale-sensor, and uncertainty tests.
6. Validate Godot demo parsing and startup in a real Godot runtime.
7. Keep Unreal Engine adapters as separate future integrations; a Godot demo is not Unreal implementation.
8. Keep all physical actuation disabled until hardware-in-the-loop safety testing and human approval.

**Exit criteria:** deterministic simulation tests pass; adapters declare hardware/runtime support; no claim of real camera, facial recognition, or sensor operation without device evidence.

### WF-09 — Ambient audio and multimodal recognition

**Current evidence:** PR #154 is an additive draft specification. The reviewed recorder excerpt does not establish real microphone capture or captured-buffer playback; its tone generator is not recorded-audio playback.

**Steps:**
1. Obtain and version the complete source before repairing truncated code.
2. Separate browser UI, DSP, microphone capture, buffer storage, playback, and Unreal adapters.
3. Add explicit microphone permission and visible recording state.
4. Define retention, deletion, and local-processing defaults before storing audio.
5. Validate sample rates, channels, clipping, latency, buffer bounds, and playback semantics.
6. Treat facial/voice recognition as a separate privacy-sensitive module requiring consent, purpose limitation, retention rules, and false-match evaluation.
7. Keep ambient detection and classification as non-actuating advisory functions initially.

**Exit criteria:** source is complete; recording and playback are independently verified; privacy/safety review passes; no inference is treated as identity proof.

### WF-10 — Finance, compliance, and business readiness

**Current evidence:** the supplied conversation file reports an ELM369 Financial v1.1.0 P0–P3 build and 6/6 tests, but this build is not verified in the current main tree. No corresponding financial package was identified in the main tool-package inventory.

**Steps:**
1. Locate and inspect the exact archive/source for the reported v1.1.0 build.
2. Reconcile its P0–P3 claims with repository files and tests.
3. Keep identity, legal entity, regulatory registry, licensing, financial ledger, KYC/KYB, AML, payments, digital assets, tax, and risk functions separately versioned.
4. Use authoritative jurisdiction-specific sources for regulatory rules and record effective dates.
5. Keep ledger changes append-only and require double-entry/reconciliation tests.
6. Treat licensing, charter, insurance, banking, tax, and vendor relationships as UNKNOWN until authoritative records establish them.
7. Do not connect banking, move funds, submit filings, or represent legal status without explicit authorization and qualified review.

**Exit criteria:** reproducible source and tests; authoritative evidence for regulatory facts; clear simulation/production boundary; no unsupported claims of licensure or financial relationships.

### WF-11 — Release and operations

1. Select a version only after all applicable gates pass.
2. Build from a clean, pinned environment.
3. Produce package, SBOM, SHA-256 manifest, and artifact attestation.
4. Verify package contents and provenance independently.
5. Publish release notes with known limitations and external dependencies.
6. Require explicit human approval for production deployment.
7. Record deployment environment, commit SHA, artifact digest, approver, and rollback target.
8. Monitor health and define rollback thresholds.

**Exit criteria:** reproducible release, verified artifact provenance, approved deployment record, tested rollback, and accurate public status.

## 6. Pull-request consolidation decisions

These are review recommendations, not merge authorizations.

| PR | Topic | Recommended treatment |
|---|---|---|
| #154 | Governance, identity crosswalk, current-state audit, ambient audio spec | Rebase/review as the governance foundation. Keep historical records unchanged. |
| #146 | Runtime, packaging, HTTP validation, Python/Node CI | Primary candidate for maintenance consolidation; independently reproduce its reported local tests. |
| #153 | Repository-wide Python test coverage | Compare with #146 and incorporate missing coverage once; do not run duplicate CI designs indefinitely. |
| #115 | Earlier Python CI | Treat as superseded candidate after comparing its useful checks with the consolidated CI. |
| #152 | `.venv/` ignore rule | Fold into the single maintenance PR if not already covered. |
| #125 and #117 | AUDIO-TX and execution plan | Consolidate into one branch; preserve the richer optional local STT adapter only after review. Both are stale relative to current main. |
| #141 | Motion core and Godot prototype | Keep as the primary motion prototype; validate the post-check Godot changes before considering merge. |
| #150 | API hardening | Dependency branch targets the motion-core branch; review after #141 consolidation. |
| #121 | Gyro butterfly simulation | Compare against #141; fold only distinct functionality, otherwise retain as a separate documented experiment. |
| #145 | Engineering simulation core | Review independently as simulation-only work. |
| #155 | Archive and sandbox completion | Keep open until the full inventory and disposition evidence satisfy the issue acceptance criteria. |
| #147–#149 | Bot, orchestrator, main-engine attachments | Inspect the attached HTML sources before assigning implementation status. Titles alone are insufficient evidence. |
| #122 | Skills | Convert the broad request into scoped, testable language/AI skill modules and evaluation criteria. |

## 7. Unified task order and dependencies

1. **P0-A:** privacy review, branch protection, auto-merge containment, identity crosswalk, evolution-gate correction.
2. **P0-B:** full repository/branch/PR inventory and a current evidence-backed status model.
3. **P1-A:** consolidated CI, dependency/secret/code scanning, reproducible packaging.
4. **P1-B:** artifact manifest and archive hash verifier; close issue #155 only after evidence.
5. **P1-C:** update active status/backlog documents from generated evidence; preserve dated historical snapshots.
6. **P2-A:** consolidate and finish AUDIO-TX.
7. **P2-B:** consolidate motion core, validate Godot, then add sensor adapters.
8. **P2-C:** complete ambient audio source and privacy-safe capture/playback.
9. **P3-A:** financial/compliance source reconciliation and staged module implementation.
10. **P3-B:** AI Studio, event bus, timeline player, Unreal adapters, and other product modules after stable contracts exist.
11. **P4:** release qualification and explicitly authorized deployment.

## 8. Project completion measurement

Do not publish one unqualified completion percentage. Generate separate measures:

- Inventory coverage = classified discovered assets / all discovered in-scope assets.
- Implementation coverage = implemented applicable acceptance criteria / total applicable criteria.
- Test pass rate = passed executed tests / all executed tests.
- Validation coverage = passed required gates / all required gates.
- Archive integrity = verified file digests / all manifested files.
- Release readiness = passed release gates / all applicable release gates.
- External readiness = verified external prerequisites / all required external prerequisites.

Every numerator and denominator must link to evidence. UNKNOWN items remain in the denominator until explicitly scoped out or accepted as risk.

## 9. Immediate next execution checkpoint

The next engineering checkpoint should be limited to the P0 set:

1. Review and document the public-data exposure without copying sensitive values.
2. Protect `main` and the baseline and suspend auto-merge until required checks are enforced.
3. Rebase/review PR #154 and adopt its identity crosswalk through a versioned amendment.
4. Correct the evolution engine so evidence cannot be fabricated by lifecycle advancement.
5. Establish one canonical CI plan from #146/#153/#115.
6. Publish an evidence-backed inventory and status snapshot.

No merge, deployment, history rewrite, identifier merge, destructive cleanup, credential change, financial transaction, or hardware actuation is authorized by this plan.

## 10. Research references

- GitHub protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- GitHub protected branch requirements and status checks: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub secure use reference for Actions: https://docs.github.com/en/actions/reference/security/secure-use
- GitHub CodeQL setup: https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/configure-code-scanning/configure-code-scanning
- GitHub dependency review: https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review
- GitHub artifact attestations: https://docs.github.com/en/actions/concepts/security/artifact-attestations

These references describe platform capabilities and recommended controls. They do not establish that any feature is enabled in this repository.
