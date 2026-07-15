# Implementation Planning

## Scenario

The design for a notification preferences feature is already approved. `ADR-0042` is Accepted and active and selects an additive preferences model. The remaining work touches the data model, service layer, API handler, and tests, and the team wants a durable implementation plan before coding starts.

## Recommended Skill Composition

- `scoped-tasking`
- `design-before-plan`
- `implementation-planning`
- `plan-review-loop`

Small local tasks would stay on `AGENTS.md` Behavioral Guidelines §4 short planning instead. This example is intentionally large enough to require a written plan artifact.

## Why This Composition

- `scoped-tasking` confirms the edit boundary before planning.
- `design-before-plan` settles the request/response contract and acceptance criteria.
- `implementation-planning` turns that settled design into ordered steps, file landing, verify checks, and rollback notes.
- `plan-review-loop` hardens the plan before implementation begins.

## Example Flow

1. `scoped-tasking` narrows the surface to:
   - `models/notification_preferences.*`
   - `services/notification_preferences.*`
   - `api/notification_preferences.*`
   - focused tests and docs
2. `design-before-plan` confirms:
   - existing preferences model is extended, not replaced
   - old clients remain backward compatible
   - acceptance criteria cover read/update behavior and validation errors
3. `implementation-planning` asks only planning-layer questions:
   - one PR or two?
   - additive schema only, or migration with backfill?
   - unit-first or integration-first validation?
4. It resolves the ADR set: consume active Accepted `ADR-0042`; exclude Proposed, inactive, or superseded decisions.
5. `implementation-planning` writes `.plans/notification-preferences-plan.md` with:
   - acceptance map (`AC1`, `AC2`, `AC3`)
   - `[parallelism: ...]`
   - ordered steps with file landing and `verify`
   - risk/rollback table
6. `plan-review-loop` reviews the plan artifact and ADR alignment before coding starts.

## What Good Looks Like

- The plan names specific files or modules for every step.
- Each step has a concrete `verify` check.
- Every acceptance criterion maps to one or more steps.
- Rollback is explicit for schema and API changes.
- `ADR-0042` appears in Sources and Alignment and every step it constrains.
- The plan is durable enough that another agent could implement it without reopening sequencing questions.

## What Bad Looks Like

- The "plan" is only 2-3 bullets in chat.
- Steps say "update backend" without naming files.
- Validation says only "run tests" with no narrower check.
- Requirements or design questions are still open, but the plan pretends implementation can start anyway.
- A Proposed or superseded ADR is treated as a frozen implementation constraint.

## Example Plan Skeleton

```markdown
# 实施计划：通知偏好

## 来源与对齐
- 需求来源：docs/requirements/notification-preferences.md
- 设计来源：docs/design/notification-preferences.md
- ADR 约束：ADR-0042 — Additive notification preferences model — Accepted

## 验收标准追溯
- AC1：用户可读取当前通知偏好
- AC2：用户可更新通知偏好
- AC3：非法渠道返回结构化校验错误

## 并行规划
[parallelism:
- independent lanes: none
- sequential blockers: schema before handler tests
- shared write surfaces: models/, services/, api/
- delegation: 0 with reason
]

## 实施步骤
### 步骤 1：扩展偏好数据模型
- 落地文件/模块：`models/notification_preferences.*`
- 依赖：无
- 操作要点：新增渠道字段，保持默认值兼容
- 受约束 ADR：ADR-0042
- 验收检查（verify）：模型单测通过
- 覆盖验收标准：AC1、AC2

### 步骤 2：实现服务层读写逻辑
- 落地文件/模块：`services/notification_preferences.*`
- 依赖：步骤 1
- 操作要点：封装读取/更新与校验
- 受约束 ADR：ADR-0042
- 验收检查（verify）：服务层单测通过
- 覆盖验收标准：AC1、AC2、AC3

## 风险与回滚
| 风险 | 关联步骤 | 影响 | 缓解 / 回滚策略 |
|---|---|---|---|
| schema default mismatch | 步骤 1 | 老数据读取异常 | additive migration + revert schema field |
```
