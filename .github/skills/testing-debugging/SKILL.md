---
name: testing-debugging
description: Reproduce failures, select relevant checks, diagnose root causes, and verify behavior after a fix. Use for test, build, lint, CI, and runtime failures or any behavior-changing edit.
---

# Testing and debugging

1. Locate the module's existing tests and its GitHub Actions workflow. Use the repository's current tools and commands; do not add a test framework just for convenience.
2. Establish the failure or expected behavior with the smallest relevant reproducible check. Read complete, relevant error output before changing code.
3. Trace the failure to its cause, including inputs, boundaries, and callers. Avoid masking the symptom or loosening a test without evidence.
4. Add or update focused regression coverage for changed behavior and important edge cases.
5. Run the relevant tests and other existing checks required by the change. Re-run affected checks after the final edit.
6. Report exact checks and outcomes. If a check cannot be run, state that plainly rather than implying it passed.
