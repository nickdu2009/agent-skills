# Claude Interactive Test Implementation Plan

This plan turns the interactive checklist into a repeatable maintainer workflow.
The target is not "Claude can load a skill" because the non-interactive trigger
smoke suite already covers that. The target is "Claude enters the right working
mode in a realistic multi-turn session."

## Why This Approach

Two simpler alternatives were rejected:

- Reusing an empty temporary directory with only `.claude/skills/`.
  This is too sparse for code-oriented prompts and often causes Claude to stop at
  "where is the real project?" instead of demonstrating the intended skill.
- Driving the full-screen interactive TTY directly.
  This is brittle because workspace-trust prompts, alternate-screen rendering,
  and timing make transcript capture unstable.

The safer approach is:

- keep the canonical `skills/` tree as the source of truth
- mirror those skills into a clean temporary Claude workspace
- seed that workspace from a small synthetic fixture repository
- run multi-turn acceptance scenarios with `claude -p` plus session resume
- treat the resulting transcripts as the reproducible baseline

This preserves the important part of interactive testing, which is multi-turn
state and behavior, without depending on fragile terminal scraping.

## Assumptions

- Maintainers have a working `claude` CLI session on the local machine.
- The local Claude default model may drift, so runs should explicitly pin
  `--model sonnet`.
- A small synthetic workspace is sufficient for interactive acceptance, as long
  as it exposes the code surfaces referenced by the scenarios.
- The baseline is maintainer-facing, not end-user-facing.

## Constraints

- The workflow must not require a heavyweight harness or external services beyond
  the local Claude CLI.
- The canonical `skills/` tree remains the only skill source of truth.
- Scenario execution must stay isolated from this repository's own maintainer
  examples and trigger fixtures.
- The implementation must be reproducible from the repository itself.

## Inputs And Outputs

Inputs:

- `skills/`
- `docs/maintainer/claude-interactive-test-checklist.md`
- `maintainer/fixtures/claude-interactive-workspace/`
- `maintainer/scripts/evaluation/run_claude_interactive_mainline.py`

Outputs:

- a JSON run report under `maintainer/reports/runs/`
- a durable Markdown baseline under `maintainer/reports/baselines/`
- a maintainer-readable plan and execution record

## Boundary Conditions

- Each scenario starts from a fresh copy of the fixture workspace.
- Multi-turn continuity is per scenario, not shared across the full suite.
- `phase-plan -> phase-execute` is allowed to edit the temporary workspace.
- Interactive acceptance scoring is separate from trigger-only scoring.
- Repository-root reruns are optional control tests, not the primary baseline.

## Failure Scenarios

- Claude returns a valid answer but does not demonstrate the intended skill behavior.
- Claude fixates on the wrong part of the fixture because the prompt is too broad
  or the fixture is too weak.
- Phase scenarios fail to create or consume the expected artifacts.
- Resume semantics break and later rounds lose state.
- CLI execution hangs or asks for permission in a way the harness cannot satisfy.

## Module Boundaries

- `docs/maintainer/claude-interactive-test-checklist.md`
  Human checklist and manual scoring rubric.
- `docs/maintainer/claude-interactive-test-implementation-plan.md`
  Maintainer strategy, scope, and execution contract.
- `maintainer/fixtures/claude-interactive-workspace/`
  Synthetic repository used as the stable acceptance substrate.
- `maintainer/scripts/evaluation/run_claude_interactive_mainline.py`
  Fixture-backed multi-turn Claude runner.
- `maintainer/reports/runs/`
  Raw JSON transcripts and scratch outputs.
- `maintainer/reports/baselines/`
  Small durable summaries promoted from trusted runs.

## Data Flow

1. Copy the synthetic fixture workspace into a new temporary directory.
2. Mirror canonical `skills/` into `.claude/skills/` inside that workspace.
3. Start the first scenario round with `claude -p`.
4. Resume the same scenario session for subsequent rounds using the returned
   session ID.
5. Capture JSON output, cost, and stderr per round.
6. Score the scenario with lightweight heuristics plus maintainer review.
7. Promote the trusted run into a Markdown baseline.

## Control Flow

1. Validate the runner can list scenarios.
2. Execute all primary scenarios in fresh fixture workspaces.
3. Inspect raw outputs for scoring and edge cases.
4. Write the baseline report.
5. Use the baseline for later regression comparisons.

## Scenario Set

Primary scenarios:

1. `scoped-tasking -> plan-before-action`
2. `context-budget-awareness`
3. `multi-agent-protocol`
4. `phase-plan -> phase-execute`
5. `conflict-resolution`

Supplementary scenarios:

1. `phase-contract-tools`
2. Negative control

## Execution Policy

- Use `--model sonnet` for all baseline runs.
- Use `--permission-mode acceptEdits` so document-driven phase flows can write
  their temporary artifacts.
- Set `stdin` to `DEVNULL` in the harness so Claude does not accidentally ingest
  the parent script contents.
- Use `--resume <session-id>` for later rounds instead of reusing a live TTY.
- Prefer JSON output over text so session IDs, cost, and error state are easy to
  capture.

## Validation

Smallest sufficient validation:

- `python3 maintainer/scripts/evaluation/run_claude_interactive_mainline.py --list-scenarios`
- `python3 maintainer/scripts/evaluation/run_claude_interactive_mainline.py`
- inspect the generated JSON report
- check the promoted Markdown baseline for pass, partial, and fail calls

Residual manual step:

- Maintainer review is still required before promoting a run to `baselines/`
  because interactive behavior scoring is not fully automatable.

## Done Criteria

The implementation is complete when:

- the fixture-backed runner exists and executes the full scenario set
- the checklist points to the maintained workflow
- maintainer docs explain why the runner uses a fixture-backed surrogate instead
  of raw TTY scraping
- one baseline run has been captured and summarized in Markdown
