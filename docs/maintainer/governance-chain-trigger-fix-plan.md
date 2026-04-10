# Governance Chain Trigger Fix Plan

Status: Proposed
Date: 2026-04-10

## Problem Summary

Analysis of all 18 SKILL.md files against three governance sources (CLAUDE-template, AGENTS-template, repo CLAUDE.md) revealed 6 categories of issues in the Skill Escalation, Skill Lifecycle, and skill-to-skill chain trigger rules.

## Issue 1: Template Escalation Rules Inconsistent

| Source | Escalation Rules | Missing |
|--------|:---:|---------|
| CLAUDE-template | 3 | design-before-plan, impact-analysis, self-review, incremental-delivery |
| AGENTS-template | 6 | design-before-plan |
| CLAUDE.md (repo root) | 7 | (none) |

**Fix:** Unify all three to 7 rules:

```
- Escalate to `design-before-plan` when: the task involves choosing between multiple implementation
  approaches, the change introduces or modifies a public API or cross-module contract, acceptance
  criteria are missing or unclear, scoped-tasking identified the boundary but design decisions remain
  open, or impact-analysis revealed 3+ affected modules requiring contract coordination.
- Escalate to `minimal-change-strategy` when: the diff is growing beyond what the task requires,
  multiple edit strategies compete, or surrounding code tempts drive-by cleanup.
- Escalate to `context-budget-awareness` when: the working set exceeds 8 files, the same file has
  been read more than twice without a new question, more than 3 hypotheses are active without ranking
  evidence, or the last 3 actions did not advance the stated objective.
- Escalate to `targeted-validation` when: multiple validation options exist and the cheapest meaningful
  check needs deliberate selection, validation is expensive and the change is local enough for a
  narrower check, or a validation failure needs diagnosis before broadening coverage.
- Escalate to `impact-analysis` when: the change touches a function or interface with 3+ callers,
  involves a public API or shared type, modifies a data model used across multiple modules, or
  read-and-locate produced 3+ tentative leads.
- Escalate to `self-review` when: edits span multiple files and are complete, or the user requests a
  diff review before testing.
- Escalate to `incremental-delivery` when: the plan from plan-before-action spans 2-4 PRs across 1-2
  modules and can be delivered serially.
```

Note: `design-before-plan` gains one new trigger condition from its SKILL.md that no template currently
has: "impact-analysis revealed 3+ affected modules requiring contract coordination."

## Issue 2: Template Lifecycle Rules Inconsistent

| Source | Lifecycle Rules | Missing |
|--------|:---:|---------|
| CLAUDE-template | 7 | design-before-plan, bugfix-workflow, safe-refactor, impact-analysis, self-review, incremental-delivery |
| AGENTS-template | 10 | design-before-plan, bugfix-workflow, safe-refactor |
| CLAUDE.md (repo root) | 11 | bugfix-workflow, safe-refactor |

**Fix:** Unify all three to 13 rules. Add:

```
- Drop `design-before-plan` after the design brief is produced and handed to plan-before-action --
  it does not stay active during implementation.
- Drop `bugfix-workflow` once the root cause is confirmed and the fix is handed off to implementation.
- Drop `safe-refactor` once the structural goal is met and invariants are intact.
- Drop `impact-analysis` after plan-before-action produces the plan.
- Drop `self-review` after the diff review passes with no blocking issues.
- Drop `incremental-delivery` after the increment list is finalized -- it provides structure, not
  ongoing execution guidance.
```

## Issue 3: Task-Type Activation Not Documented

Skills like `bugfix-workflow`, `safe-refactor`, `scoped-tasking`, `read-and-locate`, and
`plan-before-action` activate based on task characteristics, not escalation from base rules.
This distinction is not documented in any template.

**Fix:** Add a new "Skill Activation" section before "Skill Escalation":

```markdown
## Skill Activation

Skills activate through two mechanisms:

- **Task-type activation**: `bugfix-workflow`, `safe-refactor`, `scoped-tasking`, `read-and-locate`,
  and `plan-before-action` activate based on task characteristics recognized during
  `[trigger-evaluation]`. Their SKILL.md descriptions define when they match.
- **Mid-task escalation**: The rules below define when base-level governance rules prove insufficient
  and the agent should load the full skill during execution.
```

## Issue 4: SKILL.md Deactivation Triggers Contradict Lifecycle

| Skill | Template Lifecycle | SKILL.md Deactivation Trigger | Contradiction |
|-------|-------------------|------------------------------|---------------|
| `minimal-change-strategy` | "Keep active until the task is complete" | "Deactivate when the patch has been applied and the guarded boundary is no longer needed" | SKILL.md allows earlier exit |
| `targeted-validation` | "Keep active until the task is complete" | "Deactivate after the chosen targeted check has run and the result is recorded" | SKILL.md allows earlier exit |

**Fix:** Update the first deactivation trigger in each SKILL.md:

- `minimal-change-strategy`: Change to "Deactivate when the task is complete and no further patches
  need scope constraint."
- `targeted-validation`: Change to "Deactivate when the task is complete and no further validation
  cycles are expected."

## Issue 5: Skill Chain Triggers Not Centrally Documented

The 18 SKILL.md files define 33 skill-to-skill transitions (10 forward, 20 fallback, 3 orchestration)
in their Composition and Fallback sections. Agents can only see these after loading each skill,
missing critical transition signals at `[trigger-evaluation]` time.

**Fix:** Add a new "Skill Chain Triggers" section after "Skill Lifecycle" with three subsections.

### 5a. Common Flow Patterns

```
Bug fix:       scoped-tasking -> read-and-locate -> bugfix-workflow -> minimal-change-strategy -> self-review -> targeted-validation
Refactor:      scoped-tasking -> safe-refactor + minimal-change-strategy -> self-review -> targeted-validation
Multi-file:    scoped-tasking -> plan-before-action -> minimal-change-strategy -> self-review -> targeted-validation
Design-first:  scoped-tasking -> design-before-plan -> plan-before-action -> minimal-change-strategy -> self-review -> targeted-validation
Large task:    scoped-tasking -> design-before-plan -> impact-analysis -> plan-before-action -> incremental-delivery
Parallel:      multi-agent-protocol -> [subagents] -> conflict-resolution (if needed) -> synthesis
```

### 5b. Forward Handoffs (7 entries)

| From | To | Condition |
|------|----|-----------|
| `scoped-tasking` | `read-and-locate` | Boundary known but edit point still unknown |
| `scoped-tasking` | `plan-before-action` | Boundary confirmed, ready for implementation planning |
| `read-and-locate` | `plan-before-action` | Edit points identified, ready for sequencing |
| `design-before-plan` | `plan-before-action` | Design brief produced, ready for implementation planning |
| `impact-analysis` | `plan-before-action` | Impact summary produced, ready for sequencing |
| `self-review` | `targeted-validation` | Diff clean of blocking issues, ready for behavioral verification |
| `plan-before-action` | `incremental-delivery` | Plan spans 2-4 PRs that can be split into independently mergeable increments |

### 5c. Fallbacks (19 entries)

| From | To | Condition |
|------|----|-----------|
| `bugfix-workflow` | `read-and-locate` | Failure path is still unknown |
| `bugfix-workflow` | `context-budget-awareness` | Diagnosis is spinning across too many files or hypotheses |
| `minimal-change-strategy` | `design-before-plan` | Preserving the current interface may itself be the bug |
| `minimal-change-strategy` | `impact-analysis` | Supposedly local change affects multiple callers or contracts |
| `safe-refactor` | `design-before-plan` | Structural change implies interface redesign |
| `safe-refactor` | `minimal-change-strategy` | Only local cleanup is justified, not structural refactoring |
| `safe-refactor` | `read-and-locate` | Ownership seams still unclear |
| `self-review` | `minimal-change-strategy` | Review reveals the patch grew beyond task scope |
| `context-budget-awareness` | `scoped-tasking` | Compressed state shows the objective itself is too broad |
| `plan-before-action` | `design-before-plan` | Design choices, not execution order, are the real blocker |
| `plan-before-action` | `scoped-tasking` / `read-and-locate` | Edit surface still uncertain, return to discovery |
| `design-before-plan` | `impact-analysis` | Caller or module impact is still speculative |
| `design-before-plan` | `scoped-tasking` | Task boundary itself is unstable |
| `impact-analysis` | `read-and-locate` | True edit point is not stable |
| `impact-analysis` | `phase-plan` | Contract migration becomes multi-stage or externally constrained |
| `incremental-delivery` | `phase-plan` | Task exceeds 4 increments, 2 modules, or needs parallel lanes |
| `incremental-delivery` | `plan-before-action` | Downgrade -- task fits in a single PR |
| `multi-agent-protocol` | `conflict-resolution` | Subagent findings disagree materially |
| `conflict-resolution` | `targeted-validation` | Adjudication requires an empirical check |

### 5d. Not Included (intentional exclusions)

| Chain | Reason for exclusion |
|-------|---------------------|
| Phase-internal chains (P1-P7) | Self-contained system; documented in phase skill Composition sections |
| Composition "combine with" (co-active) | Not directional transitions; agents learn from SKILL.md when loaded |
| `impact-analysis` -> `design-before-plan` (3+ modules) | Already covered by Escalation rule for `design-before-plan` |
| `read-and-locate` -> `bugfix-workflow` (fault isolation) | Low frequency; agent recognizes task type directly |
| `design-before-plan` -> `incremental-delivery` (multi-PR) | Low frequency; handled via plan-before-action as intermediary |
| `impact-analysis` -> `safe-refactor` (invariants) | Indirect; flows through plan-before-action |
| `context-budget-awareness` -> `plan-before-action` (compact again) | Implied by lifecycle rules |

## Issue 6: Trigger Test Coverage Gaps

The `trigger_test_data.py` combo-trigger category has 3 test cases but does not cover the chain
triggers identified in Issue 5. Chain trigger tests would verify that agents correctly activate
skill B when skill A produces a specific output or failure condition.

**Recommended new test cases for `trigger_test_data.py`:**

| ID | Prompt | Expected Triggers | Category |
|----|--------|------------------|----------|
| `chain-scope-to-locate` | "We've narrowed the task to the auth module, but I don't know which file handles token refresh." | `read-and-locate` (not `scoped-tasking`) | chain-trigger |
| `chain-locate-to-plan` | "read-and-locate found the edit points: auth/token.ts and auth/session.ts. Now I need a plan for the changes." | `plan-before-action` (not `read-and-locate`) | chain-trigger |
| `chain-bugfix-to-cba` | "I've been diagnosing this bug for a while, checked 10 files, and I have 4 competing theories but no evidence to rank them." | `context-budget-awareness` (not `bugfix-workflow`) | chain-trigger |
| `chain-review-to-validation` | "Self-review is clean -- no blocking issues in the diff. What should I test?" | `targeted-validation` (not `self-review`) | chain-trigger |
| `chain-plan-to-design` | "I tried to plan the implementation but realized I can't sequence the steps because there are two competing design approaches." | `design-before-plan` (not `plan-before-action`) | chain-trigger |
| `chain-minimal-to-impact` | "I was making a small fix to the validator, but it turns out 5 other modules import this function." | `impact-analysis` (not `minimal-change-strategy`) | chain-trigger |
| `chain-refactor-to-design` | "I started extracting the shared helper but realized the refactor changes the module's public interface." | `design-before-plan` (not `safe-refactor`) | chain-trigger |
| `chain-parallel-to-conflict` | "Two subagents disagree: one says the timeout is in the client, the other blames the server." | `conflict-resolution` (not `multi-agent-protocol`) | chain-trigger |

## File Change Summary

| File | Changes |
|------|---------|
| `templates/governance/CLAUDE-template.md` | +Skill Activation section, +4 Escalation rules, +6 Lifecycle rules, +Skill Chain Triggers section |
| `templates/governance/AGENTS-template.md` | +Skill Activation section, +1 Escalation rule, +3 Lifecycle rules, +Skill Chain Triggers section |
| `CLAUDE.md` | +Skill Activation section, +1 design-before-plan condition, +2 Lifecycle rules, +Skill Chain Triggers section |
| `skills/minimal-change-strategy/SKILL.md` | Fix deactivation trigger #1 |
| `skills/targeted-validation/SKILL.md` | Fix deactivation trigger #1 |
| `maintainer/data/trigger_test_data.py` | +8 chain-trigger test cases |

## Implementation Order

1. Fix Issues 1-3 (Escalation + Lifecycle + Activation) -- these are preconditions for Chain Triggers
2. Fix Issue 4 (SKILL.md deactivation contradictions)
3. Fix Issue 5 (Chain Triggers section)
4. Fix Issue 6 (trigger test cases)
5. Run `manage-governance.py --sync-local claude --check` and `--sync-local cursor --check`
6. Run `run_trigger_tests.py --mode report` to verify new test cases
