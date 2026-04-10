---
name: targeted-validation
description: Choose the narrowest meaningful test or check that verifies a change without defaulting to a full build or test suite. Use when the agent must decide what to test after a patch — not needed when the user already specifies exactly which tests to run.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Reduce validation cost while preserving enough confidence for the task at hand. The skill keeps verification aligned with the actual change surface instead of treating every edit as justification for a full build or full test run.

# When to Use

- After a local patch, small refactor, or bounded bugfix when deciding what to test.
- When the affected surface can be tested or checked directly without a full build.
- When full-suite execution is expensive and the change is local enough for a narrower check.
- When the agent is about to run a broad test suite and a targeted check would suffice.

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
6. Broaden validation only when: (a) the targeted check passes but the change affects a shared interface used by other modules, (b) the targeted check cannot exercise the changed path at all, or (c) the change modifies error handling or fallback paths that are not covered by the targeted check.

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

# Common Anti-Patterns

- **"Run all tests" as the default.** The agent runs the full test suite after a one-line change in a single adapter, spending minutes on unrelated tests while the targeted adapter test would have taken seconds.
- **Skipping validation entirely.** The agent declares "looks correct" after editing without running any check, leaving the change unverified because it "seemed simple."

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

## Contract

### Preconditions

- A bounded code or document change has already been identified.
- At least one concrete validation mechanism exists, or the lack of automation can be stated explicitly.
- The affected runtime or behavior surface is narrow enough to justify focused verification first.

### Postconditions

- `status: completed` includes `checks_to_run`, `risks_not_covered`, and `pass_criteria`.
- The output names the smallest meaningful validation boundary and exact check to run.
- Broader validation is either justified explicitly or deferred explicitly.

### Invariants

- Full-suite validation is not the default.
- The first check stays aligned with the changed surface.
- Targeted failures are diagnosed locally before validation scope is broadened.

### Downstream Signals

- `checks_to_run` tells execution exactly which focused commands or manual checks to use.
- `risks_not_covered` captures the residual uncertainty after the narrow pass.
- `pass_criteria` defines when the targeted check is enough and when escalation is needed.

## Failure Handling

### Common Failure Causes

- No focused validation path exists for the changed surface.
- The change affects a shared contract that a narrow check cannot cover.
- The targeted check is flaky or fails because the environment is misconfigured.

### Retry Policy

- Allow one focused retry after diagnosing whether the issue is code, test, or setup related.
- If the same targeted check remains inconclusive, broaden validation deliberately and explain why.

### Fallback

- Use the smallest meaningful manual verification when no automated check exists.
- Escalate to broader validation when shared-interface risk exceeds the narrow check.
- Ask the user before running expensive suites if time or cost constraints were previously stated.

### Low Confidence Handling

- Surface uncovered risks explicitly instead of claiming broad confidence.
- Treat a passing targeted check as local evidence only when contract surface remains wide.

## Output Example

```yaml
[skill-output: targeted-validation]
status: completed
confidence: high
outputs:
  checks_to_run:
    - "pytest tests/payment/test_client.py -k retry"
  risks_not_covered:
    - "other payment clients do not share this retry path"
  pass_criteria:
    - "retry test passes"
    - "no duplicate charge side effects appear in the focused fixture"
signals:
  broader_validation_recommended: false
recommendations:
  next_step: "run the focused retry test before any wider suite"
[/skill-output]
```

## Deactivation Trigger

- Deactivate when the task is complete and no further validation cycles are expected.
- Deactivate when validation must be escalated into a broader suite or a different skill-owned workflow.
- Deactivate once downstream review has consumed the residual-risk statement.
