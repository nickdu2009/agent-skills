# Trigger Test Baseline Report (v2)

> Date: 2026-03-28
> Tester: automated (run_trigger_tests.py --mode api)
> Model: gpt-5.4
> Skill revision: post context-budget-awareness description optimization
> Previous baseline: trigger-baseline-2026-03-28.md (24 pass / 1 partial / 2 fail)
> Total cases: 27

## Results Summary

| Metric | v1 | v2 | Delta |
|--------|----|----|-------|
| Pass | 24 | 26 | +2 |
| Partial | 1 | 1 | 0 |
| Fail | 2 | 0 | -2 |
| Pass rate | 88.9% | 96.3% | +7.4pp |

## Change Made

Updated `context-budget-awareness` description from:

> Compress and refocus the working state when a session grows long, hypotheses accumulate, or the active file set expands beyond what the current step needs.

To:

> Compress and refocus the working state when an investigation is stuck or spinning — many files read without convergence, the same areas checked repeatedly without progress, hypotheses accumulating without evidence to rank them, or recent actions not advancing the objective. Use when the session has grown noisy and a fresh focused pass would be cheaper than carrying the full history forward.

Key additions: "stuck or spinning", "many files read without convergence", "same areas checked repeatedly without progress" — symptom-level language that matches mid-session user prompts.

## Full Results

| Case ID | Category | v1 | v2 | Change |
|---------|----------|----|----|--------|
| bug-explicit | task-type | pass | pass | |
| bug-implicit | task-type | pass | pass | |
| refactor-explicit | task-type | pass | pass | |
| feature-not-bug | task-type | pass | pass | |
| simple-one-file-fix | agents-md-boundary | pass | pass | |
| multi-file-uncertain | agents-md-boundary | pass | pass | |
| broad-request-small-surface | agents-md-boundary | pass | pass | |
| temptation-to-cleanup | agents-md-boundary | pass | pass | |
| diff-growing-beyond-task | agents-md-boundary | pass | pass | |
| what-to-test-after-patch | agents-md-boundary | pass | pass | |
| simple-test-request | agents-md-boundary | pass | pass | |
| unfamiliar-codebase | discovery | pass | pass | |
| known-file | discovery | pass | pass | |
| partial-path-known | discovery | pass | pass | |
| grep-sufficient | discovery | partial | partial | |
| long-session-refocus | context-budget | pass | pass | |
| short-task-no-noise | context-budget | pass | pass | |
| many-files-opened | context-budget | **fail** | **pass** | fixed |
| repeated-hypothesis | context-budget | **fail** | **pass** | fixed |
| medium-session-focused | context-budget | pass | pass | |
| parallel-investigation | multi-agent | pass | pass | |
| implicit-parallel-opportunity | multi-agent | pass | pass | |
| serial-single-file | multi-agent | pass | pass | |
| conflicting-subagent-results | multi-agent | pass | pass | |
| plan-large-migration | phase | pass | pass | |
| execute-wave | phase | pass | pass | |
| contract-tools-direct | phase | pass | pass | |

## By Category

| Category | Total | Pass | Partial | Fail | Pass Rate |
|----------|-------|------|---------|------|-----------|
| task-type | 4 | 4 | 0 | 0 | 100% |
| agents-md-boundary | 7 | 7 | 0 | 0 | 100% |
| discovery | 4 | 3 | 1 | 0 | 75% |
| context-budget | 5 | 5 | 0 | 0 | **100%** (was 60%) |
| multi-agent | 4 | 4 | 0 | 0 | 100% |
| phase | 3 | 3 | 0 | 0 | 100% |

## Remaining Partial

**grep-sufficient** (discovery): `read-and-locate` false positive — acceptable, no action needed (see v1 analysis).

## Regression Check

Zero regressions. All 24 previously passing cases still pass. No new partials or fails introduced.
