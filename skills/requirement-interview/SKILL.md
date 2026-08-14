---
name: requirement-interview
description: "Clarify a vague software feature request through a multi-round business interview, tracking confirmed facts, open gaps, and tentative assumptions before design or coding. Use when business goals, roles, main flow, scope, rules, or acceptance criteria are missing or ambiguous. Do not use to review a written requirements artifact; route that to artifact-review-loop with type requirements."
metadata:
  version: "0.2.0"
  tags: "requirements, clarification, interview"
---

# requirement-interview

Turn a fuzzy feature request into a bounded, verifiable requirement. Clarify *what*, *why*, and *for whom*; do not design the implementation.

## Activation and boundary

Activate for an ambiguous new feature, behavior change, workflow, permission, report, notification, configuration, or integration request. Defer when the requirement is already verifiable, the user asks to review an existing document, or the task is a concrete bug/refactor.

If the user explicitly declines an interview, give one short risk note, preserve every unresolved behavioral question, and deactivate. “直接做 / 先试试” skips the interview form only; it does not authorize invented outputs, permissions, data semantics, thresholds, retries, fallbacks, or failure handling.

## Hard constraint

**Until maturity reaches `Ready for design`, ask and record; do not write code, choose a technical design, or turn an unconfirmed assumption into behavior.**

## Core workflow

1. **Classify the request.** Identify one or more requirement types. Read [requirement-types.md](references/requirement-types.md) only when type-specific gaps or question choices are useful.
2. **Open three ledgers.** Maintain `confirmed`, `open`, and `tentative_assumptions`. Never move an item to `confirmed` without user endorsement.
3. **Scan business gaps.** Check business goal, roles, trigger, main flow, rules, exceptions, scope, data objects, permissions, and acceptance criteria. Goal, roles, main flow, scope, and acceptance are normally gating.
4. **Ask one bounded round.** Ask 3–5 questions, hard cap 5, ordered by decision impact. Prefer concrete choices, yes/no questions, and boundary questions. Do not re-ask answered items.
5. **Absorb and reconcile.** Update all ledgers, expose contradictions, and ask the user to adjudicate role or rule conflicts. Distill natural language into decidable business rules and read them back.
6. **Rejudge maturity.** Repeat only while a new round can close a material gap. State what newly confirmed evidence justifies any maturity increase.
7. **Deliver or stop.** When mature, emit the clarification result and recommend the next skill. If blocked, name the exact missing decisions instead of designing through them.

Question priority is: business before technical; gating gaps before detail; ambiguity before expansion; conflicts before new topics. A low-cost interview assumption may reduce questioning only when a wrong guess cannot affect external behavior. Tag it `【假设】` with its basis. Behavioral assumptions must be put to the user and remain open until confirmed.

Explicitly divide scope into: `must_do_now`, `not_now`, `later`, and `excluded`.

## Ledger and questioning rules

For each business dimension, record both value and evidence:

- `confirmed`: the user-endorsed rule in business language and the round/source that confirmed it
- `open`: the missing decision, why it matters, and which maturity level it blocks
- `tentative_assumptions`: `item`, `basis`, `risk`, and `confirmation_needed`

After every answer, compare it with the confirmed ledger. When two statements conflict, quote or neutrally paraphrase both, mark affected rules open, and ask the user to choose; never silently prefer the newest answer. When roles want incompatible outcomes, ask who owns the priority decision.

A good question closes one decision. Prefer “驳回后是结束、可修改重提，还是退回上一审批人？” to “异常怎么处理？”. Offer 2–3 plausible choices when they reduce effort, but do not make the recommended choice look pre-approved. Ask technical questions only when the technical constraint is itself a business boundary; implementation details remain downstream.

Turn fuzzy rules into a condition/action form without filling variables. Example: “金额大的要领导批” becomes `amount >= X -> approver Y; X and Y open`. Read the rule back and keep it open until the user confirms both variables.

## Maturity gate

| Level | Minimum state | Allowed next step |
|---|---|---|
| `Insufficient` | Goal, roles, or main flow missing; or key conflict unresolved | Continue interview only |
| `Mostly clear` | Goal, roles, and main flow confirmed; boundary forming; material gaps remain | Continue interview |
| `Ready for design` | Goal, roles, flow, boundary, and observable acceptance confirmed; behavioral assumptions confirmed or explicitly open | Hand off to `design-before-plan` |
| `Ready for planning` | Rules, exceptions, data, and permissions are also sufficient; no unconfirmed behavioral assumption remains | Hand off to planning, still no code without explicit implementation request |

Prefer the lower level when evidence is mixed. An explicitly open behavioral decision may coexist with `Ready for design` only as a design gate, never as a default. It prevents `Ready for planning`.

At the end of every round, show the maturity and the specific evidence still needed for the next level. Do not declare completion merely because the user answered all questions in the latest round; reconcile the answer with earlier confirmed rules first. Before handoff, ask the user to confirm or correct the compact clarification result.

## Output contract

Every interview round returns:

- `current_understanding`: 2–4 sentences including requirement type
- `questions`: 3–5 ordered questions
- `tentative_assumptions`: tagged assumptions with basis
- `confirmed`: current confirmed facts
- `open`: remaining gaps and conflicts
- `maturity`: one of the four levels

The final `requirement_clarification` returns:

- `business_goal`
- `roles`
- `main_flow`
- `business_rules`
- `exception_scenarios`
- `scope_boundary`: all four buckets
- `acceptance_criteria`: observable conditions
- `open_questions`
- `tentative_assumptions`
- `maturity`
- `recommended_next_step`

Use business language; keep rules decidable and acceptance observable. Do not add APIs, schemas, or implementation details. Read [examples.md](references/examples.md) only when calibration is needed.

Render a round compactly:

```markdown
## 当前理解
<2–4 sentences, including requirement type>

## 本轮需要确认
1. <highest-impact bounded question>
2. …

## 暂定假设
- 【假设】<item>（依据：…；风险：…）

## 已确认信息
- …

## 当前状态
- 成熟度：信息不足 / 基本清楚 / 可进入方案设计 / 可进入开发计划
- 关键缺口：…
- 待解决冲突：…
```

Render the final clarification with headings for 业务目标, 使用角色, 主流程, 业务规则, 异常场景, 范围边界, 验收标准, 仍未确认问题, 暂定假设, and 当前状态. The four scope buckets and every required output field must be present; write `无` rather than silently omitting an empty open-question or assumption section.

## Stop and handoff rules

Stop the loop when maturity is sufficient, the user declines, two rounds add no evidence on the same gating decision, or an owner conflict cannot be adjudicated. Do not keep asking merely to complete all ten dimensions. Recommend `scoped-tasking` when the requirement is clear but repository scope is not, `design-before-plan` when alternatives/contracts remain, and `implementation-planning` only at `Ready for planning` with a settled direction.

## Clarification quality gate

Before upgrading maturity, verify:

- The business goal names the affected actor/problem and an observable success outcome, not “support X” alone.
- The main flow has a trigger, normal sequence, end state, and role at each decision point.
- Business rules have decidable conditions and results; missing variables remain named open items.
- Permissions state both allowed operations/data visibility and the expected denied outcome.
- Exceptions describe the business result, not an invented technical retry, fallback, or error code.
- Data objects are described by business meaning, ownership, and lifecycle; do not design field schemas.
- Acceptance criteria can be observed from outside the implementation. Prefer a compact Given/When/Then statement or an equivalent actor/action/result condition.
- Each scope item belongs to exactly one of the four buckets, so “later” work is not mistaken for current acceptance.

`Ready for design` may carry an explicitly open decision only when the design phase is the correct owner and the gap is labeled blocking there. It may not carry an unresolved business goal, role, main flow, scope boundary, or acceptance outcome. `Ready for planning` cannot carry unresolved product behavior at all.

## Contract

### Preconditions

- A feature request lacks or ambiguously states a goal, role, flow, boundary, rule, or acceptance criterion.
- The user has not explicitly declined the interview.

### Postconditions

- Each round exposes the required output fields and synchronized three ledgers.
- Completion produces `requirement_clarification` or a bounded blocker report.
- `status: completed` includes `maturity`, `requirement_type`, `confirmed`, `open_questions`, and `assumptions`.

### Invariants

- No code or technical design is produced while interviewing.
- Facts, open gaps, and assumptions remain distinct; conflicts require user adjudication.
- Each round asks at most five questions and never repeats an answered question.

### Downstream Signals

- Goal, flow, boundary, and acceptance feed `design-before-plan` or `implementation-planning`.
- Open questions and assumptions remain explicit gates for downstream work.

## Failure Handling

### Common Failure Causes

- Answers remain vague, stakeholders conflict, or the user requests implementation before behavioral choices are settled.

### Retry Policy

- Ask about the same key gap for at most two productive rounds. Without new evidence, stop and request the missing decision.

### Fallback

- Clear requirement: hand off to `scoped-tasking` or `design-before-plan`.
- Written requirements review: hand off to `artifact-review-loop` with `artifact_type: requirements`.
- Interview declined: deactivate after the risk note and preserve open behavioral questions.

### Low Confidence Handling

- Keep maturity lower and assumptions open. Never let an unconfirmed behavioral assumption reach planning as an accepted default.

## Output Example

```text
[output: requirement-interview | completed medium | maturity:"Ready for design" requirement_type:"workflow/permission" confirmed:"expense approval flow; threshold 5000; rejected claims may be resubmitted" open_questions:"manager identity; finance rejection target" assumptions:"none confirmed" | next:design-before-plan]
```

## Deactivation Trigger

- A clarification result is delivered at `Ready for design` or `Ready for planning`.
- The user declines the interview after open risks are stated.
- Scope changes substantially; reset the ledgers rather than extending stale conclusions.
