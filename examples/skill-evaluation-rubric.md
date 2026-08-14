# Skill Evaluation Rubric

## Scenario

You want a repeatable scoring standard for reviewing whether an agent actually demonstrated the intended skill behavior during a scenario run.

## Recommended Skill Composition

- `scoped-tasking`
- `targeted-validation`

Planning behavior is scored against the lightweight inline-plan contract for small tasks and against `implementation-planning` for durable implementation plans.

## Review Model

```mermaid
flowchart TD
    A[Run scenario] --> B[Score global dimensions]
    B --> C[Score skill-specific signals]
    C --> D[Record failures and residual risk]
    D --> E[Decide pass, conditional pass, or fail]
```

## Scoring Scale

| Score | Meaning |
| --- | --- |
| `2` | Clearly demonstrated and materially useful |
| `1` | Partially demonstrated, ambiguous, or inconsistently applied |
| `0` | Missing, contradicted, or replaced by the opposite behavior |

## Global Dimensions

Score these dimensions for every scenario:

| Dimension | Pass Signal | Failure Signal |
| --- | --- | --- |
| Scope discipline | The agent stays inside the smallest justified boundary | The agent drifts into broad exploration without evidence |
| Planning discipline | The agent states assumptions, working set, and intended sequence before editing | The agent edits before a clear plan exists |
| Change discipline | The agent prefers the smallest viable change or recommendation | The agent bundles unrelated cleanup or broad rewrites |
| Validation discipline | The agent chooses the narrowest meaningful check first | The agent defaults to broad validation without justification |
| Uncertainty handling | The agent preserves ambiguity and residual risk | The agent overclaims confidence or collapses conflicting evidence |
| Skill lifecycle | Skills are loaded on demand and dropped when their phase ends; no more than 4 active simultaneously without justification | Unnecessary skills are carried throughout the session; the context budget grows from stale skill guidance |

## Skill-Specific Pass vs. Fail

### `scoped-tasking`

- Pass: proposes a bounded initial working set and explains each scope expansion.
- Fail: scans widely by reflex or expands scope without stating why.

### Lightweight Inline Plan

- Pass: states goal, assumptions, intended files, and per-step verify checks before non-trivial edits.
- Fail: starts editing while the plan or verify steps are still fuzzy.

### `implementation-planning`

- Pass: produces a durable plan artifact with ordered steps, file landing, per-step verify checks, rollback notes, and acceptance traceability.
- Fail: stops at a short inline plan, leaves file landing vague, or omits rollback / acceptance coverage for multi-file work.

- Pass: selects a local, reviewable patch and defers unrelated cleanup.
- Fail: mixes the main task with cosmetic rewrites, renames, or opportunistic refactors.

### `targeted-validation`

- Pass: first validation step directly exercises the changed or analyzed surface.
- Fail: jumps to full builds or broad test suites without explicit risk-based reasoning.

- Pass: compresses the session state, drops stale hypotheses, and resumes from a smaller fault domain.
- Fail: preserves dead ends and keeps re-reading noisy artifacts without a sharper question.

- Pass: starts from the strongest clue and identifies likely edit points without repo-wide drift.
- Fail: reads large unrelated areas before establishing the local ownership path.

### `safe-refactor`

- Pass: states invariants and performs behavior-preserving structural changes in small steps.
- Fail: silently changes interfaces, output shape, or user-visible behavior.

### `bugfix-workflow`

- Pass: clarifies the symptom and fault domain before applying a fix.
- Fail: patches speculative causes without confirming the failure path.

### `multi-agent-protocol`

- Pass: selects read-only or write-capable delegation appropriately, uses an explicit gate for write-capable delegation, and defines clear assignments and merge expectations.
- Fail: splits tightly coupled work, launches overlapping write scopes, skips the write-capable gate, or conflates exploration with delegated modification.

- Pass: compares overlapping findings by evidence quality and preserves uncertainty where needed.
- Fail: collapses conflicting findings into one answer without adjudication or confidence notes.

### `impact-analysis`

- Pass: traces outward from edit point, produces structured impact summary with blast radius, stops at framework boundaries or 8-file threshold.
- Fail: skips impact assessment and goes directly to planning, or reads the entire repo during impact analysis.

- Pass: `implementation-planning` splits the work into 2–4 mergeable increments with explicit dependencies and acceptance criteria; each increment keeps the system runnable; escalates to `design-before-plan` or asks the user when the work outgrows simple incremental delivery.

### `artifact-review-loop` self-delivery routing

- Pass: reviews diff before testing, catches debug residuals and out-of-scope changes, uses severity grading (blocking vs warning), fixes blocking issues before proceeding to validation.
- Fail: skips diff review and goes directly to testing, or treats all issues as equal severity, or leaves debug code in the diff.

## Trigger Accuracy

Trigger accuracy measures whether the agent loaded the correct skills before execution. Score these separately from execution behavior.

| Dimension | Pass Signal | Failure Signal |
| --- | --- | --- |
| True positive | The agent loaded a skill that the scenario requires | |
| True negative | The agent did not load a skill that the scenario excludes | |
| False negative | | The agent failed to load a required skill |
| False positive | | The agent loaded a skill that was not needed and added noise |

### Trigger Scoring

| Score | Meaning |
| --- | --- |
| `2` | All expected skills loaded, no unexpected skills loaded |
| `1` | Expected skills loaded but one or more unexpected skills also loaded (false positive) |
| `0` | One or more expected skills were not loaded (false negative) |

A false negative is worse than a false positive. If the agent never loads the skill, the skill's guidance is entirely absent. If the agent loads an extra skill, the cost is context waste but the intended guidance is still present.

### Lightweight Planning Boundary Cases

Verify that simple, bounded tasks stay on a direct-execution path while non-trivial tasks load the appropriate Skill instead of relying on an external governance file.

| Score | Meaning |
| --- | --- |
| `2` | Simple tasks stayed direct; complex tasks loaded the appropriate Skill |
| `1` | The agent loaded a full Skill for a trivial task, but still loaded the required Skill for complex work |
| `0` | A complex task did not load the required Skill, or depended on external governance instead of the Skill package |

### Chain Trigger Cases

| Score | Meaning |
| --- | --- |
| `2` | The skill was loaded only through its intended entry point |
| `1` | The skill was loaded directly but the parent skill was also present |
| `0` | The skill was loaded directly without the parent skill, or the parent skill failed to load it when needed |

## Decision Rule

### Execution Decision Rule

- Pass: no critical dimension scores `0`, and the primary skills under review mostly score `2`.
- Conditional pass: no critical safety issue exists, but one or more primary skills score `1`.
- Fail: any primary skill clearly scores `0`, or the execution pattern contradicts the skill intent.

### Trigger Decision Rule

- Pass: trigger accuracy is `2` across all tested cases.
- Conditional pass: trigger accuracy is `1` on some cases (false positives only, no false negatives).
- Fail: trigger accuracy is `0` on any case (false negatives present).

## Guardrails

- Do not average away a critical failure with strong performance elsewhere.
- Do not score only the final answer; score the execution behavior.
- Do not upgrade a `1` to a `2` unless the pass signal is clearly visible in the transcript.
- If evidence is missing, record uncertainty instead of guessing the score.
- Do not conflate trigger accuracy with execution quality. A skill that triggered correctly but was followed poorly is a behavior issue, not a trigger issue.

## Skill Protocol v2 Evidence Capture

Use protocol blocks as first-class scoring evidence instead of relying on prose impressions alone.

```text
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[triggers: scoped-tasking:trigger | targeted-validation:trigger]
[precheck: targeted-validation | result:PASS | checks:protocol-blocks-present expected-skills-known]
[output: targeted-validation | status:completed | confidence:high | command:"score the transcript against protocol lifecycle and skill rubric" reason:"visible compact blocks provide repeatable evidence" residual_risk:"the transcript cannot prove hidden internal reasoning" | next:scoped-tasking]
[validate: targeted-validation | result:PASS | checks:command reason residual_risk]
[drop: targeted-validation | reason:"transcript scoring checklist applied" | active:scoped-tasking]
```
