---
name: software-implementation
description: Implement focused, maintainable changes that fit the repository's language, architecture, and existing conventions. Use for code, configuration, and test changes.
---

# Software implementation

1. Read nearby source and tests before editing. Identify public interfaces, data formats, error handling, and supported runtimes.
2. Make the smallest complete change that satisfies the acceptance conditions; preserve compatibility unless a breaking change is requested.
3. Reuse existing modules and dependencies. Do not add a dependency, generated file, helper script, or abstraction without a demonstrated need.
4. Keep trust boundaries explicit: validate untrusted input, avoid logging secrets or payloads unnecessarily, and do not weaken policy or authorization gates.
5. Update directly related tests and documentation. Never remove unrelated tests to make validation pass.
6. Review the diff for accidental changes and state what remains unimplemented. Do not describe stubs or designs as working features.
