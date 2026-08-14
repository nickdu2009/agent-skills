# 技能索引
<div class="title-en">Skill Index</div>

## 目标
<div class="title-en">Goal</div>

这一章不是教你一次记住所有技能的细节，而是给你一个“每个技能大概是干什么的”的独立索引页。  
如果你还不熟悉这些名字，可以先从这里建立整体印象，再回到[技能选择](SKILL-SELECTION.md)和[常见工作流](COMMON-WORKFLOWS.md)。

## 怎么使用这页
<div class="title-en">How to Use This Page</div>

建议按下面顺序读：

1. 先看“默认起步组合”，知道最常见的入门搭配
2. 再按类别浏览每个技能的用途
3. 如果你已经有具体任务，再回到[技能选择](SKILL-SELECTION.md)按任务形态判断

## 默认起步组合
<div class="title-en">Default Starter Set</div>

对大多数普通开发任务，最稳的起步组合通常是：

- `scoped-tasking`
- `targeted-validation`

这组组合的作用是先把边界缩小、控制改动规模，再做最小充分验证。对小任务，计划环节可用包含修改步骤和验证点的轻量内联计划；只有在多文件、多步骤、需要落盘或需要被审查时，才升级到 `implementation-planning`。

## 整合后的技能簇
<div class="title-en">Consolidated Skill Clusters</div>

为了降低选择成本，可以先把 12 个技能按职责整合为 5 个技能簇来理解：

- 执行与质量：`scoped-tasking`、`targeted-validation`
- 缺陷与重构：`bugfix-workflow`、`safe-refactor`
- 需求、影响与设计：`requirement-interview`、`impact-analysis`、`design-before-plan`、`architecture-design`、`implementation-planning`
- 评审回环：`artifact-review-loop`
- 治理与协作：`manage-agents-md`、`multi-agent-protocol`

日常任务建议先在“执行与质量”簇起步，只有在证据显示需要时再升级到其他簇。

## 基础执行技能
<div class="title-en">Core Execution Skills</div>

这些技能都是 `skills/` 下可独立使用的 Agent Skills 标准包。

### `scoped-tasking`

先把宽泛任务压缩到最小有用边界，避免一上来就读太多文件或把任务做大。

### `targeted-validation`

优先选择最小但有意义的验证方式，而不是默认跑最重的构建或测试。

## 定位、诊断与结构技能
<div class="title-en">Discovery, Diagnosis, and Structure Skills</div>

当你还不确定编辑点、根因或影响面时，这组技能用于先找证据再动手。

### `requirement-interview`

在写代码前充当“业务访谈员”，通过多轮动态追问把模糊的功能需求问清楚。不写代码、不出技术方案，只澄清“要做什么 / 为什么做 / 给谁用”，并产出结构化的“需求澄清结果”。每轮最多问 3~5 个，维护“已确认 / 未确认 / 暂定假设”三本账，需求成熟前不进入设计或编码。

### `bugfix-workflow`

按“先证据、后修改”的方式处理缺陷，先确认症状、缩小故障域，再做最小修复。

### `safe-refactor`

做小范围、可控的结构整理，同时保持对外行为和接口稳定。

### `impact-analysis`

当改动可能影响多个调用方、共享接口或共享类型时，先查清影响面再计划。

### `design-before-plan`

当真正卡住你的不是“怎么排步骤”，而是“方案到底怎么选”时，先做设计澄清再规划实施。

### `architecture-design`

当任务需要一份完整的架构设计文档——组件分解、数据架构、接口契约、非功能设计、部署拓扑、架构决策记录（ADR）——而不仅是选一个方案方向时使用。可独立使用，也可在 `design-before-plan` 选定方向后展开。按任务规模自动调整详细程度（系统级/子系统级/模块级）。

### `implementation-planning`

当需求和设计方向已经定下来，但真正难点变成“按什么顺序做、落到哪些文件、每步怎么验证、风险怎么回滚”时，用这个技能把实施计划写成可落盘、可审查的计划文档。

## 评审回环技能
<div class="title-en">Review-Loop Skill</div>

### `artifact-review-loop`

使用一个标准包评审五类产物：需求、设计、计划、代码和测试。Skill 会先分类，再按需读取对应 `references/` 规则；可在 `review-only` 与明确授权的 `review-and-revise` 之间选择，并持续到 `clean` / `clean_with_assumptions`，或在 `needs_clarification` 时停止。

完成当前任务后的自检也使用该 Skill，但只有当前 Agent 的已授权任务产物才属于 `self-delivery`。用户说“我刚改完”不能让 Agent 继承写权限。

## 项目治理技能
<div class="title-en">Project Governance Skills</div>

### `manage-agents-md`

初始化或更新项目级 `AGENTS.md`，把仓库里已有的构建、测试、约定和 Agent 行为规则整理成可长期复用的项目说明。

## 协作与交付技能
<div class="title-en">Coordination and Delivery Skills</div>

### `multi-agent-protocol`

把确实适合并行的任务拆成低耦合子问题，并协调多个代理如何分工、汇总和验证。

并行子线出现冲突时，按证据显式裁决；中等规模任务的 2 到 4 个增量拆分通常先由 `implementation-planning` 写成实施计划，并在计划中明确并行边界与 verify 纪律。

## 一页判断法
<div class="title-en">One-Page Decision Guide</div>

如果你只想快速判断该从哪个技能开始，可以先用这几条：

- 需求在业务层面就模糊（目标/角色/主流程/边界/验收不清）：`requirement-interview`
- 范围太大或太散：`scoped-tasking`
- 需要先结构化实施计划（多文件 / 多步骤 / 多 PR / 需要落盘或被审查）：`implementation-planning`
- 是缺陷且根因不明：`bugfix-workflow`
- 是结构整理：`safe-refactor`
- 需要系统/子系统/模块级架构设计（组件分解、技术选型、非功能设计）：`architecture-design`
- 可能影响很多调用方：`impact-analysis`
- 想并行但不确定值不值得：`multi-agent-protocol`
- 只想把验证缩到最小：`targeted-validation`
- 用户说“评审/审核/review …”：使用 `artifact-review-loop`，再按需求 / 设计 / 计划 / 代码 / 测试分类
- 用户要初始化或更新项目 `AGENTS.md`：`manage-agents-md`

## 接下来读什么
<div class="title-en">Read Next</div>

- 想按任务判断该选哪个技能：看[技能选择](SKILL-SELECTION.md)
- 想看具体任务怎么跑：看[常见工作流](COMMON-WORKFLOWS.md)
- 想理解为什么这样分层和这样选择：看[关键机制](KEY-MECHANISMS.md)和[决策原因](DECISION-RATIONALE.md)
