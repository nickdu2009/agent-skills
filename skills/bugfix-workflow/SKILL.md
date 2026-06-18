---
name: bugfix-workflow
description: Diagnose, narrow, fix, and verify bugs through an evidence-first workflow. Use when a bug or unexpected behavior is reported, test failures need investigation, intermittent issues surface in production, or the root cause is not yet confirmed. Triggers on "broken", "failing", "error", "bug", or "unexpected behavior" keywords.
metadata:
  version: "0.2.0"
  tags: "coding, debugging, validation"
---

# bugfix-workflow

Use this skill when behavior is broken, failing, erroneous, intermittent, or unexpected and the root cause is not confirmed.

## Core Rule

Do not patch a guessed cause. First connect symptom, fault path, and fix with evidence.

## Workflow

1. State the symptom and expected behavior.
2. Identify the strongest available clue: failing test, stack trace, log, repro step, endpoint, or user-visible path.
3. Narrow the fault domain to the smallest plausible module or function.
4. Confirm the cause with code-path or behavioral evidence.
5. Apply the smallest fix that addresses the confirmed cause.
6. Validate the failing path first, then broaden only if risk remains.

## Evidence Standards

Strong evidence includes:

- a failing test or repro that exercises the bug
- direct code-path mismatch between actual and expected behavior
- logs tied to the failing path
- a before/after check showing the symptom is resolved

Weak evidence includes naming similarity, nearby code smell, or intuition without a path from symptom to cause.

## Output

`[output: bugfix-workflow | completed <confidence> | symptom:"..." cause:"..." fix:"..." validation:"..." | next:<action>]`

## Contract

### Preconditions

- A bug symptom, failing test, or unexpected behavior has been reported.
- The root cause is not yet confirmed.
- The agent can gather evidence before editing.

### Postconditions

- `status: completed` includes `symptom`, `cause`, `fix`, and `validation`.
- The chosen fix is tied to a confirmed failure path rather than guesswork.
- Validation checks the original symptom first.

### Invariants

- Evidence precedes editing.
- Confirmed causes remain distinct from hypotheses.
- The fix stays scoped to the confirmed fault path.

### Downstream Signals

- `symptom` preserves the user-visible failure for later verification.
- `cause` records the confirmed failure path that justified the fix.
- `fix` explains the chosen repair direction for downstream review.
- `validation` tells downstream checks how the original symptom was re-tested.

## Failure Handling

### Common Failure Causes

- The symptom cannot be reproduced or tied to a concrete path.
- Multiple root-cause hypotheses remain plausible with no evidence to rank them.
- The requested fix expands into a refactor or redesign instead of a bounded repair.

### Retry Policy

- Gather one stronger piece of evidence before broadening the search.
- If two rounds of evidence gathering still do not narrow the fault domain, stop and ask or re-scope.

### Fallback

- Hand off to `scoped-tasking` if the task boundary is still too broad.
- Hand off to `targeted-validation` if the main question becomes "which test should I run first".

### Low Confidence Handling

- State the remaining uncertainty explicitly instead of forcing a fix.
- Prefer no edit over a speculative patch.

## Output Example

```
[output: bugfix-workflow | completed high | symptom:"optional profile path returns 500" cause:"nullable profile lookup is dereferenced in account service" fix:"add guard at first optional-profile access and return 404" validation:"rerun profile-missing endpoint test and confirm non-profile account updates still pass" | next:self-review]
```

## Deactivation Trigger

- The confirmed fix direction is applied and handed to validation or review.
- The task is re-scoped into design, refactor, or broader investigation work.
