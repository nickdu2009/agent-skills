---
name: bugfix-workflow
description: Diagnose, narrow, fix, and verify bugs through an evidence-first workflow. Use when a bug or unexpected behavior is reported, test failures need investigation, intermittent issues surface in production, or the root cause is not yet confirmed. Triggers on "broken", "failing", "error", "bug", or "unexpected behavior" keywords.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Provide a practical, repeatable workflow for bugfix tasks. The skill keeps the agent from editing too early, broadening the fault domain without evidence, or declaring success without verifying the specific symptom.

# When to Use

- When the main objective is to fix a bug.
- When a symptom is known but the root cause is not yet confirmed.
- When multiple plausible failure domains exist and need to be narrowed.

# When Not to Use

- When the task is purely additive feature work.
- When the bug is already fully understood and only a mechanical patch remains.
- When the user wants a broad reliability review rather than a specific fix.

# Core Rules

- Define the symptom clearly.
- Identify the smallest plausible fault domain.
- Gather evidence before editing.
- Prefer the smallest viable fix.
- Verify the fix with the narrowest meaningful validation.
- Report residual uncertainty and follow-up risks.
- Separate confirmed causes from plausible hypotheses.

# Execution Pattern

1. State the observable symptom.
2. Define the smallest plausible fault domain.
3. Gather evidence from code paths, tests, logs, or reproduction steps.
4. Form and rank hypotheses. Rank by: (1) directness of code-path evidence, (2) ease of verification, (3) consistency with observed symptoms. Investigate the top-ranked hypothesis first.
5. Edit only after one hypothesis is confirmed by direct code-path evidence or a reproducible test case.
6. Apply the smallest viable fix.
7. Validate against the original symptom.
8. Report what is confirmed, what is still uncertain, and what may need follow-up.

# Input Contract

Provide:

- the symptom
- reproduction steps or failing evidence
- known constraints
- whether the bug is deterministic or intermittent

Optional but helpful:

- recent related changes
- suspected modules
- prior failed fixes

# Output Contract

Return:

- the symptom statement
- the narrowed fault domain
- supporting evidence
- the chosen fix and why it is the smallest viable one
- the targeted validation result
- residual uncertainty and follow-up risks

# Guardrails

- Do not treat correlation as cause without evidence.
- Do not edit before the fault domain is plausibly narrowed.
- Do not combine unrelated cleanup into the fix.
- Do not report "fixed" unless the original symptom was checked directly or the limitation is clearly stated.
- For intermittent issues, record what remains unproven.

# Common Anti-Patterns

- **Patching before diagnosing.** The agent sees something that looks wrong and immediately edits it without confirming the code path is related to the reported symptom. The "fix" turns out to be for a different issue entirely.
- **Treating correlation as causation.** A recent commit touched the same file where the bug manifests, so the agent assumes it is the cause and reverts part of it — without tracing the actual failure path or checking whether the symptom existed before that commit.

See skill-anti-pattern-template.md for format guidelines.

# Composition

Part of the `bugfix-standard` chain (see the project governance file § Skill Chain Triggers).

Role: Core diagnostic component. Receives narrowed fault domain from read-and-locate, produces confirmed root cause and fix hypothesis, hands to minimal-change-strategy.

Additional compositions:

- Fallback to `read-and-locate` when failure path is still unknown
- Fallback to `context-budget-awareness` when diagnosis spans too many files or hypotheses

# Example

Task: "Background retries sometimes send duplicate emails."

A disciplined bugfix flow is:

- symptom: duplicate email on retry only
- initial fault domain: retry scheduler, idempotency key handling, email enqueue path
- evidence: logs show duplicate enqueue with same payload but missing idempotency marker
- fix: restore or preserve the marker on retry path only
- validation: run the retry-focused test or reproduction, not the entire notification stack

Residual uncertainty may remain if no deterministic reproduction exists; state that explicitly.

## Contract

### Preconditions

- A bug symptom or unexpected behavior has been reported.
- The root cause is not yet confirmed.
- The agent can gather evidence from code, logs, tests, or reproduction steps before editing.

### Postconditions

- `status: completed` includes `symptom`, `repro`, `fault_domain`, and `fix_hypothesis`.
- The chosen fix is backed by direct evidence or a reproducible path rather than speculation alone.
- Validation is tied back to the original symptom.

### Invariants

- Diagnosis precedes editing.
- Confirmed causes remain distinct from ranked but unconfirmed hypotheses.
- The fix stays scoped to the confirmed failure path.

### Downstream Signals

- `symptom` preserves the user-visible failure to verify later.
- `repro` gives downstream validation the exact failure path to re-check.
- `fault_domain` narrows where edits may happen.
- `fix_hypothesis` documents the confirmed cause and chosen repair direction.

## Failure Handling

### Common Failure Causes

- The symptom cannot be reproduced or evidenced with the available information.
- Multiple plausible fault domains remain and none can be confirmed.
- The bug appears intermittent and validation cannot fully prove the fix.

### Retry Policy

- Allow one additional evidence-gathering pass when the first hypothesis cannot be confirmed.
- If no hypothesis can be confirmed after the second pass, stop patching and report the residual uncertainty.

### Fallback

- Use `read-and-locate` when the failure path is still unknown.
- Use `context-budget-awareness` when diagnosis is spinning across too many files or hypotheses.
- Escalate to the user when reproduction depends on unavailable environment state or missing logs.

### Low Confidence Handling

- State clearly that the fix remains a best-supported hypothesis.
- Keep validation narrow but explicitly note which intermittent behaviors remain unproven.

## Output Example

```yaml
[skill-output: bugfix-workflow]
status: completed
confidence: medium
outputs:
  symptom: "duplicate email on retry only"
  repro:
    - "run the retry-focused notification scenario"
  fault_domain:
    - "retry scheduler"
    - "idempotency marker preservation"
  fix_hypothesis: "retry path drops the idempotency marker before enqueue"
signals:
  minimal_fix_ready: true
recommendations:
  downstream_skill: "minimal-change-strategy"
[/skill-output]
```

## Deactivation Trigger

- Deactivate once the root cause has been confirmed and handed off to implementation.
- Deactivate when the task becomes a purely mechanical patch with no remaining diagnosis work.
- Deactivate if the investigation must pause for user-supplied reproduction data or logs.
