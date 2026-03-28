# Trigger Test Baseline Report

> Date: 2026-03-28
> Tester: automated (run_trigger_tests.py --mode api)
> Model: gpt-5.4
> Skill revision: current HEAD
> Total cases: 27

## Results Summary

| Metric | Value |
|--------|-------|
| Pass | 24 |
| Partial | 1 |
| Fail | 2 |
| Pass rate | 88.9% |

## Full Results

| Case ID | Category | Result | Issues |
|---------|----------|--------|--------|
| bug-explicit | task-type | pass | |
| bug-implicit | task-type | pass | |
| refactor-explicit | task-type | pass | |
| feature-not-bug | task-type | pass | |
| simple-one-file-fix | agents-md-boundary | pass | |
| multi-file-uncertain | agents-md-boundary | pass | |
| broad-request-small-surface | agents-md-boundary | pass | |
| temptation-to-cleanup | agents-md-boundary | pass | |
| diff-growing-beyond-task | agents-md-boundary | pass | |
| what-to-test-after-patch | agents-md-boundary | pass | |
| simple-test-request | agents-md-boundary | pass | |
| unfamiliar-codebase | discovery | pass | |
| known-file | discovery | pass | |
| partial-path-known | discovery | pass | |
| grep-sufficient | discovery | partial | FALSE POSITIVE: read-and-locate triggered but should not |
| long-session-refocus | context-budget | pass | |
| short-task-no-noise | context-budget | pass | |
| many-files-opened | context-budget | fail | FALSE NEGATIVE: context-budget-awareness not triggered |
| repeated-hypothesis | context-budget | fail | FALSE NEGATIVE: context-budget-awareness not triggered |
| medium-session-focused | context-budget | pass | |
| parallel-investigation | multi-agent | pass | |
| implicit-parallel-opportunity | multi-agent | pass | |
| serial-single-file | multi-agent | pass | |
| conflicting-subagent-results | multi-agent | pass | |
| plan-large-migration | phase | pass | |
| execute-wave | phase | pass | |
| contract-tools-direct | phase | pass | |

## By Category

| Category | Total | Pass | Partial | Fail | Pass Rate |
|----------|-------|------|---------|------|-----------|
| task-type | 4 | 4 | 0 | 0 | 100% |
| agents-md-boundary | 7 | 7 | 0 | 0 | 100% |
| discovery | 4 | 3 | 1 | 0 | 75% |
| context-budget | 5 | 3 | 0 | 2 | 60% |
| multi-agent | 4 | 4 | 0 | 0 | 100% |
| phase | 3 | 3 | 0 | 0 | 100% |

## Analysis

### Failures

**context-budget category (2 fails)**:
The `context-budget-awareness` skill description does not trigger for prompts describing mid-session symptoms like "read 12 files without convergence" or "checked the same areas multiple times." The description focuses on when to *use* the skill, but the prompts simulate user frustration *within* a session — a signal that depends on session state, not just the initial prompt. This is a known limitation: trigger tests evaluate cold-start prompt matching, while `context-budget-awareness` is designed to activate from accumulated session context.

**Recommendation**: The `many-files-opened` and `repeated-hypothesis` cases may need to be reclassified as "session-state triggers" that cannot be reliably tested via single-prompt evaluation. Alternatively, the `context-budget-awareness` description could be expanded to mention symptoms like "many files read without convergence" or "repeated investigation of the same areas."

### Partial

**grep-sufficient (1 partial)**:
`read-and-locate` triggered because the prompt mentions updating "all callers" across the codebase, which resembles a discovery task. The description overlap between `read-and-locate` ("find where code lives") and a grep-based rename is a known fuzzy boundary.

**Recommendation**: Acceptable false positive. The cost is minor context waste; the agent would still use grep. No description change needed.

## Follow-Up Actions

- Consider expanding `context-budget-awareness` description to cover mid-session symptom keywords
- Re-run after any description changes to establish a new baseline
- Run the same test matrix on Cursor/Codex/Claude Code platforms for cross-platform data (see `templates/evaluation/cross-platform-trigger-baseline.md`)
