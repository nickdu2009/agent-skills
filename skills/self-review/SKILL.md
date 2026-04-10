---
name: self-review
description: Review the agent's own diff for quality issues, debug residuals, and scope violations before running tests. Use when all edits are complete, before targeted-validation, when the diff spans multiple files and manual review would catch issues that tests miss, or when the user explicitly asks for a diff review before testing.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Catch low-cost quality issues in the agent's own diff before entering the validation phase. The goal is to find debug residuals, scope violations, and anti-patterns that tests will not catch, reducing review cost and preventing avoidable rework.

# When to Use

- After all planned edits are complete and before running tests.
- When the diff spans multiple files and manual review would catch issues that tests miss.
- When the task involved substantial code changes (not trivial one-line fixes).
- When the user explicitly asks for a diff review before testing.

# When Not to Use

- For trivial single-line changes where the edit is obviously correct.
- When the user explicitly says to skip review and go straight to tests.
- During exploratory editing when the diff is still in progress.

# Core Rules

- Review each changed file in the diff against the planned working set.
- Check for debug residuals (console.log, print(), TODO: remove, commented-out code).
- Check for scope violations (files changed that were not in the plan).
- Check for anti-patterns (type assertions to bypass checks, empty catch blocks, hardcoded values).
- Grade each issue as blocking or warning.
- Fix blocking issues before proceeding to targeted-validation.
- Do not fix warning-level issues unless they are trivial — record them instead.

# Execution Pattern

1. Run git diff (or equivalent) to get the full set of changed files.
2. Compare changed files against the planned working set from plan-before-action.
3. For each changed file, scan for items on the anti-pattern checklist.
4. Grade each finding: blocking (must fix before testing) or warning (record for later).
5. If blocking issues found, fix them. Then re-run self-review to confirm clean. If clean, hand off to targeted-validation.

Anti-pattern checklist:

1. Debug residuals: `console.log`, `print()`, `debugger`, `TODO: remove`, `FIXME`, commented-out code blocks.
2. Scope violations: files modified that were not in the planned working set.
3. Hardcoded values: paths, secrets, API keys, environment-specific strings.
4. Signature mismatches: function signature changed but not all callers updated.
5. Empty error handling: `pass` in except blocks, empty `catch {}`, swallowed errors.
6. Unused imports: new imports added during refactoring but old ones not removed.
7. Type escape hatches: `as any`, `# type: ignore`, `@SuppressWarnings` used to bypass type checks.
8. Inconsistent error messages: new error strings that don't match the existing style.
9. Hardcoded test expectations: test assertions with magic numbers instead of computed values.

# Input Contract

Provide:

- the current diff (git diff or equivalent)
- the planned working set from plan-before-action

Optional:

- the project's lint rules or style conventions
- known acceptable exceptions

# Output Contract

Return:

```
review_result: clean | has-issues
issues:
  - file: "src/auth.ts"
    line: 42
    severity: blocking
    type: "debug-residual"
    detail: "console.log left in production code"
    fix: "Remove line 42"
  - file: "src/config.ts"
    line: 15
    severity: warning
    type: "out-of-scope"
    detail: "File not in planned working set"
    fix: "Revert changes to this file or justify inclusion"
blocking_count: 1
warning_count: 1
```

# Guardrails

- Do not run tests before self-review is clean on blocking issues.
- Do not treat all issues as equal severity — use the blocking/warning distinction.
- Do not skip self-review because "tests will catch it" — tests verify behavior, not diff quality.
- Do not use self-review as an excuse to start cleaning up code beyond the task scope.
- Check the planned working set against actually changed files — unexpected files are a signal.

# Common Anti-Patterns

- **Skipping straight to tests.** The agent finishes editing and immediately runs the test suite, missing a console.log that will ship to production and a config file that was accidentally modified.
- **Treating warnings as blocking.** The agent refuses to proceed because of a minor style inconsistency, wasting time on issues that do not affect correctness.

# Composition

- Follows `minimal-change-strategy` — self-review enforces the same discipline from the review side.
- Precedes `targeted-validation` — review diff quality first, then verify behavior.
- Consumes the planned working set from `plan-before-action`.
- Drop after review passes — self-review does not stay active during validation.

Part of `bugfix-standard`, `refactor-safe`, `multi-file-planned`, and `design-first` chains. See full chain definitions in docs/maintainer/skill-chain-aliases.md.

# Example

Task: After implementing a caching layer for user profiles, self-review the diff.

Diff contains 4 changed files:

- `src/cache/profile-cache.ts` — new cache logic (in plan) → scan for debug residuals
- `src/handlers/profile.ts` — updated to use cache (in plan) → found `console.log("cache hit")` on line 58 → **blocking**
- `src/config.ts` — config formatting change (NOT in plan) → **warning**: out-of-scope change
- `tests/cache.test.ts` — new tests (in plan) → clean

Result: 1 blocking issue (debug log), 1 warning (scope violation). Fix the console.log, then proceed to targeted-validation.

## Contract

### Preconditions

- Planned edits are complete enough to review as a whole diff.
- A working set or intended scope exists to compare against the actual diff.
- Review happens before validation or before a user-requested diff review handoff.

### Postconditions

- `status: completed` includes `findings`, `residual_risks`, and `scope_violations`.
- Blocking issues are either fixed immediately or reported before validation starts.
- Warning-level items are recorded without triggering unrelated cleanup.

### Invariants

- Review is diff-focused rather than a fresh redesign pass.
- Blocking and warning issues are distinguished explicitly.
- Unexpected file changes are surfaced instead of silently accepted.

### Downstream Signals

- `findings` gives the concrete issues and severities.
- `residual_risks` tells validation or the user what remains after review.
- `scope_violations` flags any changes outside the planned boundary.

## Failure Handling

### Common Failure Causes

- The planned working set is missing, so scope comparison is weak.
- The diff is still changing, making review results unstable.
- The reviewer starts broad cleanup instead of reporting targeted issues.

### Retry Policy

- Re-run once after fixing blocking issues.
- If the diff keeps changing underneath review, stop and return to execution until a stable review point exists.

### Fallback

- Ask for the intended working set when scope-violation checking is impossible.
- Hand off to `minimal-change-strategy` when review reveals the patch grew beyond task scope.
- Continue to `targeted-validation` only after blocking issues are cleared or explicitly waived by the user.

### Low Confidence Handling

- Record uncertain issues as residual risks rather than blockers.
- Do not invent precision for missing line-level evidence; report the uncertainty directly.

## Output Example

```yaml
[skill-output: self-review]
status: completed
confidence: high
outputs:
  findings:
    - "blocking: debug log left in handler"
  residual_risks:
    - "config formatting file changed outside the planned scope"
  scope_violations:
    - "src/config.ts"
signals:
  blocking_count: 1
recommendations:
  next_step: "remove the debug log, then re-run self-review"
[/skill-output]
```

## Deactivation Trigger

- Deactivate once the diff is clean enough to hand off to validation.
- Deactivate when the user explicitly chooses to proceed despite warning-level residual risks.
- Deactivate if execution resumes to fix newly found blocking issues.
