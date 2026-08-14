# Agent Skills 使用手册
<div class="title-en">Agent Skills Usage Manual</div>

这是一套独立的使用手册目录，用来沉淀面向最终使用者的系统化说明。

这套手册优先回答下面几个问题：

- 这个项目是什么，解决什么问题
- 我应该选择哪些 Skill
- 不同任务应该怎样组合技能
- 我如何把这套技能真正用到日常开发里
- 遇到问题时应该如何排查

为避免同一件事在多处重复展开，这套手册按几个层次拆开：

- [快速开始](QUICK-START.md) / [接入 Agent Skills](INSTALLATION.md): 先解决如何交付完整标准包、如何按运行时文档接入并验证
- [设计理念](DESIGN-PHILOSOPHY.md) / [关键机制](KEY-MECHANISMS.md) / [决策原因](DECISION-RATIONALE.md): 再解释为什么这样设计、机制是什么、为什么这样选
- [技能索引](SKILL-INDEX.md) / [技能选择](SKILL-SELECTION.md) / [常见工作流](COMMON-WORKFLOWS.md): 再落到每个技能是什么、怎么选技能、怎么走流程
- [故障排查](TROUBLESHOOTING.md) / [常见问题](FAQ.md): 最后收口排错和高频问题

## 推荐阅读顺序
<div class="title-en">Recommended Reading Order</div>

1. [快速开始](QUICK-START.md)
2. [设计理念](DESIGN-PHILOSOPHY.md)
3. [关键机制](KEY-MECHANISMS.md)
4. [接入 Agent Skills](INSTALLATION.md)
5. [技能索引](SKILL-INDEX.md)
6. [技能选择](SKILL-SELECTION.md)
7. [决策原因](DECISION-RATIONALE.md)
8. [常见工作流](COMMON-WORKFLOWS.md)
9. [故障排查](TROUBLESHOOTING.md)
10. [常见问题](FAQ.md)

## 按目标阅读
<div class="title-en">Recommended Paths by Goal</div>

- 我想先交付标准包并跑通一次： [快速开始](QUICK-START.md) -> [接入 Agent Skills](INSTALLATION.md) -> [故障排查](TROUBLESHOOTING.md) -> [常见问题](FAQ.md)
- 我想先理解这套方法为什么这样设计： [设计理念](DESIGN-PHILOSOPHY.md) -> [关键机制](KEY-MECHANISMS.md) -> [决策原因](DECISION-RATIONALE.md) -> [常见工作流](COMMON-WORKFLOWS.md)
- 我想先知道每个技能分别是什么： [关键机制](KEY-MECHANISMS.md) -> [技能索引](SKILL-INDEX.md) -> [技能选择](SKILL-SELECTION.md)
- 我想按任务选择合适的技能： [关键机制](KEY-MECHANISMS.md) -> [技能索引](SKILL-INDEX.md) -> [技能选择](SKILL-SELECTION.md) -> [决策原因](DECISION-RATIONALE.md) -> [常见工作流](COMMON-WORKFLOWS.md)
- 我已经遇到问题，想快速排错： [快速开始](QUICK-START.md) -> [接入 Agent Skills](INSTALLATION.md) -> [故障排查](TROUBLESHOOTING.md) -> [常见问题](FAQ.md)

如果你不确定自己属于哪一类，默认从[快速开始](QUICK-START.md)开始，再按上面的分支继续。

## 章节导览
<div class="title-en">Chapter Guide</div>

- [快速开始](QUICK-START.md): 先跑通一次标准包交付与验证
- [设计理念](DESIGN-PHILOSOPHY.md): 解释这套技能体系背后的基本方法论
- [关键机制](KEY-MECHANISMS.md): 解释使用者会直接遇到的关键机制
- [接入 Agent Skills](INSTALLATION.md): 说明唯一的标准包交付方式，以及按运行时官方文档接入的边界
- [技能索引](SKILL-INDEX.md): 独立介绍每个技能的定位与用途
- [技能选择](SKILL-SELECTION.md): 从任务形态出发选择技能
- [决策原因](DECISION-RATIONALE.md): 解释常见使用决策背后的原因
- [常见工作流](COMMON-WORKFLOWS.md): 给出从任务到执行的典型流程
- [故障排查](TROUBLESHOOTING.md): 汇总排错与常见误区
- [常见问题](FAQ.md): 汇总高频使用问题和快速答案

## 范围说明
<div class="title-en">Scope</div>

这个目录面向两类读者：

- 想把完整 Agent Skills 标准包交付到运行时支持位置的个人使用者
- 想组合这些标准 Skill、但不引入客户端专属适配层的团队使用者

以下内容不作为本目录重点：

- 维护者内部评测脚本
- 手册本地预览方式
- 仓库内部开发用安装机制
- 当前仓库自身的维护工作流
- 基线报告生成细节
- 仓库内部实验性优化记录
