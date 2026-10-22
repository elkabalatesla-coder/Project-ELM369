# Coding-agent skill set research

**Research date:** 2026-10-22
**Purpose:** Select high-value, repeatable skills for a coding agent working in Project-ELM369 and publish them in a portable format.

## Findings

GitHub documents agent skills as on-demand folders containing a required `SKILL.md` with YAML `name` and `description` metadata. Skills are selected when relevant, which supports small, focused procedures instead of one large always-loaded prompt. GitHub also distinguishes project skills from personal skills and warns that shell-enabled or third-party skills should be inspected before use. The Agent Skills open-standard repository describes the same progressive-disclosure model.

For a coding agent, the highest-leverage competencies are a connected engineering loop rather than language trivia: understand the repository and task; plan bounded changes; implement against existing conventions; test and debug; assess security; review for regressions; research and document evidence; and communicate validation and limitations. Project-ELM369 adds a need to distinguish implemented tools from scaffolds and to honor explicit safety, authorization, provenance, and rollback gates.

## Prioritized skills

| Priority | Skill | Why it matters | Project-ELM369 application |
|---|---|---|---|
| 1 | Repository orientation | Prevents edits to the wrong layer and mistaken claims about what exists. | Start at `docs/REPO_MAP.md`; distinguish source code, registries, schemas, docs, and artifact/stub areas. |
| 2 | Task planning | Converts ambiguous requests into a bounded, verifiable change. | State assumptions, preserve scope, and keep plans in the response unless a plan file is requested. |
| 3 | Software implementation | Produces maintainable changes that fit local patterns and contracts. | Inspect neighboring code and tests; prefer existing dependencies and interfaces. |
| 4 | Testing and debugging | Makes behavior reproducible and catches regressions before delivery. | Find the relevant workflow and test command; reproduce failures and validate fixes. |
| 5 | Secure engineering | Reduces the risk of leaking secrets or weakening safety controls. | Preserve authorization, provenance, safety, and rollback gates; never treat a score as permission. |
| 6 | Code review | Finds correctness and regression issues beyond whether code compiles. | Review changed behavior against callers, failure modes, tests, and compatibility. |
| 7 | Research and technical writing | Grounds decisions in current, attributable evidence and clear uncertainty. | Prefer primary sources; distinguish verified implementation from design intent and speculation. |
| 8 | Tool integration | Avoids duplicating existing repository capabilities or breaking tool contracts. | Check the tool registry, repository map, module README, schema, and tests before extending a tool. |
| 9 | Change delivery | Makes work auditable and useful to maintainers. | Report files changed, checks actually run, results, and unresolved limitations without overstating completion. |

These priorities synthesize GitHub's task-specific skill and coding-agent guidance with the repository's live-tool map and evolution/QBIT safety boundaries. They are capability areas, not a claim that one prompt can guarantee error-free performance.

## Skills added

Nine repository-local skills live under `.github/skills/`:

- `repository-orientation`
- `task-planning`
- `software-implementation`
- `testing-debugging`
- `secure-engineering`
- `code-review`
- `technical-research`
- `elm369-tool-integration`
- `change-delivery`

Each has task-triggering metadata and an actionable workflow. Together they give the agent a reusable practice loop for new work and for changes involving existing repository tools. They do not modify personal skills, hidden agent configuration, model weights, or skills installed outside this repository. Skills-compatible hosts must support repository skills and load them for the relevant task; actual competency still depends on following the instructions and validating results.

## Research sources

1. GitHub Docs, [Agent skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills) — skill purpose, supported project locations, progressive use, and supported Copilot surfaces. Retrieved 2026-10-22.
2. GitHub Docs, [Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) — required `SKILL.md` metadata, structure, skill discovery, security warning for shell pre-approval, and guidance on skills versus repository-wide instructions. Retrieved 2026-10-22.
3. Agent Skills, [open-standard repository](https://github.com/agentskills/agentskills) — portable folder format and progressive-disclosure model. Retrieved 2026-10-22.
4. GitHub Docs, [GitHub Copilot on GitHub.com](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github) — coding agents can research, plan, edit, and test; review and human validation remain separate parts of the workflow. Retrieved 2026-10-22.
5. Project-ELM369, [`docs/REPO_MAP.md`](../REPO_MAP.md), [`ELM369_AUTOMATED_EVOLUTION_SPEC_v1.0.0.md`](../architecture/ELM369_AUTOMATED_EVOLUTION_SPEC_v1.0.0.md), [`ELM369_QBIT_DESIGN_v0.1.0.md`](../architecture/ELM369_QBIT_DESIGN_v0.1.0.md), and [`data/registries/elm369_tools.json`](../../data/registries/elm369_tools.json) — repository-specific implementation, validation, provenance, and authorization boundaries.

## Scope and limits

This is a focused, source-linked synthesis, not a universal ranking of every engineering competency or a benchmark of a particular model. The skills add repository-level procedures only. The personal/global skills available to a coder are outside this repository and were not inspected or changed; a skill file cannot make an agent literally “master” a skill or establish that an agent has executed it successfully.
