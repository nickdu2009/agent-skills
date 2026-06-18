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

## Contract

### Preconditions

- A changed, analyzed, or reviewed surface is known.
- Multiple plausible validation options exist, or the narrowest useful check is not obvious.
- The task benefits from validation choice rather than blind full-suite execution.

### Postconditions

- `status: completed` includes `command`, `reason`, and `residual_risk`.
- The chosen check is the narrowest meaningful validation for the current surface.
- Any skipped broader validation is made explicit.

### Invariants

- Validation selection stays tied to the changed surface.
- Broader checks are justified by residual risk, not habit.
- Unrun validation remains visible as residual risk.

### Downstream Signals

- `command` tells execution exactly which check to run next.
- `reason` explains why that check is the best first validation.
- `residual_risk` records what still remains unverified afterward.

## Failure Handling

### Common Failure Causes

- The changed surface is still too unclear to choose a meaningful check.
- Available checks are too broad, flaky, or expensive for the current risk.
- The question is actually about diagnosis or review rather than validation choice.

### Retry Policy

- Choose the cheapest discriminating check first.
- If the first check fails ambiguously, narrow once more before broadening to a larger suite.

### Fallback

- Hand off to `bugfix-workflow` if validation selection turns into fault diagnosis.
- Hand off to `self-review` if the diff itself still needs inspection before testing.

### Low Confidence Handling

- State when the proposed check is only a best-effort proxy.
- Record the unvalidated risk explicitly if no narrow deterministic check exists.

## Output Example

```
[output: targeted-validation | completed high | command:"pytest tests/auth/test_optional_profile.py -k missing_profile" reason:"directly exercises the changed handler path without running unrelated account flows" residual_risk:"full account update suite still unrun" | next:run-command]
```

## Deactivation Trigger

- The validation decision is made and handed to execution or reporting.
- The changed surface shifts enough that validation must be reselected from scratch.
