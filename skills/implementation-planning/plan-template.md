# Implementation plan template

```markdown
# 实施计划：<主题>

## 来源与对齐
- 需求来源：<文档 / 澄清结果 / 路径>
- 设计来源：<设计简报 / 架构文档>
- ADR 约束：
  - <ADR-ID> — <title> — Accepted — <artifact/path>
- 决策锁：<哪些正式来源/决定不可由实施者重新解释>
- 范围边界：本次做 … / 本次不做 …
- 兼容策略：<clean-state / additive compatibility / migration bridge / other>
- 设计取向假设：
  - 【设计取向·假设】…（依据：…；若推翻则回退设计阶段）

## 授权边界
- 本计划被接受仅表示：<作为执行来源 / 可进入评审 / other>
- 不自动授权：<代码修改 / schema / 依赖 / 外部服务 / 部署 / commit/push / 删除数据 / production-like validation>
- 执行前需单独确认：<具体授权项与 owner>

## Truth 与 Ownership
- 业务真相 owner：<domain / backend / database / external system / other>
- 非 truth surfaces：<UI state / stream / generated artifact / cache / mock / logs / other>
- 共享写面单 owner：<contracts / migrations / package-lock / root config / app composition / test config>

## 验收标准追溯
- AC1：… ← 来源：…
- AC2：…

## 开工 Gate
### GATE-00：<pre-coding gate name>
- goal：<关闭合同 / schema / 安全 / 依赖 / 外部服务 / 环境等前置>
- prerequisites：<必须先满足的授权/决策/输入>
- owns：<gate ledger / go-no-go / owner decision>
- must-not-touch：<生产代码 / migration / package / other>
- actions：<逐项 gate 检查>
- expected outputs：<owner、结论、证据、blocked 项>
- verify：<如何确认 gate 结论与正式来源一致>
- done conditions：<哪些卡可开始，哪些 blocked>
- stop/escalate conditions：<冲突/owner 未定/授权缺失>
- handoff：<交给 writer/reviewer 的内容>

## 并行规划
[parallelism:
- independent lanes: <parallel work, or none>
- sequential blockers: <must happen first>
- shared write surfaces: <single-owner files/modules>
- delegation: <delegate count, or 0 with reason>
]

## 实施步骤
### 步骤 1：<动作>
- 落地文件/模块：`path/to/file`
- 依赖：无 / 步骤 N
- 操作要点：…
- 受约束 ADR：<ADR-ID or None>
- 验收检查（verify）：…
- 覆盖验收标准：AC1、AC2

### 步骤 2：<动作>
- 落地文件/模块：`path/to/file`
- 依赖：步骤 1
- 操作要点：…
- 受约束 ADR：<ADR-ID or None>
- 验收检查（verify）：…
- 覆盖验收标准：AC3

## Coding Agent 任务卡（如需委派）
### T01：<任务名>
- goal：<本卡目标>
- prerequisites：<前置 gate/任务>
- must-read：<正式输入>
- owns：<本卡唯一写面>
- must-not-touch：<禁止触碰的文件/模块/动作>
- actions：<实施动作>
- expected outputs：<产物>
- verify：<最小充分检查>
- done conditions：<完成条件>
- stop/escalate conditions：<必须停止并升级的条件>
- handoff：<交给后续卡/reviewer/validator 的信息>

## 风险与回滚
- 风险：…
  - 关联步骤：…
  - 影响：…
  - 缓解 / 回滚：…

## 验收标准覆盖检查
- AC1 → 步骤 1
- AC2 → 步骤 1

## 待确认 / 残留假设
- 【假设】…（验证方法：…）

## 下一步
- 建议运行 plan-review-loop，再进入实现。
```

Omit assumptions only when none remain. Do not omit source, verification, risk, or coverage sections.
