# Claude Code Interactive Test Checklist

Use this checklist when you want to validate skill behavior in Claude Code's interactive mode rather than relying only on `claude -p` smoke tests.

This is a maintainer-facing acceptance checklist. It focuses on the highest-value multi-turn scenarios: skill boundary decisions, context compression, parallelism decisions, and phase-system handoffs.

## Why This Exists

Non-interactive trigger checks are still the best regression baseline, but they miss some of the most important real-world behaviors:

- multi-turn skill escalation
- context growth and later compression
- permission-gated phase behavior
- parallel vs serial decision quality
- handoff behavior between related skills

Use this checklist as a complement to the static mirror checks and prompt-based smoke tests described in [`README.md`](../../README.md).

## Test Setup

Prefer a clean temporary workspace backed by a small synthetic fixture
repository. An empty directory with only `.claude/skills/` is often too sparse
for code-oriented scenarios and can cause Claude to stop at "please point me at
the real project" instead of demonstrating the target skill behavior.

For the maintained fixture-backed workflow, use:

```bash
python3 maintainer/scripts/evaluation/run_claude_interactive_mainline.py --list-scenarios
python3 maintainer/scripts/evaluation/run_claude_interactive_mainline.py
```

For a manual session against the same fixture, start from a clean temporary workspace:

```bash
tmpdir=$(mktemp -d)
cp -R /path/to/agent-skills/maintainer/fixtures/claude-interactive-workspace/. "$tmpdir/"
mkdir -p "$tmpdir/.claude/skills"
cp -R /path/to/agent-skills/skills/* "$tmpdir/.claude/skills/"
cd "$tmpdir"
claude --model sonnet
```

Notes:

- Use an explicit model such as `sonnet` so trigger behavior is not coupled to local default-model drift.
- If you intentionally want to test "inside the skill repository itself," record that as a separate run because repository context can change trigger quality.
- If you intentionally use an empty temporary workspace, record that too. Empty-workspace results are useful as a control, but they should not be treated as the primary acceptance baseline for code-oriented skills.
- For phase scenarios, note whether Claude had write permission when you scored the result.

## Scoring

Use these labels:

- `pass`: the target skill behavior clearly appeared and the response stayed on the intended path
- `partial`: the response moved in the right direction but was diluted by context mismatch, permission gating, or extra non-target behavior
- `fail`: the response missed the intended skill behavior or clearly followed the wrong workflow

## High-Value Scenarios

### 1. `scoped-tasking` -> `plan-before-action`

Purpose:
Confirm that a broad request is first narrowed, then upgraded into an explicit plan once the working set becomes multi-file and uncertain.

Round 1 prompt:

```text
Look into the performance issues across the reporting, billing, and notification systems — users say the daily summary email is slow.
```

Round 2 prompt:

```text
We will probably need changes in the service layer, client wrapper, and tests. I'm not sure where the timeout config lives.
```

Pass signals:

- Round 1 narrows the task boundary instead of scanning everything
- Round 2 introduces scope, assumptions, likely files/modules, and intended action order
- The agent does not jump straight into implementation

Failure signals:

- Immediate repo-wide exploration with no boundary
- No upgrade from scoping to planning after uncertainty becomes explicit

### 2. `context-budget-awareness`

Purpose:
Verify that Claude can compress a noisy session into a useful summary instead of continuing to thrash.

Prompt sequence:

```text
We checked the cache twice and the queue config three times. Still no root cause.
```

```text
I have read about 12 files and the logging issue still does not connect to any handler.
```

```text
Let's step back and figure out what we actually know so far.
```

Pass signals:

- The response compresses state into knowns, unknowns, and next steps
- Repeated dead-end exploration is called out explicitly
- The working set is reduced rather than expanded

Failure signals:

- The agent keeps exploring without summarizing
- The answer becomes generic reassurance rather than state compression

### 3. `multi-agent-protocol`

Purpose:
Check that Claude recommends parallel work when the task is decomposable, and avoids it when the task is serial.

Positive prompt:

```text
Investigate the auth middleware, session storage, and role checking in parallel to understand the full auth flow.
```

Negative prompt:

```text
Fix the off-by-one error in pkg/runtime/replay.go.
```

Pass signals:

- Positive case proposes a split across distinct investigation tracks or subagents
- Negative case stays serial and does not force parallelism
- The agent distinguishes low-coupling work from single-file work

Failure signals:

- Parallelism is suggested for the single-file fix
- The positive case stays completely serial without justification

### 4. `conflict-resolution`

Purpose:
Validate that Claude asks for evidence, preserves uncertainty, and adjudicates by evidence quality rather than tone.

Round 1 prompt:

```text
Two subagents disagree: one says the cache invalidation path is broken, the other blames clock skew in expiry logic. Which is right?
```

Round 2 prompt:

```text
Subagent A cites cache.py:112-118. Subagent B only has log timing correlation.
```

Pass signals:

- Round 1 requests or frames the missing evidence instead of guessing
- Round 2 weighs direct code-path evidence above weaker correlation evidence
- Residual uncertainty is stated if still unresolved

Failure signals:

- Immediate certainty without asking for evidence
- The louder or more confident claim wins without comparison

### 5. `phase-plan` -> `phase-execute`

Purpose:
Confirm that the phase system behaves like a document-driven execution model rather than generic planning prose.

Round 1 prompt:

```text
Break down this database migration into phases. We need sequenced waves with clear ownership so multiple agents can work in parallel.
```

Round 2 prompt:

```text
Execute wave 2 of the phase 1 plan.
```

Pass signals:

- Round 1 enters phase-planning behavior: waves, ownership, ordering, execution docs
- If write access is missing, the response blocks on artifact creation rather than pretending the files exist
- Round 2 requires the accepted phase plan artifacts and explains the missing prerequisite if they do not exist

Failure signals:

- Generic migration advice with no phase execution contract
- Round 2 improvises execution with no plan file or accepted docs

### 6. `phase-contract-tools`

Purpose:
Verify the direct trigger path for phase-tooling maintenance tasks.

Prompt:

```text
Fix a validation error in the phase schema validator script.
```

Pass signals:

- The response treats the task as contract-tool maintenance
- Attention goes to validator/schema/renderer behavior, not generic planning
- The response does not bounce into `phase-plan` or `phase-execute` unless required by evidence

Failure signals:

- The answer becomes a generic phase-planning explanation
- The response ignores validator-level details entirely

### 7. Negative Control

Purpose:
Ensure a normal feature request does not spuriously trigger bugfix, refactor, or phase-system workflows.

Prompt:

```text
Add a dark mode toggle to the settings page.
```

Pass signals:

- The agent treats this as a normal feature request
- No obvious bugfix/refactor/phase workflow is injected without reason

Failure signals:

- Claude frames the task as a bugfix, refactor, or phase execution problem

## Suggested Run Order

If you want a short interactive acceptance pass, run these in order:

1. `scoped-tasking` -> `plan-before-action`
2. `context-budget-awareness`
3. `multi-agent-protocol`
4. `phase-plan` -> `phase-execute`
5. `conflict-resolution`

If you want one extra direct-tooling check, add `phase-contract-tools`.

## Reporting Template

Record each run in simple form:

```text
Scenario:
Workspace:
Model:
Permission state:
Result: pass | partial | fail
Observed behavior:
Residual risk:
```

If a result differs between:

- repository-root testing
- clean temporary workspace testing

record both. That difference often indicates repository-context interference rather than a true skill-format problem.
