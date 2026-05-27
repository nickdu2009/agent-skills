# 快速开始
<div class="title-en">Quick Start</div>

## 目标
<div class="title-en">Goal</div>

用最短路径完成一次真实可用的安装，并确认这套技能已经可以被你的 Agent 发现和使用。

这一章只保留第一次上手最需要的步骤。  
如果你想完整比较当前支持的安装路径和边界，直接继续读[安装说明](INSTALLATION.md)。

## 适合谁
<div class="title-en">Who This Is For</div>

- 第一次接触 `agent-skills`
- 希望先跑通，再决定是否深入治理能力

## 接着读什么
<div class="title-en">Read This Next</div>

如果你已经完成第一次安装，下一步建议阅读：

- [设计理念](DESIGN-PHILOSOPHY.md)，理解这套技能体系为什么这样工作
- [关键机制](KEY-MECHANISMS.md)，理解 `skill`、`governance` 和 `AGENTS.md` 的分工

## 选择安装入口
<div class="title-en">Choose the Supported Entry</div>

先回答一个问题：你是想让这套技能和治理规则成为你机器上的默认能力，还是想把它接入某个具体项目？

### 方案 A：用户级安装
<div class="title-en">Option A: User Install</div>

适合你如果：

- 主要是个人使用
- 想在多个项目里复用同一套技能和治理规则
- 不需要给某个项目提交治理文件

最短命令路径：

```bash
python3 maintainer/scripts/install/manage-governance.py install user
```

安装完成后，你通常会得到：

- 用户级平台目录中的技能
- Codex 用户级 `AGENTS.md` 或 Claude Code 用户级 `CLAUDE.md`
- Cursor 用户级 skills（治理规则需要手动复制到 Cursor User Rules）
- 一个跨项目可复用的默认技能与治理环境
- 不改项目文件的安装结果

### 方案 B：项目安装
<div class="title-en">Option B: Project Install</div>

适合你如果：

- 想把这套技能用到自己的项目
- 希望 Agent 能同时获得技能内容和治理规则
- 想让团队在同一个项目里看到一致行为
- 希望治理规则随仓库提交和共享

最短命令路径：

```bash
python3 maintainer/scripts/install/manage-governance.py install project /path/to/my-repo
```

安装完成后，你通常会得到：

- 安装到对应平台目录中的技能
- 注入到目标项目里的治理规则
- 一个更完整的“技能 + 治理规则”使用环境

第一轮验证建议：

- 目标项目里已经生成或更新了 `AGENTS.md`
- 平台对应的技能安装目录里已经出现技能
- Agent 在真实任务里开始表现出更稳定的边界控制、计划和验证习惯

如果你需要调整已有安装结果，可以后续再看[安装说明](INSTALLATION.md)里的 `--overwrite-skills` 和 `--replace-rules`。

## 首次验证
<div class="title-en">First Validation</div>

第一次验证建议做两件事。

### 1. 确认技能可以被发现
<div class="title-en">Confirm Skills Are Discoverable</div>

如果你走的是用户级安装，优先确认：

- `verify user` 能正常通过
- 重启对应 Agent 后能重新发现已安装技能
- 如果你使用 Cursor，已手动把治理规则复制到 Cursor User Rules；更新旧规则时要确认 `Behavioral Guidelines` §4 已包含 `[parallelism: ...]` 计划块

```bash
python3 maintainer/scripts/install/manage-governance.py verify user
```

如果你走的是项目安装，优先确认：

- 目标项目里已经生成或更新了 `AGENTS.md`
- 对应平台的技能安装目录已经出现技能内容

```bash
python3 maintainer/scripts/install/manage-governance.py verify project /path/to/my-repo
```

### 2. 跑一个最小场景
<div class="title-en">Run a Small Scenario</div>

第一次不要上复杂任务，建议直接挑一个简单场景，观察 Agent 是否开始表现出这套技能体系想要的行为：

- 先缩小边界
- 先判断是否值得并行，再给出计划
- 改动保持局部
- 验证保持针对性

如果你需要一个现成入口，可以继续看[技能测试快速开始](../user/SKILL-TESTING-QUICK-START.md)和 `examples/` 里的场景文件。

## 两个常见误区
<div class="title-en">Two Common Mistakes</div>

- 不要把用户级安装误当成项目安装。用户级安装会按已检测平台写入 Codex 或 Claude Code 的用户级治理规则；Cursor 仍需手动复制到 User Rules，而且不会往项目里写入 `AGENTS.md` 或 `CLAUDE.md`。
- 不要把安装对象理解成可拆分部件。这个库的公开安装对象始终是整套技能和治理模板。
