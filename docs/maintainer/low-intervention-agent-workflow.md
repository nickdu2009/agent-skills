# Low-Intervention Agent Workflow

**Status**: Proposal / not implemented
**Implementation note**: This document records the intended protocol. It does not currently create an `autonomous-coding-workflow` skill, update governance templates, or add trigger tests.

## Purpose

这篇文档记录一套面向外部项目的低人工介入 AI coding agent 工作协议。

它不是某个业务项目的执行计划，也不是单个 skill 的说明。它面向维护 `agent-skills` 仓库的人，用来回答：

- 如何把现有 skills 串成更自动化的开发流程
- 哪些场景应该默认继续执行
- 哪些风险边界必须停下来请求人工确认
- 后续如果新增顶层编排 skill，应该遵循什么设计边界

核心原则：

```text
默认自动推进，风险升级才停下。
```

## Positioning

`agent-skills` 是给其它项目使用的 AI coding agent 技能库和治理模板。低人工介入协议的目标不是让本仓库本身少问确认，而是让被安装到外部项目中的 agent 能更稳定地完成完整开发循环。

这套协议应该主要落在 governance 层：

- `skills/*/SKILL.md` 继续定义单个能力模块
- `templates/governance/*-template.md` 负责路由、交接、升级和确认边界
- `docs/maintainer/` 记录维护者设计意图和演进约束

不要把某个 skill 的完整执行步骤复制进治理模板。模板只应描述“什么时候自动接下一步”和“什么时候必须停下”。

## Default Development Pipeline

推荐把一次开发任务理解为下面的流水线：

```text
intake
-> scope
-> choose workflow
-> execute
-> self-review
-> targeted-validation
-> state or handoff
```

对应当前技能体系：

```text
scoped-tasking
-> bugfix-workflow / safe-refactor / design-before-plan / review-loop
-> self-review
-> targeted-validation
-> worktrail-state / worktrail-handoff
```

这条流水线不是要求每个任务都完整跑一遍。小任务可以走 fast path；长任务、跨模块任务或高风险任务才需要完整链路。

## Supported Scenarios

### Bug Fix

用户描述失败测试、报错、异常行为或回归问题时，推荐链路是：

```text
scoped-tasking -> bugfix-workflow -> self-review -> targeted-validation
```

agent 应先收集证据和收窄故障域，而不是立即猜测原因。修复完成后，如果变更不止一行或影响多个调用点，应自动进入 `self-review` 和 `targeted-validation`。

### Small Feature Or Local Change

目标清楚、影响面局部的小功能可以自动完成：

```text
scope -> lightweight plan -> implement -> targeted-validation
```

适合加字段、补校验、改 CLI 参数、调整已有页面状态、接入已有 API 等场景。只要不触碰公共契约、数据迁移、依赖或发布动作，就不应该要求用户逐步批准。

### Multi-File Change

当任务涉及多个文件或需要明确顺序时，先按 `AGENTS.md` 的 plan + verify 结构生成短计划，再执行：

```text
scoped-tasking -> plan -> implement -> self-review -> targeted-validation
```

计划应包含最小边界、顺序依赖、共享写入面和验证方式。执行中如果发现范围扩大，应回退到 `scoped-tasking` 或升级到设计/影响分析。

### Safe Refactor

用户要求重构、抽取、合并重复逻辑或简化代码时，推荐链路是：

```text
scoped-tasking -> safe-refactor -> self-review -> targeted-validation
```

默认假设行为和接口保持不变。任何行为变更都应被显式标出，并在必要时请求用户确认。

### Design And Contract Work

涉及多个方案、公共接口、数据模型、跨模块契约或验收标准不清时，先不要直接实现：

```text
scoped-tasking -> design-before-plan -> impact-analysis
```

这类任务的自动化重点是澄清约束、比较方案和评估影响面，而不是绕过人工决策。

### Review Loops

需求、设计、计划、代码和测试产物分别由对应 review-loop 处理：

```text
requirements-review-loop
design-review-loop
plan-review-loop
code-review-loop
test-review-loop
```

review-loop 的自动化规则是：

```text
review -> revise or fix -> validate -> re-review until review_result: clean
```

当输出已经是 `review_result: clean`，并且 `next` 指向非破坏性的明确后续动作时，agent 可以默认继续下一步。

### Parallel Investigation

多个独立方向可以用 `multi-agent-protocol` 分派：

```text
multi-agent-protocol -> subagents -> synthesis
```

适合跨模块影响分析、多路径性能排查、升级依赖前评估调用点等场景。写能力 subagent 仍要遵循项目的委派声明和并发上限。

### Long Task Continuity

长任务、容易上下文压缩的任务或跨会话任务，应自动使用 Worktrail：

```text
worktrail context -> work -> worktrail state -> worktrail handoff
```

状态记录应保留目标、约束、证据、决策、已做工作、验证、开放问题和下一步，不记录密钥、生产数据或私有运行载荷。

## Automatic Continuation Rules

在以下条件同时满足时，agent 应默认继续推进，而不是向用户请求下一步确认：

- 当前动作是只读探索、局部编辑或本地验证
- 目标范围已经明确，且没有新增行为歧义
- review-loop 已返回 `review_result: clean`
- `next` 字段或计划中的下一步是明确且非破坏性的
- 验证可以在本地执行，不访问生产系统或真实用户数据
- 改动不涉及公共接口、持久化 schema、依赖、提交、推送或发布

典型例子：

```text
plan-review-loop -> review_result: clean -> next: ready to execute
```

如果 plan 中的下一步只是实现局部代码并跑本地验证，agent 可以继续执行实现、自审和验证。

## Human Confirmation Boundaries

下面这些情况必须停下来请求人工确认：

- 需求、验收标准或预期行为存在实质歧义
- 修改公共 API、跨模块契约、持久化 schema、数据迁移或兼容性策略
- 删除、重命名或批量移动大量文件
- 安装新依赖、修改工具链、升级运行时或改变构建系统
- 执行 `git commit`、`git push`、发布、部署或 force 操作
- 访问生产环境、外部服务、真实用户数据、密钥或凭据
- 运行破坏性命令，或可能覆盖用户未提交改动
- 自动流程发现风险已经超出原任务边界

这条边界的意图是把人工介入集中在风险决策点，而不是每个普通步骤。

## Candidate Orchestration Skill

如果后续要把这套协议沉淀成顶层编排 skill，可以考虑新增：

```text
autonomous-coding-workflow
```

它的职责应是路由和交接，而不是替代现有 skills：

```text
bug/error/failing
  -> scoped-tasking -> bugfix-workflow -> self-review -> targeted-validation

refactor/cleanup/simplify
  -> scoped-tasking -> safe-refactor -> self-review -> targeted-validation

requirements/design/plan/test review
  -> matching review-loop -> revise -> re-review until clean

multi-file implementation
  -> scoped-tasking -> plan -> implement -> self-review -> targeted-validation

long or risky task
  -> worktrail context/state/handoff
```

Non-goals for this skill:

- 不复制其它 skill 的详细步骤
- 不绕过高风险确认边界
- 不替代 `targeted-validation` 的验证选择
- 不让所有任务强制走完整重流程
- 不把外部项目的业务特例写入通用技能库

## Governance Template Guidance

如果把低人工介入协议写入 `AGENTS-template.md` 或 `CLAUDE-template.md`，建议只写成短规则：

```text
Low-Intervention Mode:
- Continue automatically when the next action is clear, local, non-destructive, and within scope.
- If a review loop returns review_result:"clean" with an explicit non-destructive next step, proceed to that next step.
- Ask for confirmation before public contract changes, migrations, dependency/toolchain changes, destructive file operations, commits, pushes, releases, production access, or ambiguous behavior decisions.
```

模板里不应展开每个场景的完整链路。完整解释留在本文档和对应 `SKILL.md`。

## Rollout Strategy

建议按保守自动化逐步推进：

1. 先在维护文档中固定协议和确认边界
2. 再把短版规则加入治理模板
3. 用触发测试验证不会导致过度自动化
4. 观察外部项目使用反馈
5. 如果稳定，再考虑新增 `autonomous-coding-workflow`

成功标准：

- 小任务不再频繁要求用户手动说“继续”
- 高风险动作仍会停下来请求确认
- review-loop 的 `clean -> next` 能形成稳定交接
- agent 的最终输出能说明做了什么、如何验证、还有什么残余风险

## Related Docs

- [`skill-and-governance-architecture.md`](skill-and-governance-architecture.md)
- [`skill-chain-aliases.md`](skill-chain-aliases.md)
- [`review-loop-mainchain-design.md`](review-loop-mainchain-design.md)
- [`../manual/COMMON-WORKFLOWS.md`](../manual/COMMON-WORKFLOWS.md)
