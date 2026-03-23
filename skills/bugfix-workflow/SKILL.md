---
name: bugfix-workflow
description: Diagnose, narrow, fix, and verify bugs through an evidence-first workflow with bounded scope and explicit residual risk.
tags: [coding, agents, orchestration, efficiency]
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
4. Form and rank hypotheses.
5. Edit only after one hypothesis is well supported.
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

# Composition

Combine with:

- `scoped-tasking` to keep diagnosis inside the smallest plausible domain
- `read-and-locate` to trace the relevant path quickly
- `minimal-change-strategy` to keep the fix small
- `targeted-validation` to verify the symptom without paying unnecessary suite cost

# Example

Task: "Background retries sometimes send duplicate emails."

A disciplined bugfix flow is:

- symptom: duplicate email on retry only
- initial fault domain: retry scheduler, idempotency key handling, email enqueue path
- evidence: logs show duplicate enqueue with same payload but missing idempotency marker
- fix: restore or preserve the marker on retry path only
- validation: run the retry-focused test or reproduction, not the entire notification stack

Residual uncertainty may remain if no deterministic reproduction exists; state that explicitly.
