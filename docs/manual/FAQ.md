# 常见问题
<div class="title-en">FAQ</div>

这页提供的是高频问题的快速答案。  
如果你需要完整解释，优先回到对应章节：安装问题看[安装说明](INSTALLATION.md)，机制问题看[关键机制](KEY-MECHANISMS.md)，使用决策看[决策原因](DECISION-RATIONALE.md)，排错看[故障排查](TROUBLESHOOTING.md)。

## 这套项目到底是什么
<div class="title-en">What Is This Project</div>

`agent-skills` 是一套给编码 Agent 使用的行为技能库。  
它不负责教 Agent 某种编程语言，而是约束 Agent 在真实仓库里怎样缩小范围、计划修改、控制改动规模、选择验证方式，以及在需要时怎样并行协作。

## 我应该选哪条安装路径
<div class="title-en">Which Install Mode Should I Choose</div>

普通使用者的公开安装入口是 `manage-governance.py`，但有两种使用方式：

- 想在你自己的机器上跨项目复用，选全局安装：`--global`
- 想让某个项目自己携带技能和治理规则，选项目安装：`--project /path/to/my-repo`

如果你想看完整说明，先读[安装说明](INSTALLATION.md)。

## `skill` 和 `governance` 的区别是什么
<div class="title-en">What Is the Difference Between Skill and Governance</div>

最简单的理解方式是：

- `skill` 是单个行为模块
- `governance` 是项目级路由和约束层

前者回答“某类任务该怎么做”，后者回答“什么时候该启用哪个技能、怎样交接、什么时候退出”。

如果你想看更完整的解释，去读[关键机制](KEY-MECHANISMS.md)。

## 我去哪里看每个技能的介绍
<div class="title-en">Where Can I Read About Each Skill</div>

如果你想先快速建立整体印象，直接看[技能索引](SKILL-INDEX.md)。

那一章会按类别介绍每个技能是做什么的、适合在什么情况下作为起点。  
如果你已经带着具体任务来选技能，再继续读[技能选择](SKILL-SELECTION.md)。

## 全局安装和项目安装的区别是什么
<div class="title-en">What Is the Difference Between Global and Project Install</div>

最核心的区别是“安装结果落在哪里”。

- 全局安装把技能装到用户级平台目录，适合个人默认环境
- 项目安装把技能装到目标项目里，并可同时注入 `AGENTS.md` 或 `CLAUDE.md`

如果你需要项目内可见的治理规则，就不要只做全局安装。

## 我可以只安装一个技能吗
<div class="title-en">Can I Install Just One Skill</div>

当前公开支持的安装入口不是“单个技能安装”，而是通过 `manage-governance.py` 安装完整技能库，并按需要选择是否同时注入治理规则。  

如果你只是想减少对目标项目的改动，可以使用：

- `--skills-only`
- `--rules-only`

如果你想看完整命令，去读[安装说明](INSTALLATION.md)。

## 为什么 `AGENTS.md` 看起来不像技能手册
<div class="title-en">Why `AGENTS.md` Does Not Look Like a Skill Manual</div>

因为它本来就不是技能手册。

在这个项目里：

- `AGENTS.md` 是路由和治理层
- 每个技能的正文都在各自的 `SKILL.md`

`AGENTS.md` 负责回答“什么时候启用哪个技能，如何交接，什么时候停用”，而不是重复解释每个技能的细节。

如果你想看这组机制的完整分层解释，去读[关键机制](KEY-MECHANISMS.md)。

## 安装后为什么会出现 `AGENTS.md` 或 `CLAUDE.md`
<div class="title-en">Why `AGENTS.md` or `CLAUDE.md` Appears After Installation</div>

因为项目安装做的不只是“复制技能”，还会把治理规则写进目标项目。

这些文件通常是从仓库里的治理模板生成出来的，作用是把：

- 什么时候启用哪个技能
- 技能之间如何交接
- 什么时候该升级、降级或停用

这些项目级规则稳定地落到目标项目里。

所以它们不是多出来的技能正文，而是技能之外的治理规则载体。  
如果你想看更完整的使用者解释，去读[关键机制](KEY-MECHANISMS.md)。

## 我是不是一开始就要用阶段技能
<div class="title-en">Do I Need Phase Skills Right Away</div>

通常不需要。

`phase-plan`、`phase-plan-review`、`phase-execute` 适合的是多模块、多 PR、多波次协调的大任务。  
如果你只是处理普通开发任务，一开始更适合从基础组合开始：

- `scoped-tasking`
- `plan-before-action`
- `minimal-change-strategy`
- `targeted-validation`

## 编辑点不明确时，为什么先用 `read-and-locate`
<div class="title-en">Why Use `read-and-locate` When the Edit Point Is Unclear</div>

因为最容易失控的情况，就是编辑点还没找到，工作集已经膨胀了。

`read-and-locate` 的价值不在于“多读一点”，而在于：

- 从最强线索开始
- 只追相邻路径
- 区分已确认位置和待确认线索
- 一旦编辑点清楚就停止继续浏览

## 缺陷修复为什么不能直接改
<div class="title-en">Why Not Edit a Bugfix Immediately</div>

因为症状不等于根因。

如果没有先确认故障域，就直接下手修，常见结果是：

- 只修掉了表面现象
- 修复建立在错误假设上
- 引入新回归

所以这个项目强调缺陷修复要先证据、后修改。

## 多代理是不是默认更快
<div class="title-en">Is Multi-Agent Always Faster</div>

不是。

只有在任务可以拆成低耦合子问题时，并行才值得。  
如果多个子问题共享同一编辑面，或者汇总和冲突裁决成本很高，并行反而会更慢。

## 我怎么判断这套技能真的在起作用
<div class="title-en">How Do I Know the Skills Are Working</div>

不要只看最后结果，还要看过程。

最值得观察的是：

- 有没有先缩小边界
- 有没有先给出计划
- 改动有没有保持局部
- 验证有没有针对直接受影响的面
- 在证据不足时有没有保留不确定性

如果你想快速验证，可以看[快速开始](QUICK-START.md)、[故障排查](TROUBLESHOOTING.md)和[技能测试快速开始](../user/SKILL-TESTING-QUICK-START.md)。
