# Manual And Repo Development

## Scope

这篇文档面向正在开发 `agent-skills` 仓库本身的人，而不是把这套 skills 接入外部项目的普通使用者。

这里集中放三类内容：

- `docs/manual/` 的本地预览方式
- local mirror 的同步与排错
- 与当前仓库维护直接相关的工作流示例

## Manual Preview

这套手册可以单独本地预览，不需要把整个仓库文档一起挂起来。

```bash
make docs-manual-serve
```

如果你想改端口：

```bash
make docs-manual-serve PORT=3001
```

如果你想预览维护者文档：

```bash
make docs-maintainer-serve
```

如果你想改端口：

```bash
make docs-maintainer-serve PORT=3001
```

## Local Mirror

### When To Use It

local mirror 只用于开发当前仓库本身。

适合以下场景：

- 你正在修改 `skills/`，想让本地工具重新发现技能
- 你正在调试手册、示例或技能引用
- 你需要验证 canonical `skills/` 树与本地工具目录是否一致

它不是：

- 外部项目的正式安装入口
- 发布源
- canonical source 的替代品

### Sync Local Mirror

```bash
python3 maintainer/scripts/install/manage-governance.py --sync-local cursor
python3 maintainer/scripts/install/manage-governance.py --sync-local claude
```

### Check Local Mirror

```bash
python3 maintainer/scripts/install/manage-governance.py --check-local cursor
python3 maintainer/scripts/install/manage-governance.py --check-local claude
```

## Canonical Source

`skills/` 是唯一 canonical source。

这意味着：

- 每个 skill 只在一个正式位置维护
- 本地 mirror 只是从 `skills/` 生成出来的便利层
- `.cursor/`、`.claude/` 等目录不应被当成正式源头继续手工维护

如果出现不一致，默认以 `skills/` 为准，不以 mirror 为准。

## Local Mirror Troubleshooting

### `--check-local` 失败怎么办

先不要手工修镜像目录，优先重新同步：

```bash
python3 maintainer/scripts/install/manage-governance.py --sync-local cursor
python3 maintainer/scripts/install/manage-governance.py --sync-local claude
```

然后再重新检查：

```bash
python3 maintainer/scripts/install/manage-governance.py --check-local cursor
python3 maintainer/scripts/install/manage-governance.py --check-local claude
```

### 本地镜像与 `skills/` 不一致怎么办

默认以 `skills/` 为准。  
local mirror 是从 canonical source 生成出来的便利层，不是你应该手工维护的主副本。

### 为什么 local mirror 不应该提交为发布源

因为一旦把它当成主源，就会破坏“`skills/` 是唯一 canonical source”这个前提，后续安装、扫描、验证都会变得混乱。

## Repository Workflows

下面这些示例适合开发当前仓库时参考，不属于普通使用者手册主线。

### 给单个 Skill 补边界说明

- 任务场景：你发现 `skills/scoped-tasking/SKILL.md` 的边界解释还不够直观，想补一小段更贴近仓库实际用法的说明。
- 推荐 skill 组合：`scoped-tasking` + `plan-before-action` + `minimal-change-strategy` + `targeted-validation`
- 执行顺序：
  1. 把范围压到一个目标 skill 文件。
  2. 在编辑前先说清楚这次只补什么。
  3. 按最小改动补充文字，沿用仓库里已经存在的概念。
  4. 自检新增内容是否和相关手册章节保持一致。
- 结束信号：
  - 改动仍然只落在一个 skill 文件
  - 新增说明已经能帮助使用者区分边界
  - 不需要连带修改其他 skill 或手册章节

### 先判断安装说明该改在哪一章

- 任务场景：使用者仍分不清 `manage-governance.py` 和 local mirror 的区别，但你还不确定真正 edit point 在 `docs/manual/QUICK-START.md`、`docs/manual/INSTALLATION.md` 还是 `docs/manual/TROUBLESHOOTING.md`。
- 推荐 skill 组合：`scoped-tasking` + `read-and-locate` + `plan-before-action`
- 执行顺序：
  1. 先看 `docs/manual/QUICK-START.md` 的首次上手路径。
  2. 再看 `docs/manual/INSTALLATION.md` 的安装路径分工。
  3. 只在必要时再看 `docs/manual/TROUBLESHOOTING.md`。
  4. 一旦主 edit point 清楚，就停止继续扩展并进入计划阶段。
- 结束信号：
  - 已经能说清楚主 edit point 属于哪一章
  - 其他章节最多只是对照或交叉引用
  - 下一步已经从“继续找”变成“准备做单点修改”

### 修正 `examples/` 里的 Skill 引用

- 任务场景：`examples/` 中某个场景文档引用了不存在的 skill 名称，或者名字和 `skills/` 目录中的真实名称对不上。
- 推荐 skill 组合：`scoped-tasking` + `read-and-locate` + `bugfix-workflow` + `minimal-change-strategy` + `targeted-validation`
- 执行顺序：
  1. 先把症状说清楚。
  2. 以 `skills/` 目录作为基线，确认真实存在的 skill 名称。
  3. 只修确认错误的引用，不顺手重写整个示例。
  4. 定向复查改后的每个名字都能在 `skills/` 对上。
- 结束信号：
  - 每个改动都有 `skills/` 目录中的真实名称作证据
  - 示例文档的结构和任务意图没有被顺手改写
  - 目标引用已经和仓库里的真实 skill 名称一致

### 整理手册目录页的导航结构

- 任务场景：`docs/manual/README.md` 的入口仍然偏散，想把导航结构整理得更清楚，同时不改变已有章节顺序、不删除现有链接。
- 推荐 skill 组合：`scoped-tasking` + `safe-refactor` + `minimal-change-strategy` + `self-review` + `targeted-validation`
- 执行顺序：
  1. 先确认这次目标是整理结构，而不是重写手册内容本身。
  2. 明确不变条件，例如章节文件名、阅读顺序和已有入口不变。
  3. 只在 `docs/manual/README.md` 内做局部收拢。
  4. 自查是否引入了重复说明、遗漏链接或改变了原有阅读逻辑。
- 结束信号：
  - 导航结构更清楚了，但章节内容和阅读顺序没有被改写
  - 所有既有入口仍然有效，没有丢链接
  - 改动仍然局限在导航层

### 一条线补阅读路径图，一条线补工作流案例

- 任务场景：你想同时增强手册的“怎么读”和“怎么用”两部分内容，一条线处理 `docs/manual/README.md`，一条线处理 `docs/manual/COMMON-WORKFLOWS.md`。
- 推荐 skill 组合：`plan-before-action` + `multi-agent-protocol` + `targeted-validation`
- 执行顺序：
  1. 先判断这两项工作是否低耦合。
  2. 把工作拆成两条独立子线，避免交叉编辑。
  3. 每条子线独立完成自己的文档增强。
  4. 集成时统一检查术语、章节顺序和入口逻辑。
- 结束信号：
  - 两条子线的结果能直接汇总
  - 术语、章节顺序和入口逻辑保持一致
  - 集成后没有引入重叠编辑
