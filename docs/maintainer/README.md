# Maintainer Docs Index

本目录记录 Skill 内容、协议、评测与 token 优化。当前实现边界以代码和根 [`README.md`](../../README.md) 为准。

## 当前权威

- `skills/` 是唯一可分发 Agent Skills 树。
- 每个 Skill 包含 `SKILL.md` 与同目录 supporting files。
- 根 `AGENTS.md` 只治理本仓库，不作为模板或分发物。
- 仓库不维护运行时安装器、发现路径、治理 renderer、sidecar 或专属验收 runner。

## 维护入口

- Skill 格式与引用：[`../../maintainer/README.md`](../../maintainer/README.md)
- Skill 使用与接入：[`../manual/README.md`](../manual/README.md)
- 协议说明：[`../user/SKILL-PROTOCOL-V2.md`](../user/SKILL-PROTOCOL-V2.md)
- 测试快速开始：[`../user/SKILL-TESTING-QUICK-START.md`](../user/SKILL-TESTING-QUICK-START.md)
- Skill chain：[`skill-chain-aliases.md`](skill-chain-aliases.md)

## 历史材料

带日期的分析、tracker、优化报告、旧版协议及 [`review-loop-mainchain-design.md`](review-loop-mainchain-design.md) 通常是历史快照，只用于追溯当时的判断。若其描述了已经删除的适配层、模板或测试入口，不得当作当前操作说明。

维护当前文档时，应把客户端无关的内容沉淀到 portable Skill 或通用评测；真实运行时差异留待出现兼容需求时重新验证和设计。
