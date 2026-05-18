---
name: self-review
description: Review the agent's own diff for quality issues, debug residuals, and scope violations before running tests. Use when all edits are complete, before targeted-validation, when the diff spans multiple files and manual review would catch issues that tests miss, or when the user explicitly asks for a diff review before testing.
metadata:
  version: "0.2.0"
  tags: "coding, review, quality"
---

# self-review

Use this skill after edits are complete and before validation or final reporting.

## Use When

- The diff spans multiple files.
- The user asks for a review before testing.
- A change touched shared behavior, scripts, or governance docs.

## Review Checklist

Check only the current task diff:

- correctness: behavior matches the request and no obvious regression is introduced
- scope: no unrelated cleanup, formatting churn, or opportunistic refactor slipped in
- residuals: no debug prints, commented-out code, temporary files, or stale notes remain
- consistency: names, docs, examples, and generated data agree with each other
- boundaries: public contracts and compatibility impact are intentional
- validation: the planned check is narrow but meaningful

## Rules

- Findings first when issues exist.
- Fix real issues before running validation when the fix is obvious and in scope.
- Do not rewrite unrelated code while reviewing.
- If a risk remains untested, state it explicitly.

## Output

`[output: self-review | completed <confidence> | issues:"none|..." scope:"clean|..." validation:"..." | next:validation]`
