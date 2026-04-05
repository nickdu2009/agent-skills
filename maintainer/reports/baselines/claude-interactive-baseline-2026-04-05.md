# Claude Interactive Baseline (2026-04-05)

> Date: 2026-04-05
> Evaluator: Codex
> Platform: Claude Code via `claude -p` plus `--resume`
> Model: `sonnet`
> Fixture workspace: `maintainer/fixtures/claude-interactive-workspace/`
> Runner: `maintainer/scripts/evaluation/run_claude_interactive_mainline.py`
> Raw run: `maintainer/reports/runs/claude-interactive-mainline-2026-04-05.json`

## Why This Baseline Exists

This baseline covers the highest-value Claude multi-turn acceptance path. It is
not a trigger-only check. It verifies that Claude enters the intended skill
working mode across multiple turns in a clean fixture-backed workspace.

The runner intentionally uses `claude -p` plus `--resume <session-id>` instead
of TTY scraping because direct interactive automation was unstable around
workspace-trust prompts and alternate-screen rendering.

## Validation Performed

- `python3 -m py_compile maintainer/scripts/evaluation/run_claude_interactive_mainline.py`
- `python3 maintainer/scripts/evaluation/run_claude_interactive_mainline.py --list-scenarios`
- targeted fixture-backed reruns while tuning noisy scenarios
- full fixture-backed scenario run:
  `python3 maintainer/scripts/evaluation/run_claude_interactive_mainline.py --output maintainer/reports/runs/claude-interactive-mainline-2026-04-05.json`

Approximate run cost from the saved JSON: `$2.18`.

## Scenario Results

| Scenario | Runner status | Reviewed status | Notes |
| --- | --- | --- | --- |
| `scoped-to-plan` | pass | conditional pass | Claude found the right files and timeout/config surfaces, but it still tends to jump into diagnosis faster than the ideal "scope first, then explicit plan" pattern. |
| `context-budget-awareness` | pass | pass | Final round compressed the session into knowns, unknowns, and the smallest next step. |
| `multi-agent-protocol` | warn | pass | Positive round explicitly used parallel investigation. Negative round stayed single-file and fixed the bug directly; the heuristic marked `warn` only because it expected explicit "serial" language. |
| `phase-plan-to-execute` | pass | pass | Claude created phase planning artifacts in the fixture workspace, then executed wave 2 against those artifacts. |
| `conflict-resolution` | pass | pass | First round asked for evidence; second round preferred direct code evidence over weaker timing correlation. |
| `phase-contract-tools` | pass | pass | Stayed focused on schema/validator maintenance and identified the `lane` vs `lanes` bug. |
| `negative-control` | pass | pass | Treated the prompt as a normal feature request rather than forcing a bugfix/refactor/phase workflow. |

## Overall Decision

### Heuristic result

- `6 pass`
- `1 warn`
- `0 fail`

### Reviewed result

The interactive baseline is a **pass**. All seven scenarios demonstrated the
intended Claude-side behavior at an acceptable level for maintainer regression
testing. The only remaining downgrade is heuristic, not behavioral.

## Residual Risk

- `scoped-to-plan` still over-indexes on immediate diagnosis. It reaches the
  right working set and plan inputs, but its first response is more action-heavy
  than the ideal skill pattern.
- `multi-agent-protocol` serial-path scoring is still somewhat literal. A future
  runner revision could treat a direct single-file fix with no parallel language
  as an automatic pass.
- `phase-plan-to-execute` is materially slower and more expensive than the other
  scenarios, so it is the main source of runtime variance.

## Follow-Up Actions

- Keep using the fixture-backed runner as the primary Claude interactive
  baseline.
- If runner noise becomes a problem again, refine heuristics before changing the
  scenario prompts.
- Use repository-root reruns only as a control, not as the canonical baseline.
