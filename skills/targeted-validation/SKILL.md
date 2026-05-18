---
name: targeted-validation
description: Choose the narrowest meaningful test or check that verifies a change without defaulting to a full build or test suite. Use when the agent must decide what to test after a patch — not needed when the user already specifies exactly which tests to run.
metadata:
  version: "0.2.0"
  tags: "coding, testing, validation"
---

# targeted-validation

Use this skill when a patch is ready and the cheapest useful check is not obvious.

## Decision Tree

- Single function or component: run the closest unit test or focused lint/type check.
- One feature path: run the feature's targeted test or a narrow smoke check.
- Cross-module behavior: run the smallest integration test that crosses the changed boundary.
- Script or installer change: run the script's smoke test and one representative real invocation.
- Documentation-only change: run link/reference checks when available; otherwise review rendered structure.
- Validation failure: diagnose with the smallest command that distinguishes test issue from code issue.

## Rules

- Start with the check most directly tied to the changed surface.
- Broaden only when the first result leaves material risk.
- Do not hide unrun validation; state why it was skipped.
- Prefer deterministic commands over manual inspection when available.

## Output

`[output: targeted-validation | completed <confidence> | command:"..." reason:"..." residual_risk:"..." | next:<action>]`
