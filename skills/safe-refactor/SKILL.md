---
name: safe-refactor
description: Guide small, controlled refactors that improve code structure while keeping behavior and interfaces stable. Use when the task is structural cleanup (extract duplicate code, consolidate similar functions, simplify tangled logic), pre-refactor for a feature, or local improvement is needed without behavior change. Triggers on "refactor", "extract", "consolidate", "simplify", or "cleanup" keywords.
metadata:
  version: "0.2.0"
  tags: "coding, refactor, safety"
---

# safe-refactor

Use this skill for structural cleanup, extraction, consolidation, or simplification without behavior change.

## Use When

- The user asks to refactor, extract, consolidate, simplify, or clean up.
- Duplicate logic or tangled local structure is the target.
- A behavior-preserving internal change is needed before a feature or fix.

## Required Invariants

Before editing, state:

- behavior that must remain unchanged
- public interface or file boundary that must remain stable
- smallest validation that can detect accidental behavior drift

## Execution Rules

- Make one structural move at a time.
- Keep names and ownership aligned with the surrounding module.
- Do not change inputs, outputs, errors, persistence, or protocols unless explicitly requested.
- Stop when the responsibility is clearer; do not chase unrelated cleanup.

## Output

`[output: safe-refactor | completed <confidence> | invariants:"..." changes:"..." validation:"..." | next:<action>]`
