---
name: code-review
description: Review a change set for high-confidence correctness, security, compatibility, and regression issues. Use when reviewing a diff, pull request, or proposed implementation.
---

# Code review

1. Read the full diff and enough surrounding code to understand the affected behavior and callers.
2. Prioritize concrete defects: incorrect behavior, missing error handling, unsafe trust boundaries, compatibility breaks, and missing regression coverage.
3. Verify each suspected issue against source, tests, and contracts. Report only actionable findings; separate confirmed defects from questions or risks.
4. For each finding, state the impact and point to the smallest relevant location. Avoid style-only feedback unless it affects correctness or maintainability.
5. Check that tests exercise the relevant behavior, not merely that a test command passed.
6. In Project-ELM369 reviews, check for claims that confuse scaffolding with implementation and for bypasses of authorization, provenance, safety, or rollback gates.
