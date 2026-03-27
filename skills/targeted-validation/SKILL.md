---
name: targeted-validation
version: 0.1.0
description: Choose the narrowest meaningful validation that protects confidence without defaulting to full-suite execution.
tags: [coding, agents, orchestration, efficiency]
---

# Purpose

Reduce validation cost while preserving enough confidence for the task at hand. The skill keeps verification aligned with the actual change surface instead of treating every edit as justification for a full build or full test run.

# When to Use

- After a local patch, small refactor, or bounded bugfix.
- When the affected surface can be tested or checked directly.
- When full-suite execution is expensive and not clearly necessary.

# When Not to Use

- When the user explicitly requests a full build or full test suite.
- When the change affects shared infrastructure or a wide contract surface.
- When narrow validation cannot cover the risk introduced by the change.

# Core Rules

- Validate as narrowly as possible.
- Prefer targeted tests, focused checks, or local compile steps over full-suite execution.
- Do not run full builds or full tests by default.
- When validation fails, iterate around the failure before broadening coverage.
- Suggest the smallest meaningful verification command.
- Expand validation only when risk or evidence justifies it.

# Execution Pattern

1. Map the change to its affected runtime surface.
2. Choose the cheapest validation that exercises that surface.
3. Run the targeted check.
4. If it fails, diagnose whether the failure is in the code, the test, or the setup.
5. Fix or narrow the issue around the failure.
6. Broaden validation only if the local result is still insufficient.

# Input Contract

Provide:

- the change summary
- the affected files or interfaces
- available validation mechanisms
- time or cost constraints if relevant

Optional but helpful:

- known flaky tests
- commands already attempted

# Output Contract

Return:

- the chosen validation boundary
- the exact targeted check to run
- why that check is sufficient or insufficient
- the result
- whether broader validation is recommended

# Guardrails

- Do not default to "run everything."
- Do not confuse broad validation with better reasoning.
- Do not ignore a targeted failure by jumping straight to unrelated checks.
- If broader validation is required, explain the risk that justifies the extra cost.
- If no meaningful automated validation exists, propose the smallest manual or observational check.

# Composition

Combine with:

- `minimal-change-strategy` to keep validation cost aligned with patch size
- `safe-refactor` to verify structural changes in small steps
- `bugfix-workflow` to confirm the symptom is actually resolved
- `multi-agent-protocol` when separate hypotheses need separate checks

# Example

Task: "Fix date parsing in one import adapter."

Prefer validation such as:

- the adapter's unit tests
- a focused command that parses the failing fixture
- a file-local type check if relevant

Do not default to the full integration suite unless the adapter change alters a shared parsing contract used elsewhere.
