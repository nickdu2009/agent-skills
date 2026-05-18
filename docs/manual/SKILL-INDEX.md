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
- `plan-before-action`
- `targeted-validation`

这组组合的作用是先把边界缩小、先计划、控制改动规模，再做最小充分验证。

## 基础执行技能
<div class="title-en">Core Execution Skills</div>

`manage-governance.py` 不再安装它。

### `scoped-tasking`

先把宽泛任务压缩到最小有用边界，避免一上来就读太多文件或把任务做大。

### `plan-before-action`

在多步或不确定任务里，先形成短计划，再进入编辑和验证。

把改动控制在最小可行补丁内，避免顺手清理、顺手重构、顺手扩大范围。

### `targeted-validation`

优先选择最小但有意义的验证方式，而不是默认跑最重的构建或测试。

### `self-review`

在测试前先回看自己的 diff，检查范围是否跑偏、有没有残留调试代码、有没有低成本质量问题。

## 定位、诊断与结构技能
<div class="title-en">Discovery, Diagnosis, and Structure Skills</div>

在陌生区域里沿着最强线索找真正的编辑点，不做无边界扫读。

### `bugfix-workflow`

按“先证据、后修改”的方式处理缺陷，先确认症状、缩小故障域，再做最小修复。

### `safe-refactor`

做小范围、可控的结构整理，同时保持对外行为和接口稳定。

当调查越做越散、文件越看越多、假设越列越多时，主动压缩上下文，重新聚焦。

### `impact-analysis`

当改动可能影响多个调用方、共享接口或共享类型时，先查清影响面再计划。

### `design-before-plan`

当真正卡住你的不是“怎么排步骤”，而是“方案到底怎么选”时，先做设计澄清再规划实施。

## 评审回环技能
<div class="title-en">Review-Loop Skills</div>

这一组技能用于“拿到一个产物 → 评审 → 修订 → 再评审”的闭环式审核。按被评审产物的类型选择对应技能，技能之间互斥；任何一个都要求"反复直到 review_result: clean"，不是一次性 review。

### `requirements-review-loop`

审核需求文档 / PRD / 用户故事 / 验收标准。关键词：需求、PRD、user story、acceptance criteria。

### `design-review-loop`

审核设计文档 / RFC / ADR / 接口设计 / 架构设计 / 数据模型 / 技术方案。中文“方案 / 实现思路 / 实现方案 / 接口 / 思路”默认归这里。

### `plan-review-loop`

审核实施计划 / 迁移方案 / 重构计划 / 任务计划 / 路线图。中文“实施方案 / 迁移方案”归这里。

### `code-review-loop`

审核已实现的代码 diff / commit / PR / 指定文件，修复实现层缺陷并跑最小验证。

### `test-review-loop`

审核测试用例 / 测试策略 / 覆盖矩阵 / 新增或修改的测试文件本身，跑测试作为验证。注意：审"测试用例本身"而不是"被测的产品代码"。

## 协作与交付技能
<div class="title-en">Coordination and Delivery Skills</div>

### `multi-agent-protocol`

把确实适合并行的任务拆成低耦合子问题，并协调多个代理如何分工、汇总和验证。

当并行调查结果或多个假设彼此冲突时，用证据而不是语气来比较和裁决。

把一个中等规模任务拆成 2 到 4 个可独立合并的增量，而不是一次压成一个大改动。

## 阶段系统技能
<div class="title-en">Phase System Skills</div>

这组技能比普通执行技能重很多，适合多波次、多 PR、跨模块的大型任务。  
如果你只是处理普通开发任务，通常不需要一开始就启用它们。

### `phase-plan`

把大任务拆成按波次执行的结构化计划，而不是写成一篇松散的规划说明。

在阶段执行前，从意图一致性、计划质量和执行可行性三个角度审查阶段计划。

### `phase-execute`

按已经接受的 phase 执行文档推进具体波次，而不是凭记忆或口头计划执行。

### `phase-contract-tools`

维护 phase 系统共享的 schema、validator、renderer 和合同约束工具，不是普通任务默认会用到的技能。

## 一页判断法
<div class="title-en">One-Page Decision Guide</div>

如果你只想快速判断该从哪个技能开始，可以先用这几条：

- 范围太大或太散：`scoped-tasking`
- 需要先计划：`plan-before-action`
- 是缺陷且根因不明：`bugfix-workflow`
- 是结构整理：`safe-refactor`
- 可能影响很多调用方：`impact-analysis`
- 想并行但不确定值不值得：`multi-agent-protocol`
- 只想把验证缩到最小：`targeted-validation`
- 用户说“评审/审核/review …”：按被审产物选 `requirements-review-loop` / `design-review-loop` / `plan-review-loop` / `code-review-loop` / `test-review-loop`

## 接下来读什么
<div class="title-en">Read Next</div>

- 想按任务判断该选哪个技能：看[技能选择](SKILL-SELECTION.md)
- 想看具体任务怎么跑：看[常见工作流](COMMON-WORKFLOWS.md)
- 想理解为什么这样分层和这样选择：看[关键机制](KEY-MECHANISMS.md)和[决策原因](DECISION-RATIONALE.md)
