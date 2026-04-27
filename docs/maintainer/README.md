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

## Go By Task

- 我在维护治理模板、平台注入边界或 `AGENTS.md` / `CLAUDE.md` 的来源：  
  [`skill-and-governance-architecture.md`](skill-and-governance-architecture.md)

- 我想知道模板里该放什么、不该放什么，当前各 section 在负责什么：  
  [`skill-and-governance-architecture.md`](skill-and-governance-architecture.md)

- 我在维护手册、手册预览、本地 mirror 或仓库内部文档：  
  [`manual-and-repo-development.md`](manual-and-repo-development.md)

- 我在做技能测试、场景验证或维护者视角的评估：  
  [`skill-system-evaluation.md`](skill-system-evaluation.md)  
  [`current-test-evaluation.md`](current-test-evaluation.md)  
  [`../user/SKILL-TESTING-QUICK-START.md`](../user/SKILL-TESTING-QUICK-START.md)

- 我在做 Claude 交互式场景验证：  
  [`claude-interactive-test-checklist.md`](claude-interactive-test-checklist.md)  
  [`claude-interactive-test-implementation-plan.md`](claude-interactive-test-implementation-plan.md)

## Boundary Reminder

- `docs/manual/` 讲的是最终使用者如何理解和使用这套系统
- `docs/maintainer/` 讲的是维护者如何维护技能、治理规则、模板和仓库文档
- `templates/governance/` 里的模板是治理规则源文件，不是维护者教程首页
