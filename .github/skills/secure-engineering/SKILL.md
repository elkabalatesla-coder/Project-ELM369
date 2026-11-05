---
name: secure-engineering
description: Apply defensive security, privacy, and authorization practices during software changes. Use when handling inputs, credentials, files, external services, automation, or security-sensitive workflows.
---

# Secure engineering

1. Identify assets, trust boundaries, untrusted inputs, side effects, and the impact of failure before changing security-sensitive behavior.
2. Never add, expose, echo, or commit credentials or private data. Scan modified files for secrets before commit using the available repository workflow.
3. Validate input and paths against trusted constraints. Do not let untrusted manifests or user data choose arbitrary files, commands, or destinations.
4. Preserve least privilege, explicit authorization, safe defaults, auditability, and rollback. Review workflow permissions and dependency changes with extra care.
5. In Project-ELM369, keep evidence/scoring, policy, authority, and safety-governor decisions separate. QSTATE or confidence is never authorization; provenance is not proof of authenticity.
6. Do not introduce autonomous exploitation, production mutation, credential changes, destructive deletion, or physical actuation. Defer or request human authorization when needed.
7. Describe what security checks establish and what they do not establish; do not claim a security guarantee from a passing test alone.
