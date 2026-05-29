# Template-First Governance Roadmap

**Status**: Partial implementation
**Implementation note**: The first increment from this roadmap is now implemented in the working tree: template behavior boundaries, isolated governance evaluator refresh, and the sync/smoke validation chain. The remaining future work is the later consolidation track (`P2`) and any follow-on tightening not covered by the first increment.

## Purpose

这篇文档回答的不是“治理模板现在怎么分层”，而是“在已经明确模板权威边界之后，下一步治理应该先改什么、后改什么”。

它面向维护 `agent-skills` 仓库的人，用来回答三类问题：

- 如何在不破坏 template-first 边界的前提下继续改进治理
- 如何把“少问确认、自动串联”的目标真正落到模板层
- 模板、安装器、生成结果、验证脚本和维护文档应该按什么顺序收敛

## Positioning

这篇文档是以下两篇文档之间的桥梁：

- [`skill-and-governance-architecture.md`](skill-and-governance-architecture.md)  
  说明 skill 层、governance 层、模板源文件与生成结果的边界
- [`low-intervention-agent-workflow.md`](low-intervention-agent-workflow.md)  
  说明目标行为，即 agent 什么时候应默认继续推进、什么时候必须停下确认

前者回答“权威在哪里”，后者回答“希望出现什么行为”。  
这篇路线图回答的是：**怎样以模板为唯一真相源，把目标行为分阶段落地**。

## Template-First Principles

这份路线图建立在四条前提之上：

1. `templates/governance/*.md` 是共享治理权威  
   模板定义路由、交接、升级、退出和通用执行约束。
2. 生成出的 `AGENTS.md` / `CLAUDE.md` 只是模板投影  
   它们可以作为当前落地状态的观察面，但不应反向成为治理源文件。
3. 安装器、验证脚本和维护文档都应追随模板  
   任何治理改动都应先改模板，再让投影和验证收敛。
4. 这条路线图优先改 governance，不优先扩 skill 数量  
   当前最需要补的是模板行为边界与闭环验证，而不是新增更多能力模块。
5. 这份路线图只讨论 governance 层权威，不改动 skill 层 canonical source 的定义  
   `manual-and-repo-development.md` 中“`skills/` 是唯一 canonical source”仍适用于 skill 内容本身；template-first 只用于治理模板层。

## Roadmap Summary

| Phase | Goal | Primary surfaces | Verify |
|---|---|---|---|
| `P0` | 把“默认继续 / 必须停下”的行为边界写进模板 | `templates/governance/*` | 只看模板也能判断常见任务的继续/停下边界 |
| `P1` | 让安装与验证围绕模板形成闭环 | `maintainer/scripts/install/*`, `maintainer/scripts/analysis/*`, `maintainer/scripts/evaluation/*`, `maintainer/governance_eval/*` | 模板改动后，投影和行为测试都能跟上 |
| `P2` | 收敛协议语义、镜像维护和治理健康度 | 模板 + 验证 + 维护文档 | 模板仍是唯一权威，维护成本下降 |

## Execution Shape

```text
[parallelism:
- independent lanes: 模板规则设计 与 行为样例设计 可并行；安装/验证加固 与 维护清单固化 可并行
- sequential blockers: 先收敛模板中的“继续/停下”边界，再补行为回归，最后再做协议和镜像优化
- shared write surfaces: templates/governance/*, maintainer/scripts/install/*, maintainer/scripts/analysis/*, maintainer/scripts/evaluation/*, maintainer/governance_eval/*, docs/maintainer/*
- delegation: 0 with reason: 本文档只定义路线图，不拆分执行子线
]
```

## P0: Clarify Template Behavior Boundaries

`P0` 的目标是：让模板本身能够独立回答“当前任务应该默认继续，还是必须停下确认”。

这一步不要求引入新 skill，也不要求重写治理结构。  
重点是把低人工介入协议中最关键的边界真正写进现有模板 section，而不是继续停留在 proposal 文档里。

### Where The New Rules Should Land

优先使用现有模板 section，除非现有结构明显无法承载，否则不要新增顶层 section：

| Current template section | P0 should add or tighten |
|---|---|
| `Behavioral Guidelines` | 明确默认继续原则：局部编辑、本地验证、非破坏性下一步可以自动推进；风险升级才停下 |
| `Validation Rules` | 明确哪些验证可在本地默认执行，哪些验证因为涉及外部系统、真实数据或高成本操作必须停下 |
| `Skill Activation` | 区分 fast path 与需要完整链路的任务形状，减少对轻量任务的过度升级 |
| `Escalation Rules` | 明确哪些信号必须触发 `design-before-plan`、`impact-analysis` 或人工澄清 |
| `Common Flow Patterns` | 标注哪些链路允许自动进入下一步，哪些链路遇到公共契约、迁移、依赖、发布动作时必须中断 |
| `Multi-Agent Rules` | 保持委派边界清晰，避免“能并行”被误读成“默认并行” |

### P0 Deliverables

- 模板内明确写出 `default continue` 与 `must ask` 的判断边界
- 模板内明确 fast path 与 full path 的区分
- 模板内明确 review clean 后、局部编辑后、本地验证前后的自动衔接条件
- 一组最小化治理样例，覆盖：
  - 小范围本地改动
  - 多文件改动
  - 设计 / 契约工作
  - schema / migration
  - 依赖、提交、推送、发布

### P0 Verify

- 只读模板时，维护者能够对一组常见任务稳定判断 `continue` 或 `ask`
- `AGENTS-template.md` 与 `CLAUDE-template.md` 在边界语义上保持一致
- 不通过新增新 section 来掩盖现有 section 设计不清的问题

## P1: Close The Projection And Behavior Loop

`P1` 的目标是：模板不只是“写得对”，还要能稳定投影到生成结果，并能通过行为级测试验证。

### Work Items

1. **强化模板驱动的安装与替换路径**  
   安装器应继续以模板 section 顺序为唯一真相源，不保留模板之外的治理真相。

2. **增加模板导向的行为回归测试**  
   这里应明确区分两条验证线，避免把“安装投影验证”和“模板语义验证”混在一起：
   - **投影 smoke**：用临时项目运行安装流程，确认生成出的 `AGENTS.md` / `CLAUDE.md` 与模板同步
   - **行为回归**：优先在隔离工作区中直接评估模板本身，让 agent 只看到被测治理文件，而不是整个仓库或额外项目文件

   行为回归除了检查 section 是否存在，还要检查治理判断是否符合模板定义，例如：
   - 什么时候应 `trigger` / `skip` / `defer`
   - 什么时候应默认继续下一步
   - 什么时候必须请求人工确认
   - 什么时候应 `[delegate: 0]`

3. **固化模板改动后的维护链**  
   维护者在改模板后，应有固定清单：
   - 验证模板本身
   - 验证 fresh install 生成结果
   - 验证 repo 内投影结果
   - 用隔离工作区验证行为级样例或回归脚本
   - 再决定是否需要更新 maintainer / manual 文档

### P1 Verify

- 模板改动后，如果生成结果、行为样例或镜像模板漂移，验证会直接失败
- fresh install 与仓库内当前投影不会长期背离
- 模板语义验证与安装投影验证各自独立，避免因为工作区污染得到假阳性结果
- 模板变更不再依赖维护者记忆去补齐下游校验

## P2: Consolidate Protocol Semantics And Reduce Long-Term Drift

`P2` 的目标是：在不破坏 template-first 的前提下，继续降低治理维护成本，并让模板规则更容易测试。

### Work Items

1. **轻量收敛协议语义**  
   如果后续需要增强 `Skill Protocol`，应直接从模板 section 出发，优先收敛：
   - 输入校验语义
   - trigger / escalation 语义
   - output / validate / drop 的最小公共格式
   - 循环检测等保护信号（如确有必要）

   重点是“更可测试”，不是把系统做成重型 runtime。

2. **继续降低双模板维护成本**  
   明确哪些差异属于平台差异，哪些只是 mirror drift。  
   优先增强一致性检查，而不是放任两份模板自然分叉。

3. **建立治理健康度指标**  
   后续可以持续跟踪：
   - 模板投影一致率
   - 行为回归通过率
   - 额外确认率是否下降
   - routing 误判率是否下降
   - mirror drift 事件数

### P2 Verify

- 模板仍然是唯一共享权威，不出现“脚本另有真相”或“生成结果另有真相”
- 协议增强后，验证能力提升，但模板可读性没有明显退化
- 治理改动的维护成本低于改动前，而不是更高

## Out Of Scope For This Roadmap

下面这些方向不属于这份路线图的优先事项：

- 先扩 skill 数量来弥补治理问题
- 先改仓库根 `AGENTS.md` / `CLAUDE.md`，再倒推模板
- 直接全量复活历史版 `Skill Protocol v1`
- 引入重型图状态机或复杂 runtime
- 把 skill 级写作优化（例如 chain alias、skill contract 模板）混进 governance 主线

这些工作可能各自有价值，但不应抢占 template-first 治理闭环的优先级。

## Recommended First Increment

如果只做一个最小、可验证的增量，建议顺序如下：

1. 在现有模板 section 内补全 `continue` / `ask` / `must stop` 的判断边界
2. 在隔离工作区中直接针对模板运行 8 到 12 个治理样例，验证行为判断
3. 再用临时项目重新生成 `AGENTS.md` / `CLAUDE.md`，验证安装投影没有漂移
4. 固化“模板变更后的维护者验证清单”

这个增量完成后，再决定是否进入协议语义收敛或镜像维护优化。

## Relationship To Other Maintainer Docs

- 如果你要理解**为什么权威在模板里**，先看 [`skill-and-governance-architecture.md`](skill-and-governance-architecture.md)
- 如果你要理解**低人工介入目标行为本身是什么**，看 [`low-intervention-agent-workflow.md`](low-intervention-agent-workflow.md)
- 如果你要开始真正实施这份路线图，应把模板、安装器、验证脚本和 maintainer 文档的改动拆成独立增量，而不是一次性混改
