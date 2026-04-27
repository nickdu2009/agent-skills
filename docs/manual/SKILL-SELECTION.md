# 技能选择
<div class="title-en">Skill Selection</div>

## 目的
<div class="title-en">Purpose</div>

帮助使用者从任务出发选择技能，而不是从目录出发阅读全部技能。

如果你还不熟悉每个技能分别是什么，建议先读[技能索引](SKILL-INDEX.md)。

如果你想知道“为什么这样选”，请继续阅读[决策原因](DECISION-RATIONALE.md)。
如果你已经确定要走哪条主线、想看更具体的执行方式，请继续阅读[常见工作流](COMMON-WORKFLOWS.md)。

## 从小开始
<div class="title-en">Start Small</div>

默认建议从最小技能组合开始：

- `scoped-tasking`
- `plan-before-action`
- `minimal-change-strategy`
- `targeted-validation`

这组组合适合大多数普通开发任务，因为它先解决四个最基础的问题：

- 边界有没有先缩小
- 编辑前有没有先想清楚
- 改动有没有被压到最小
- 验证有没有先从最小充分开始

如果你还不确定从哪里开始，先从这组默认组合起步，通常比一开始就上更重的技能更稳。

## 一个简单决策流
<div class="title-en">A Simple Decision Flow</div>

选技能时，可以按下面顺序问自己：

1. 任务边界清楚吗
2. 编辑点清楚吗
3. 当前问题是普通改动、缺陷修复，还是结构性整理
4. 这次改动会不会碰到共享接口、共享类型或多个调用方
5. 任务能不能安全拆成低耦合子问题
6. 任务规模是否已经大到需要多 PR 或多波次协调

前面的回答没有清楚之前，不要急着跳到后面更重的机制。

## 按任务形态选择
<div class="title-en">Selection by Task Shape</div>

### 范围不清楚
<div class="title-en">Scope is unclear</div>

优先考虑：

- `scoped-tasking`

适用场景：

- 用户请求比较宽
- 你知道问题大概在哪，但边界还不稳定
- 你担心一上来就读太多文件

结束信号：

- 已经能说清楚这次只打算处理哪一小块问题

### 编辑点不明确
<div class="title-en">Edit point is unknown</div>

优先考虑：

- `read-and-locate`

适用场景：

- 你知道是哪个模块，但不知道该改哪个文件
- 你需要先沿着一条调用路径或数据路径把编辑点找出来

结束信号：

- 已确认位置和待确认线索已经分开
- 可能的编辑点已经清楚，可以进入计划或修改阶段

### 已报告缺陷但根因不清楚
<div class="title-en">Bug is reported but root cause is unclear</div>

优先考虑：

- `bugfix-workflow`

适用场景：

- 已经看到错误、异常或错误行为
- 但你还不能确认根因在什么地方

结束信号：

- 故障域已经缩小
- 根因假设已经被证据支持
- 可以开始最小修复

### 只做结构整理，不改行为
<div class="title-en">Structural cleanup without behavior change</div>

优先考虑：

- `safe-refactor`

适用场景：

- 目标是整理结构，不是改变行为
- 你想提取重复逻辑、简化局部复杂度、收拢职责

结束信号：

- 结构问题已经缓解
- 对外行为和接口仍保持稳定

### 共享接口或多调用方改动
<div class="title-en">Shared API or multi-caller change</div>

优先考虑：

- `impact-analysis`

适用场景：

- 改动会触及共享类型、公共接口、数据模型
- 某个函数或类型已有多个调用方

结束信号：

- 影响范围已经从“猜测”变成“有证据的调用面”
- 可以进入计划，而不是边改边猜

### 任务可拆成低耦合子问题
<div class="title-en">Task can be split into low-coupling subproblems</div>

优先考虑：

- `multi-agent-protocol`
- 必要时补 `conflict-resolution`

适用场景：

- 子问题之间边界清楚
- 每条线都能独立推进
- 汇总成本低于并行节省的时间

结束信号：

- 每条子线的结果都能被主代理统一汇总
- 冲突结论已显式处理，而不是被忽略

### 工作跨度为 2 到 4 个合并请求
<div class="title-en">Work spans 2-4 PRs</div>

优先考虑：

- `incremental-delivery`

适用场景：

- 一次做完太大
- 但又没大到需要阶段系统
- 可以拆成 2 到 4 个独立可合并增量

结束信号：

- 增量边界已经确定
- 每个增量都能独立验证和合并

### 工作需要按波次协调
<div class="title-en">Work needs wave-based coordination</div>

优先考虑：

- `phase-plan`
- `phase-plan-review`
- `phase-execute`

适用场景：

- 任务跨多个模块和多个阶段
- 需要波次、依赖、交接物和正式协调

结束信号：

- 波次结构已经建立
- 每一波的进入条件和交付物已经清楚

## 什么时候不要升级
<div class="title-en">When Not to Escalate</div>

不要为了“看起来更完整”而过早升级到更重的技能：

- 小范围改动，不要一开始就上 `phase-*`
- 编辑点已经明确时，不要再强行走 `read-and-locate`
- 单文件小修，不必默认拉起并行
- 纯信息问题，不要把执行型技能全都挂上

## 起步组合
<div class="title-en">Starter Compositions</div>

如果你只想要几组最常用组合，可以先从这里开始：

- 小范围普通改动：`scoped-tasking` + `plan-before-action` + `minimal-change-strategy` + `targeted-validation`
- 陌生区域定位：`scoped-tasking` + `read-and-locate` + `plan-before-action`
- 缺陷修复：`scoped-tasking` + `read-and-locate` + `bugfix-workflow` + `minimal-change-strategy` + `targeted-validation`
- 安全重构：`scoped-tasking` + `safe-refactor` + `minimal-change-strategy` + `self-review` + `targeted-validation`
- 低耦合并行分析：`plan-before-action` + `multi-agent-protocol` + `conflict-resolution`（必要时） + `targeted-validation`

## 这一章补充了什么
<div class="title-en">What This Chapter Adds</div>

- 任务到技能的决策表
- 什么时候不该启用某个技能
- 一组可直接上手的常见技能链
