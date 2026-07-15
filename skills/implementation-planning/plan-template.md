# Implementation plan template

```markdown
# 实施计划：<主题>

## 来源与对齐
- 需求来源：<文档 / 澄清结果 / 路径>
- 设计来源：<设计简报 / 架构文档>
- ADR 约束：
  - <ADR-ID> — <title> — Accepted — <artifact/path>
- 范围边界：本次做 … / 本次不做 …
- 设计取向假设：
  - 【设计取向·假设】…（依据：…；若推翻则回退设计阶段）

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
