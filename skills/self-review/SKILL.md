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

## Contract

### Preconditions

- Edits are complete enough to review as a coherent diff.
- The current task boundary is known.
- The next step would otherwise be testing or final reporting.

### Postconditions

- `status: completed` includes `issues`, `scope`, and `validation`.
- Real correctness, scope, or residual-quality issues are surfaced before validation.
- Remaining untested risk is explicitly stated instead of implied away.

### Invariants

- Review stays scoped to the current task diff.
- Findings are reported before broad retesting when issues remain.
- Unrelated cleanup is not introduced during review.

### Downstream Signals

- `issues` tells downstream work what must be fixed or monitored.
- `scope` records whether the diff stayed inside the planned boundary.
- `validation` tells downstream testing what check still matters after review.

## Failure Handling

### Common Failure Causes

- The diff is still changing and cannot yet be reviewed coherently.
- The review surface includes unrelated user changes that should not be adjudicated by this skill.
- Validation questions dominate because the diff itself is already clean.

### Retry Policy

- If the diff is still unstable, wait for one more coherent review point instead of repeatedly re-reviewing noise.
- If the same scope or residual issue appears twice, fix it before continuing to validation.

### Fallback

- Hand off to `targeted-validation` if the main remaining question is what to test.
- Ask the user when unrelated user edits make scope ownership ambiguous.

### Low Confidence Handling

- Mark residual risks explicitly when they are not yet validated.
- Prefer a narrower, evidence-backed finding set over speculative review comments.

## Output Example

```
[output: self-review | completed high | issues:"blocking: leftover debug print in auth handler; warning: docs still mention old route name" scope:"clean except docs drift" validation:"rerun auth handler test after removing debug print" | next:targeted-validation]
```

## Deactivation Trigger

- The diff review is complete and handed to validation or final reporting.
- The artifact being reviewed changes substantially and needs a fresh review pass.
