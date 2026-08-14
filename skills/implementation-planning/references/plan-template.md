# Implementation plan template

```markdown
# 实施计划：<主题>

## 来源与对齐
- 需求/设计来源：<artifact/path>
- Accepted ADR：<ID — artifact/path>
- 决策锁与范围：本次做 … / 不做 …
- 兼容策略：<clean-state / additive / dual-read-write / migration bridge>

## 授权边界
- 计划接受表示：…
- 不自动授权：代码 / schema / dependency / external / deploy / commit-push / destructive / production-like validation
- 单独确认项与 owner：…

## Truth 与 Ownership
- 业务 truth owner：…
- 非 truth surfaces：…
- 共享写面单 owner：…

## 验收追溯
- AC1：… ← 来源：…

## 开工 Gate（如需）
- GATE-00：<引用完整 gate contract；未关闭项阻断哪些步骤>

## 并行规划
[parallelism:
- independent lanes: …
- sequential blockers: …
- shared write surfaces: …
- delegation: …
]

## 实施步骤
### S1：<动作>
- 落地文件/模块：…
- 依赖：…
- 操作要点：…
- 受约束 ADR：…
- verify：…
- 覆盖：AC1

## Coding Agent 任务卡（如需）
- <引用完整 task-card contract>

## 风险与回滚
- 风险；关联步骤；影响；缓解/回滚：…

## 覆盖检查
- AC1 → S1 → verify

## 待确认 / 残留假设
- 【机械假设】…（验证方法：…）
- 【行为假设】…（source；owner decision；done condition）— 未关闭不得编码

## 下一步
- artifact-review-loop(type=plan) / authorized implementation
```

Omit only sections that are genuinely inapplicable. Never omit sources, landing, verification, risk/rollback, coverage, or authorization boundaries.
