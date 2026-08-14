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

## Contract

### Preconditions

- The task is structural cleanup, extraction, consolidation, or simplification.
- Behavior and public interfaces are expected to remain stable.
- The refactor boundary is narrow enough to validate locally.

### Postconditions

- `status: completed` includes `invariants`, `changes`, and `validation`.
- The refactor boundary is explicit enough for downstream review or validation.
- Behavior-preserving assumptions remain visible rather than implicit.

### Invariants

- Structural change does not silently alter behavior.
- Public interfaces stay stable unless the user explicitly asked otherwise.
- Each refactor move remains bounded and reviewable.

### Downstream Signals

- `invariants` tells downstream validation what must remain true.
- `changes` explains the structural move that was performed.
- `validation` tells downstream checks how behavior drift would be detected.

## Failure Handling

### Common Failure Causes

- The cleanup request actually changes behavior or public contracts.
- Multiple unrelated cleanup opportunities tempt the refactor beyond scope.
- Validation cannot detect whether the behavior stayed stable.

### Retry Policy

- Reduce the refactor to a smaller structural move if the current boundary is too broad.
- Stop after one failed attempt to preserve invariants and re-scope rather than pushing through.

### Fallback

- Hand off to `design-before-plan` if interface or contract changes become necessary.
- Hand off to `scoped-tasking` if the structural boundary is still unstable.

### Low Confidence Handling

- Keep invariants conservative and explicit.
- Prefer deferring a cleanup step over mixing it with unrelated behavior changes.

## Output Example

```
[output: safe-refactor | completed medium | invariants:"handler signatures unchanged; normalized payload shape unchanged" changes:"extract shared normalization helper and switch handlers one by one" validation:"run handler-focused tests after each extraction step" | next:artifact-review-loop:self-delivery]
```

## Deactivation Trigger

- The bounded structural change is complete and handed to review or validation.
- The work stops being behavior-preserving and must escalate to another skill.
