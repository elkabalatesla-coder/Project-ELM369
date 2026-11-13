---
name: change-delivery
description: Deliver a code change with an auditable summary of scope, validation, and limitations. Use when preparing a commit, pull request, progress update, or final handoff.
---

# Change delivery

1. Inspect the final diff and ensure only task-related files changed.
2. Run applicable existing validation and any required secret scan. Never report an unrun check as passed.
3. Summarize the user-visible result, key files or behavior changed, and validation results.
4. State remaining risks, blocked checks, and unimplemented work directly. Do not overstate confidence, completeness, or mastery.
5. Follow the requested delivery workflow. Do not create a pull request unless explicitly asked.
6. Keep the handoff concise and use links or exact paths so a maintainer can verify the result.
