---
name: task-planning
description: Turn an implementation request into a bounded, testable sequence of work. Use when requirements are ambiguous, cross-cutting, high-risk, or explicitly ask for a plan.
---

# Task planning

1. Restate the requested outcome internally; identify the affected users, interfaces, and acceptance conditions.
2. Explore relevant code and existing validation before deciding scope. Ask a concise question when a critical requirement cannot be safely inferred.
3. Break the work into the smallest complete change and a short checklist. Include tests, documentation, security implications, and delivery steps where applicable.
4. Preserve existing behavior unless the request explicitly changes it. Do not expand into adjacent cleanup.
5. For Project-ELM369, treat credentials, destructive actions, external effects, production mutation, and physical actuation as explicit authorization boundaries. A confidence score never substitutes for approval.
6. Do not create a plan file unless the user asks for one. Do not claim a plan is implementation or validation.
