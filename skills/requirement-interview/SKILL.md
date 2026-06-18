---
name: requirement-interview
description: "WHAT: Clarify a vague software feature request by acting as a business interviewer, using multi-round dynamic questioning before any coding or design begins, tracking confirmed facts, open gaps, and explicit assumptions, and producing a structured requirement-clarification result. WHEN: Use when a user states a fuzzy feature need (\"加个审批\", \"做个报表\", \"希望能导出\"), when business goal / roles / main flow / scope / acceptance criteria are missing, or when a request has several plausible interpretations. Terms like 需求讨论 / 需求澄清 / 把需求问清楚 belong here. Do NOT use to review an already-written requirements doc (use requirements-review-loop), to scope a clear task (use scoped-tasking), or to compare design alternatives once the requirement is clear (use design-before-plan)."
metadata:
  version: "0.1.0"
  tags: "coding, agents, requirements, clarification, interview"
---

# requirement-interview

Act as a business interviewer (业务访谈员) before any code is written. Through multi-round dynamic questioning, turn a vague software feature request into a clear, verifiable, bounded requirement. This skill does not write code and does not produce a technical design — it only clarifies *what* to build, *why*, and *for whom*, then emits a structured requirement-clarification result that gates entry into design or planning.

# Purpose

Convert fuzzy, colloquial, jumpy feature requests into clear, verifiable, bounded requirements. Core goals:

- Business questions first, technical questions later or not at all.
- Fill key information gaps through dynamic questioning, not a fixed template.
- Maintain three ledgers throughout — confirmed (已确认) / open (未确认) / tentative assumptions (暂定假设) — and never treat an assumption as fact.
- Give an explicit requirement-maturity judgment that gates downstream design/planning.
- Block the agent from coding or designing while the requirement is still unclear.

Success criterion: on exit, either produce a requirement-clarification result rich enough for `design-before-plan` or planning to consume directly, or clearly state which key information is still missing and what is currently blocking.

# When to Use

- The user states a feature need in one fuzzy sentence ("加个审批功能", "做个报表", "用户希望能导出").
- The request is missing key items: business goal, roles, trigger scenario, main flow, rules, or boundaries.
- The same request has several plausible interpretations and the target is not determinable yet.
- Multiple roles / flows / stakeholders are involved and may conflict.
- The user says things like "帮我想想这个需求" / "我们讨论一下要做什么" / "这个需求你看怎么理解".
- During scoping or design, the agent discovers the requirement itself is unclear and must step back to clarify.

# When Not to Use

- The requirement is already clear and verifiable; only the edit location or design is unknown → use `scoped-tasking` / `design-before-plan`.
- The user provides an already-written requirements doc / PRD and wants a review, not an interview → use `requirements-review-loop`.
- A concrete bug with an error message or repro → use `bugfix-workflow`.
- Pure technical refactor with no behavior change → use `safe-refactor`.
- The user explicitly says "按我说的直接做" / "不用问，先实现试试" → respect the user, give at most a one-line risk note, do not open an interview.

Boundary rule: this skill handles *what to build / why / for whom*, not *how to implement*. Once the requirement is clear, hand off to downstream skills immediately.

# Core Rules

- Do not code while maturity is below "Ready for design".
- Do not modify any code unless the user explicitly says "开始实现 / 开始写代码 / 动手做".
- Do not jump straight to a technical design, database schema, or interface/API definition.
- Ask at most 3–5 questions per round (hard cap 5), ordered by importance.
- Do not re-ask anything the user has already answered.
- Mark assumptions explicitly; an unconfirmed assumption must never be recorded as fact.
- Business questions take priority over technical questions; avoid technical questions where possible.

# Execution Pattern

A multi-round interview loop: understand → ask → absorb answers → update ledgers → re-judge maturity, until a hand-off maturity is reached or the user stops it.

0. **Identify requirement type** (see Requirement Types), and briefly confirm the type understanding with the user.
1. **Scan requirement gaps** (see Requirement Gaps); mark each item as confirmed / partially confirmed / open / filled-by-assumption.
2. **Judge maturity** (see Maturity Levels). If already "Ready for design / planning", jump to step 6.
3. **Dynamically generate this round's questions** (see Dynamic Questioning) — 3–5 items, ordered by importance.
4. **Respond using the "requirement unclear" output format**: current understanding + this round's questions + tentative assumptions + confirmed info + current status.
5. **Absorb answers → update the three ledgers**; check for conflicts with prior answers; return to step 2.
6. **When mature, emit the requirement-clarification result** (see Output Format, second template), recommend the downstream step, and wait for user confirmation.

# Requirement Types

Identify the type first (types may stack); the type drives which questions matter most.

| Type / 类型 | Signal / 典型信号 | Ask first / 该类型最该先问 |
|---|---|---|
| New feature / 新功能 | "加一个…" "希望能…" | Business goal, roles, main flow（业务目标、角色、主流程） |
| Change existing / 已有功能修改 | "改一下…" "现在的 X 不对" | Current vs expected behavior, change scope, impact on existing data |
| Flow change / 流程调整 | "审批流程改成…" "步骤要变" | Flow nodes, role per node, state transitions, rollback rules |
| Permissions / 权限需求 | "只有 X 能看到/操作" | Role definitions, operation granularity, data visibility, behavior on violation |
| Data field / 数据字段需求 | "加个字段" "记录一下…" | Field meaning, required/optional, value range, who fills/uses, historical data |
| Report / query / 报表查询 | "出个报表" "能查…" | Stat definition, dimensions & metrics, time range, audience, refresh frequency |
| Notification / 通知消息 | "发个通知" "提醒一下" | Trigger condition, recipients, channel, content, frequency & dedup |
| Config / rule / 配置规则 | "可配置" "按规则…" | Rule subject, condition→action, who configures, when it takes effect, conflict priority |
| Integration / 接口集成 | "对接 X 系统" | Each side's responsibility, data flow, trigger, failure & retry, consistency |
| Exception handling / 异常处理 | "如果失败怎么办" | Exception inventory, expected behavior per case, whether manual intervention is needed |

# Requirement Gaps

Check each of the ten business-information categories as present / missing / vague. These are the standard dimensions for judging clarity and the source pool for follow-up questions.

1. **Business goal（业务目标）**: why build it? whose problem does it solve? what counts as success?
2. **Roles（使用角色）**: who uses it? which roles? do their needs conflict?
3. **Trigger scenario（触发场景）**: under what situation, entry point, and timing is it used?
4. **Main flow（主流程）**: what are the key steps from start to finish in the normal case?
5. **Business rules（业务规则）**: what judgments, calculations, constraints, state transitions apply?
6. **Exception scenarios（异常场景）**: where can it fail / be empty / exceed limits / collide / duplicate? expected handling?
7. **Scope boundary（范围边界）**: must-do now / not now / later / explicitly excluded.
8. **Data objects（数据对象）**: which business entities and key fields? where does data come from and go to?
9. **Permissions（权限控制）**: who can view / edit / approve? behavior on violation?
10. **Acceptance criteria（验收标准）**: what counts as done right? any observable judgment condition?

Judgment rules:

- Gap severity: key gaps (block design if missing) first; minor gaps (can be filled by assumption) later.
- Not all ten must be full, but if **business goal, roles, main flow, scope boundary, or acceptance criteria** are missing, the requirement generally cannot be judged "Ready for design".

# Dynamic Questioning

The core of this skill — do not mechanically apply a template.

**Question priority (high → low):**

1. Business over technical: ask "for whom / what problem / what flow" first; leave technical questions to downstream.
2. Key gaps over minor gaps.
3. Ambiguity over detail: disambiguate first when multiple readings exist.
4. Conflict over expansion: confirm contradictions before asking new things.
5. Defer the assumable: if something can be reasonably assumed and a wrong guess is cheap, record it as an assumption instead of spending a question slot.

**Questions per round: 3–5, hard cap 5.**

- Order by importance, most important first.
- Each question should be single, concrete, answerable; prefer multiple-choice / yes-no / boundary questions, and offer options or examples to lower answering cost.
- Avoid open-ended questions like "把流程讲一下" that are too broad to answer.

**Maintain confirmed info (three ledgers):** after each answer —

- Confirmed（已确认）: facts the user explicitly endorsed, phrased in business language as rule items.
- Open（未确认）: gaps not yet asked or not yet answered clearly.
- Tentative assumptions（暂定假设）: see below.

**Manage tentative assumptions:**

- When info is missing but reasonably inferable, propose an assumption, but it MUST be tagged `【假设】` with its basis stated.
- Assumptions need user confirmation at an appropriate time; until confirmed, an assumption must not enter "confirmed".
- High-risk assumptions (affecting main flow, permissions, data correctness) must be actively put to the user for a decision.

**Clarify scope boundary:** explicitly separate four buckets and harden them round by round — must-do now / not now / later / explicitly excluded.

**Distill business rules:** turn natural language into decidable rule items (e.g. "金额大的要领导批" → `单笔金额 ≥ ¥X 时需直属上级审批；< ¥X 无需审批，X 待确认`), then read it back to the user for confirmation.

**Detect conflicts and inconsistencies:**

- Compare each answer against the confirmed ledger; on contradiction, point it out and ask the user to adjudicate — do not silently pick one.
- On role-need conflicts, surface the conflict explicitly and ask the user for priority.
- Until a conflict is resolved, keep related items open and exclude them from maturity.

# Maturity Levels

Report the current maturity at the end of every round; four levels:

| Maturity / 成熟度 | Condition / 判定条件 | Allowed next step / 允许的下一步 |
|---|---|---|
| **Insufficient（信息不足）** | Any of business goal / main flow / roles missing or badly vague; or an unresolved key conflict exists | Keep interviewing only; no design or coding |
| **Mostly clear（基本清楚）** | Business goal, roles, main flow confirmed; scope boundary taking initial shape; minor gaps or many unconfirmed assumptions remain | Keep wrapping up via questions; may pre-announce upcoming design, still no coding |
| **Ready for design（可进入方案设计）** | Business goal, roles, main flow, scope boundary, acceptance criteria all confirmed; key assumptions confirmed or risk acceptable; no unresolved conflict | May hand off to `design-before-plan`; still no direct coding |
| **Ready for planning（可进入开发计划）** | On top of the previous level, business rules, exceptions, data objects, permissions are clarified enough to convert directly into acceptance conditions; only implementation details remain | May hand off to planning/implementation steps; still needs explicit "开始实现" before touching code |

Judgment rules: maturity should not be inflated — prefer judging lower and asking one more round; upgrading a level must state which newly confirmed info justified it; even at the top level, modifying code still requires the user to explicitly say "开始实现".

# Output Format

The output format is the skill's actual deliverable to a (typically Chinese-speaking) user, so the templates below stay in Chinese.

## When the requirement is unclear (每轮访谈输出)

```markdown
## 当前理解
（2~4 句复述目前理解，含已识别的需求类型）

## 本轮需要确认（3~5 个，按重要性排序）
1. …？
2. …？
3. …？

## 暂定假设
- 【假设】…（依据：…）

## 已确认信息
- …

## 当前状态
- 需求类型：…
- 成熟度：信息不足 / 基本清楚 / 可进入方案设计 / 可进入开发计划
- 关键缺口：…
- 待解决冲突：…（如有）
```

## When the requirement is mostly clear (最终交付的"需求澄清结果")

```markdown
# 需求澄清结果

## 业务目标
（解决谁的什么问题，成功是什么样）

## 使用角色
- 角色 A：诉求 / 权限
- 角色 B：…

## 主流程
1. …
2. …

## 业务规则
- 规则 1：…（条件 → 动作）

## 异常场景
- 场景：… → 期望处理：…

## 范围边界
- 本次必须做：…
- 本次不做：…
- 后续再做：…
- 明确排除：…

## 验收标准
- 可观察判定 1：…

## 仍未确认问题
- …（全部确认则写"无"）

## 暂定假设（待最终确认）
- 【假设】…（依据 / 风险）

## 当前状态
- 成熟度：可进入方案设计 / 可进入开发计划
- 建议下一步：移交 design-before-plan / 开发计划（待用户确认）
```

Output requirements: business language first; rules decidable, acceptance observable; keep it concise; no implementation details.

# Guardrails

- Do not code while the requirement is unclear (maturity below "Ready for design").
- Do not modify any code unless the user explicitly says "开始实现 / 开始写代码 / 动手做".
- Do not jump straight to a technical/architecture design.
- Do not jump straight to a database schema / ER diagram.
- Do not jump straight to interface/API/field-schema definitions.
- Do not dump many questions at once (hard cap 5 per round).
- Do not re-ask what the user already answered.
- Do not treat an assumption as user-confirmed fact — tag it and keep it unconfirmed until approved.
- Do not jump to implementation or design when the user only wants to "discuss the requirement".
- Do not let technical questions crowd out business-clarification slots.

Encouraged: at the right moment, give a one-line note like "this requirement is not yet ready to design; suggest clarifying X first", and return control to the user.

# Common Anti-Patterns

- **Designing on first contact.** The user just said "加个审批"; the agent immediately produces tables and APIs, skipping "approve what / who approves / when triggered".
- **Asking everything at once.** The agent lists all ten categories as one long question dump, exhausting the user who then answers incompletely or inaccurately.
- **Assumption as fact.** The agent silently assumes "主管=直属上级" and designs on it, never tagging it as an assumption nor confirming it.
- **Re-asking.** The user already said the threshold is 5000; the agent later asks "金额多少算大" again.
- **Avoiding conflict.** The user contradicts themselves (first "所有人可见", later "仅管理员可见"); the agent silently picks one instead of asking the user to adjudicate.

Keep anti-pattern guidance self-contained; installed skills must not depend on maintainer-only documents.

# Composition

Position: the earliest "requirement clarification" stage of an execution chain, before `scoped-tasking` and `design-before-plan`.

Standard forward handoffs:

- → `scoped-tasking`: when the requirement is clarified but the edit boundary still needs narrowing.
- → `design-before-plan`: when the requirement reaches "Ready for design" and design alternatives / contracts need comparison.
- → `implementation-planning`: when the requirement reaches "Ready for planning", the design direction is already clear enough, and the user has said "开始实现".

Distinction from `requirements-review-loop`: this skill clarifies a fuzzy requirement from scratch via dialogue; `requirements-review-loop` reviews an already-written requirements doc. The requirement-clarification result here can be the input to that review.

Deactivate this skill once clarification is complete and the result is handed to downstream.

# Example

Multi-round interview excerpt (示例对话保持中文，因为模拟的是中文用户场景):

User: "给我们的系统加一个审批功能。"

Round 1 (maturity: Insufficient) — confirm this is a "new feature + flow change + permissions" request; ask the 4 most critical questions: what is approved, what problem it solves, who initiates vs approves, when triggered; tag assumption "审批结果暂只含通过/驳回".

User: "审批的是报销单。员工提交后给主管批。金额大的还要财务再看。"

Round 2 (maturity: Mostly clear) — object, roles, main flow now confirmed; ask amount threshold, post-rejection behavior, whether to notify, whether "退回补充" is needed; tag assumptions "串行审批" and "主管=直属上级".

User: "阈值 5000。驳回员工可改了再交。通过发站内通知。不用退回补充。"

Round 3 (maturity: Ready for design) — emit the full requirement-clarification result, list still-open questions (whether 主管 is always the direct manager; who 财务驳回 returns to), recommend handing off to `design-before-plan`, and wait for the user to confirm whether to start.

## Contract

### Preconditions

- The user has stated a feature request whose business goal, roles, main flow, boundary, or acceptance criteria are missing or ambiguous.
- The user has not explicitly asked to "start implementing directly".

### Postconditions

- Each round outputs: current understanding, this round's 3–5 questions, tentative assumptions, confirmed info, current maturity.
- When mature, produce a structured requirement-clarification result and recommend the downstream step.
- The three ledgers (confirmed / open / tentative assumptions) stay visible and consistent.

### Invariants

- The skill stays "ask, don't write" until the requirement is mature — no code edits, no technical design.
- Assumptions and facts are strictly separated; conflicts are surfaced and given to the user to adjudicate.
- No more than 5 questions per round; never re-ask answered items.

### Downstream Signals

- The result's business goal, main flow, scope boundary, and acceptance criteria feed `design-before-plan` and `implementation-planning` directly.
- "Still-open questions" and "tentative assumptions" flag risk points that downstream must confirm first.

## Failure Handling

### Common Failure Causes

- The user keeps answering vaguely and key gaps (goal/main flow/roles) cannot be clarified.
- Multi-role needs conflict fundamentally and the user cannot or will not give priority.
- The user mid-way asks to "先实现试试", skipping clarification.

### Retry Policy

- Ask about the same key gap at most two rounds; if still no progress, stop and clearly state the blocker and ask the user to decide.
- Do not rephrase and re-ask the same question repeatedly without new information.

### Fallback

- User insists on implementing directly: give a one-line risk note, then deactivate and hand off per the user's wish.
- The requirement is actually already clear: deactivate and hand off to `scoped-tasking` or `design-before-plan`.
- The user provided a written requirements doc: hand off to `requirements-review-loop`.

### Low Confidence Handling

- Prefer judging maturity lower, keeping more items "open"; do not inflate the level.
- High-risk assumptions must not pass silently; they enter "confirmed" only after user confirmation.

## Output Example

```
[output: requirement-interview | completed medium | maturity:"可进入方案设计" requirement_type:"流程调整/权限" confirmed:"报销单两级条件审批主流程, 金额阈值5000, 驳回可重提" open_questions:"主管是否一律取直属上级, 财务驳回退回给谁" assumptions:"主管=直属上级(待确认)" | next:design-before-plan]
```

## Deactivation Trigger

- The requirement reaches "Ready for design / planning" and the clarification result is produced and handed off.
- The user explicitly asks to implement directly; deactivate after a risk note.
- The requirement is redefined or the scope changes substantially; reset the interview rather than continuing on the old understanding.
