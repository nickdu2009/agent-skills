# Maintainer Docs Index

## Purpose

这页是 `docs/maintainer/` 的维护者入口。  
它面向维护 `agent-skills` 仓库本身的人，用来回答三类问题：

- 这套系统内部怎么分层
- 模板、技能、安装器和手册分别该改哪里
- 维护时应该从哪篇文档进入

如果你的目标是安装、选型、工作流和排错，请先回到[`Agent Skills 使用手册`](../manual/README.md)。

## Start Here

第一次进入 maintainer 文档，优先看这两篇：

- [`skill-and-governance-architecture.md`](skill-and-governance-architecture.md)  
  先看 skill 层、governance 层、治理模板边界，以及 `docs/manual/` 和 `docs/maintainer/` 的文档分工。
- [`manual-and-repo-development.md`](manual-and-repo-development.md)  
  再看手册预览、本地 mirror、canonical source，以及仓库维护相关工作流。

## Document Status

维护文档按状态阅读，不要把历史报告当成当前实现：

- **Current authority**: 当前维护入口、治理模板说明、canonical source 说明。这里必须和仓库实现一致。
- **Proposal / roadmap**: 设计想法、候选 skill、未来 rollout。除非明确写入 `skills/`、`templates/governance/` 或维护脚本，否则不代表已经实现。
- **Partial implementation**: 已有一部分能力，但还有未完成的测试、模板、CI 或文档闭环。阅读时先看实现状态说明。
- **Historical snapshot**: 某个时间点的评估、报告或基线。保留用于追溯决策，不作为当前架构依据。
- **Superseded**: 已被新机制替代的旧方案。保留时应在开头标明替代来源。

修订规则：优先修正 Current authority；Proposal 和 Partial implementation 补状态说明；Historical snapshot 只加醒目的历史提示，不大面积重写正文。

## Deprecated Terminology

下列术语在 2026-05 治理 cleanup 后已退场。如果在历史文档（plan / tracker / report / `*-2026-04-*.md` / 已退役 v 版本等）里看到它们，请按下表回到当前权威：

| 已废弃术语 | 当前权威 |
|---|---|
| `Skill Chain Triggers` | `AGENTS.md` / `CLAUDE.md` § Common Flow Patterns 与 `templates/governance/AGENTS-template.md` 的同名段 |
| `Skill Protocol v1` / `Skill Protocol v2` | `AGENTS.md` / `CLAUDE.md` § Skill Protocol（已合并、不再分版本） |
| `Skill Family Concurrency Budgets` | `AGENTS.md` § Multi-Agent Rules 的 Tier 1/2 + Overflow，以及 `multi-agent-protocol` 技能 |
| `minimal-change-strategy`、`plan-before-action`、phase-* 技能 | 已退役；规划与 surgical 约束并入 `AGENTS.md` § Behavioral Guidelines §3-§4 |
| `.cursor/skills/` / `.claude/skills/` 仓库内镜像 | 已弃用；canonical source 仅 `skills/`，安装由 `maintainer/scripts/install/manage-governance.py` 注入 |

历史文档中保留这些术语用于追溯决策；当前实现请以仓库根 `AGENTS.md` / `CLAUDE.md` 与 `templates/governance/` 为准。如某历史文件没有头部 `**Status**` 标记，默认按 *Historical snapshot* 解读（除非从 [Start Here](#start-here) 入口被显式引用为当前权威）。

## Go By Task

- 我在维护治理模板、平台注入边界或 `AGENTS.md` / `CLAUDE.md` 的来源：  
  [`skill-and-governance-architecture.md`](skill-and-governance-architecture.md)

- 我在设计如何让外部项目中的 agent 少问确认、自动串联开发流程：  
  [`low-intervention-agent-workflow.md`](low-intervention-agent-workflow.md)

- 我想知道模板里该放什么、不该放什么，当前各 section 在负责什么：  
  [`skill-and-governance-architecture.md`](skill-and-governance-architecture.md)

- 我在维护手册、手册预览、本地 mirror 或仓库内部文档：  
  [`manual-and-repo-development.md`](manual-and-repo-development.md)

- 我在做技能测试、场景验证或维护者视角的评估：
  [`skill-system-evaluation.md`](skill-system-evaluation.md)（历史快照，待重写）
  [`current-test-evaluation.md`](current-test-evaluation.md)（历史快照）
  [`../user/SKILL-TESTING-QUICK-START.md`](../user/SKILL-TESTING-QUICK-START.md)

- 我在做 Claude 交互式场景验证：  
  [`claude-interactive-test-checklist.md`](claude-interactive-test-checklist.md)  
  [`claude-interactive-test-implementation-plan.md`](claude-interactive-test-implementation-plan.md)

## Boundary Reminder

- `docs/manual/` 讲的是最终使用者如何理解和使用这套系统
- `docs/maintainer/` 讲的是维护者如何维护技能、治理规则、模板和仓库文档
- `templates/governance/` 里的模板是治理规则源文件，不是维护者教程首页
