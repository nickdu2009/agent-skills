# Cross-Platform Trigger Baseline Report

> Date:
> Tester:
> Skill revision: (git SHA or version)

## Purpose

Record trigger accuracy across platforms to establish a quantitative baseline.
Run after changing skill `description` fields, `When to Use` / `When Not to Use`
sections, after adding or removing skills, or after changing the model lineup
used for trigger evaluation.

## Platforms Tested

| Platform | Version | Model | Notes |
|----------|---------|-------|-------|
| Cursor   |         |       |       |
| Codex    |         |       |       |
| Claude Code |      |       |       |

## Description Checks

Record any `description` changes that may affect trigger behavior:

- Uses third-person phrasing
- Includes both what the skill does and when to use it
- Includes specific trigger terms instead of vague wording

## Test Cases

Use cases from `maintainer/data/trigger_test_data.py`. For each case, record the result on each platform.

### Case Template

```text
Case ID:
Category:
Prompt: <paste from trigger_test_data.py>

| Platform    | Expected Triggers       | Actual Triggers         | Expected Non-Triggers   | Actual Non-Triggers     | Result       |
|-------------|-------------------------|-------------------------|-------------------------|-------------------------|--------------|
| Cursor      |                         |                         |                         |                         | pass/partial/miss/fail |
| Codex       |                         |                         |                         |                         | pass/partial/miss/fail |
| Claude Code |                         |                         |                         |                         | pass/partial/miss/fail |
```

### Scoring

| Result    | Meaning |
|-----------|---------|
| `pass`    | All expected triggers fired, no expected non-triggers fired |
| `partial` | Expected triggers fired but one or more non-triggers also fired (false positive) |
| `miss`    | One or more expected triggers did not fire (false negative) |
| `fail`    | Expected triggers did not fire AND unexpected skills fired |

## Summary Matrix

| Case ID | Category | Cursor | Codex | Claude Code |
|---------|----------|--------|-------|-------------|
|         |          |        |       |             |

## Aggregate Scores

| Platform    | Total Cases | Pass | Partial | Miss | Fail | Pass Rate |
|-------------|-------------|------|---------|------|------|-----------|
| Cursor      |             |      |         |      |      |           |
| Codex       |             |      |         |      |      |           |
| Claude Code |             |      |         |      |      |           |

## Observations

- Platform-specific differences:
- Model-specific differences:
- Skills with lowest trigger accuracy:
- Recommended description changes:

## Follow-Up Actions

-
