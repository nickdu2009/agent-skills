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
