---
name: implementation-planning
description: "Guide implementation planning by turning a settled requirement/design into a concrete plan that is sequenced, file-grounded, verifiable, and reviewable. The skill writes or proposes a plan document, not production code. Use when a task is ready to implement but still needs explicit execution ordering, per-step validation, rollback thinking, or multi-file / multi-PR coordination. Accepts either a design brief or a requirement document whose design direction is already clear. Do NOT use for small single-file edits where AGENTS.md §4 short planning is enough, or when major design choices are still open (use design-before-plan first)."
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, planning"
---

# implementation-planning

Create a durable implementation plan before coding when lightweight inline planning is no longer enough.

This skill exists to handle the gap between "the design direction is settled" and "implementation can proceed safely." It produces a reviewable plan artifact with explicit sequencing, file-level landing, verification, and rollback notes.

# Purpose

Translate a settled requirement and/or design direction into an executable implementation plan. Core goals:

- Convert vague "we should do this next" thinking into ordered, verifiable steps.
- Ground each step in concrete files, modules, or interfaces rather than abstract intent.
- Preserve traceability from requirements / acceptance criteria to implementation steps.
- Make risks, rollback points, and sequencing explicit before code changes begin.
- Produce a plan artifact that can be handed to `plan-review-loop` or implementation directly.

Success criterion: on exit, the agent has produced a plan document specific enough that another agent could implement it without reopening major sequencing or ownership questions.

# When to Use

- The task spans multiple files, modules, or PR-sized increments.
- The design direction is already settled, but implementation ordering still matters.
- The user asks for an implementation plan / execution plan / task breakdown / 实施计划 / 执行计划.
- The work needs a written plan artifact before coding or review.
- Impact analysis has clarified the blast radius and now the changes must be sequenced.
- Requirements are clear enough to implement, but validation, rollback, or file landing is still implicit.

# When Not to Use

- For trivial or single-file edits where `AGENTS.md` Behavioral Guidelines §4 short planning is sufficient.
- When major design choices, contracts, or acceptance criteria are still unresolved — use `design-before-plan`.
- When the requirement itself is still vague or contradictory — use `requirement-interview`.
- When the user only wants artifact review of an existing plan — use `plan-review-loop`.
- When the user explicitly wants exploratory implementation ("try it first and see").

Boundary rule: this skill plans *how to execute an already-understood change*. It does not own business clarification or design comparison.

# Core Rules

- Do not write production code while planning.
- Do not reopen settled design questions unless a blocking inconsistency is discovered.
- Do not treat lightweight §4 short planning as a reason to activate this skill; this skill is for durable, reviewable planning.
- Every implementation step must name its landing surface and its verification.
- Every acceptance criterion must be covered by at least one planned step.
- Every non-trivial risk must have a mitigation or rollback note.

# Execution Pattern

0. **Check whether durable planning is actually needed**:
   - If the task is small, local, and obvious, defer to `AGENTS.md` §4 short planning instead of activating this skill.
   - If the task needs a real plan artifact, continue.

1. **Validate planning inputs**:
   - Collect available design brief, requirement doc, scoped boundary, and impact summary.
   - Decide whether the design direction is already settled enough to plan.
   - If not settled, hand off to `design-before-plan` or `requirement-interview`.

2. **Run the planning-clarification gate when needed**:
   - Ask only planning-layer questions first: increment boundaries, sequencing, validation preference, risk tolerance, rollback expectations, and plan file location.
   - Ask at most 3-5 questions per round.
   - If a major design or requirement gap is discovered, stop and hand back upstream instead of silently planning through it.

3. **Build the acceptance map**:
   - List the requirement / design acceptance criteria that must be covered.
   - Assign short identifiers (for example `AC1`, `AC2`) so steps can trace back to them.

4. **Decide the implementation structure**:
   - Determine whether the work is one pass, phased, or split into 2-4 mergeable increments.
   - Fill the §4-style `[parallelism: ...]` block for independent lanes, blockers, shared write surfaces, and delegation stance.

5. **Draft the executable steps**:
   - For each step, record: landing files/modules, dependency, action summary, verification check, and covered acceptance criteria.
   - Keep steps implementation-facing, not design-theory-facing.

6. **Add risk and rollback coverage**:
   - Identify critical failure points, sequencing hazards, compatibility risks, and rollback boundaries.
   - Add concrete mitigation and rollback notes to the plan artifact.

7. **Write or update the plan artifact**:
   - Prefer a dedicated Markdown plan file.
   - Default location: `.plans/<topic>-plan.md` unless the user specifies another path.

8. **Recommend the next step**:
   - Suggest `plan-review-loop` when the plan is non-trivial or high impact.
   - If the user wants to proceed directly, hand off to implementation with risks made explicit.

# Input Contract

Provide one or more of:

- a settled design brief from `design-before-plan`
- a requirement document / PRD / requirement-clarification result whose design direction is already clear
- a scoped boundary from `scoped-tasking`
- an impact summary from `impact-analysis`

Optional but helpful:

- preferred plan path or file location
- preferred validation style (unit / integration / manual)
- rollout / rollback constraints
- multi-PR or increment expectations

If the user provides only a file path to a requirement or design document, read that file before planning.

# Output Contract

Return:

- `sequence`: ordered implementation steps and dependency structure
- `file_landing`: the concrete files, modules, or interfaces each step touches
- `verify`: per-step and overall validation checks
- `risks`: rollback, mitigation, and residual implementation risks
- `traceability`: mapping from acceptance criteria to implementation steps

When writing a plan file, prefer this structure (Chinese template kept inline because the artifact is user-facing):

```markdown
# 实施计划：<主题>

## 来源与对齐
- 需求来源：<需求文档 / 澄清结果 / 路径>
- 设计来源：<设计简报 / 明确设计方向>
- 范围边界：本次做 … / 本次不做 …
- 设计取向假设（如适用）：
  - 【设计取向·假设】…（依据：…；若被推翻则回退 design-before-plan）

## 验收标准追溯
- AC1：… ← 来源：…
- AC2：…

## 并行规划
[parallelism:
- independent lanes: <parallel work, or none>
- sequential blockers: <must happen first>
- shared write surfaces: <single-owner files/modules>
- delegation: <delegate count, or 0 with reason>
]

## 实施步骤
### 步骤 1：<动作描述>
- 落地文件/模块：`path/to/file`
- 依赖：无 / 步骤 N
- 操作要点：…
- 验收检查（verify）：…
- 覆盖验收标准：AC1、AC2

### 步骤 2：<动作描述>
- 落地文件/模块：`path/to/file`
- 依赖：步骤 1
- 操作要点：…
- 验收检查（verify）：…
- 覆盖验收标准：AC3

## 风险与回滚
| 风险 | 关联步骤 | 影响 | 缓解 / 回滚策略 |
|---|---|---|---|
| … | 步骤 N | … | … |

## 验收标准覆盖检查
- AC1 → 步骤 1
- AC2 → 步骤 1

## 待确认 / 残留假设
- 【假设】…（验证方法：…）

## 下一步
- 建议运行 plan-review-loop 审查本计划，再进入实现。
```

# Guardrails

- Do not activate this skill just to produce a 2-3 bullet short plan; that belongs to `AGENTS.md` §4.
- Do not silently make business or design decisions under the label of planning.
- Do not leave step landing vague ("update backend") when a narrower file/module target is known.
- Do not leave verification as "run tests" without saying which test/check matters.
- Do not mark a plan complete while acceptance coverage or rollback notes are missing.
- Do not turn the plan into a changelog or implementation transcript; keep it forward-looking.

# Common Anti-Patterns

- **Recreating the retired lightweight planning form.** The plan is just a tiny inline list of next actions, with no durable artifact, no risk coverage, and no handoff to review. That belongs in §4 short planning, not here.
- **Planning through unresolved design.** The agent notices contract choices are still open but keeps drafting execution steps anyway, producing a false sense of readiness.
- **Abstract steps without landing.** The plan says "update the service" or "handle validation" without naming files, modules, or interfaces.
- **No acceptance traceability.** The plan lists steps, but no one can tell which acceptance criterion each step satisfies or whether anything was missed.
- **Risk-free fiction.** The change clearly touches shared surfaces or staged rollout concerns, but the plan contains no rollback or mitigation strategy.

Keep anti-pattern guidance self-contained; installed skills must not depend on maintainer-only documents.

# Composition

Position: after requirements and design are clear enough to implement, before code changes begin.

Standard forward handoffs:

- → `plan-review-loop`: when the plan should be hardened or reviewed before implementation
- → implementation: when the plan is accepted and the user wants to start coding

Standard upstream dependencies:

- `requirement-interview` clarifies what to build
- `scoped-tasking` narrows the boundary
- `design-before-plan` settles design direction when needed
- `impact-analysis` clarifies blast radius when shared callers or contracts are involved

Deactivate this skill once the implementation plan is written and handed off to `plan-review-loop` or implementation.

# Example

Task: "Implement the notification preferences API according to the existing design doc. It will touch the model, service, HTTP handler, and tests, and we want to split it into two PRs."

Apply implementation-planning:

- Validate inputs: design doc already exists; no major design choice remains.
- Ask 2 planning questions: whether rollout should be 1 PR or 2, and whether backward compatibility is required for old clients.
- Build acceptance map from the design doc.
- Draft plan file:
  - PR 1: persistence model + service layer + unit tests
  - PR 2: HTTP handler + integration tests + docs
  - shared write surface: `notification/preferences/*`
  - rollback: PR 1 additive schema only; PR 2 can be reverted without data loss
- Recommend `plan-review-loop` before implementation starts.

## Contract

### Preconditions

- The requirement or design direction is clear enough to implement.
- The user wants an implementation/execution plan rather than code edits immediately.
- The agent can identify concrete files, modules, or interfaces that the work will likely touch.

### Postconditions

- `status: completed` includes `sequence`, `file_landing`, `verify`, `risks`, and `traceability`.
- A durable plan artifact exists or is proposed with concrete implementation ordering.
- The plan is specific enough for `plan-review-loop` or implementation to consume without reopening basic sequencing questions.

### Invariants

- Planning precedes coding.
- Design decisions remain distinct from execution sequencing.
- Every planned step stays tied to concrete landing surfaces and verification.

### Downstream Signals

- `sequence` tells implementation and review what order to follow.
- `file_landing` narrows the expected edit surface for downstream work.
- `verify` tells validation and review which checks make each step observable.
- `risks` marks where rollback margin or extra caution is needed.
- `traceability` shows which acceptance criteria are covered and where.

## Failure Handling

### Common Failure Causes

- The requirement doc exists, but the design direction is still ambiguous.
- The blast radius is unclear because shared callers or interfaces were not analyzed yet.
- The user asks for a plan but has not decided increment boundaries, rollout preference, or acceptance expectations.

### Retry Policy

- Ask about the same planning-layer gap at most two rounds.
- If the second round still cannot settle a major planning blocker, stop and escalate upstream rather than drafting a speculative plan.

### Fallback

- Hand off to `requirement-interview` if the requirement itself is not mature.
- Hand off to `design-before-plan` if major design decisions are still open.
- Hand off to `impact-analysis` if the blast radius is still speculative.
- If the task is tiny and obvious, deactivate and use `AGENTS.md` §4 short planning instead.

### Low Confidence Handling

- Mark unsettled implementation assumptions explicitly in the plan artifact.
- Require `plan-review-loop` before implementation when risks or sequencing confidence remain medium or low.

## Output Example

```
[output: implementation-planning | completed medium | sequence:"2 PRs, schema/service before handler/docs" file_landing:"models/preferences.py, services/preferences.py, api/preferences.ts, tests/preferences_*" verify:"unit tests for service, integration test for handler, acceptance map coverage check" risks:"shared client compatibility, additive schema rollback, staged rollout order" traceability:"AC1->PR1, AC2->PR2, AC3->PR2" | next:plan-review-loop]
```

## Deactivation Trigger

- The plan artifact is written and handed to `plan-review-loop` or implementation.
- Upstream clarification becomes necessary again and the skill must hand back to `requirement-interview`, `design-before-plan`, or `impact-analysis`.
- The task is reduced to a small local change that no longer needs durable planning.
