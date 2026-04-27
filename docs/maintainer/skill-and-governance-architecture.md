# Skill And Governance Architecture

## Purpose

这篇文档面向开发和维护 `agent-skills` 仓库本身的人。  
它不回答“最终使用者该怎么装、怎么选、怎么排错”，而是回答“这套系统内部为什么要分成 skill 与 governance 两层，以及维护时该把什么内容写到哪里”。

## Audience

适合以下读者：

- 在维护 `skills/` 目录中的 skill 定义
- 在维护 `templates/governance/` 中的治理模板
- 在维护 `manage-governance.py` 的安装与注入逻辑
- 在判断一段说明应该写进 `docs/manual/` 还是 `docs/maintainer/`

## System Split

这套系统内部可以分成两层：

### Skill Layer

这一层由各个 skill 的 `SKILL.md` 构成。  
它的职责是定义单个行为模块本身，例如：

- 什么时候适用
- 怎么执行
- 输入输出是什么
- 什么时候停止
- 与其他 skill 的组合关系

维护时，下面这些内容属于 skill 层：

- skill 的具体工作步骤
- skill 的边界和反例
- skill 自己的输入输出约束
- skill 自己的验证与停用条件

### Governance Layer

这一层由 `AGENTS-template.md`、`CLAUDE-template.md` 及其注入结果构成。  
它的职责不是重复 skill 内容，而是把 skill 组织成一套项目级路由规则，例如：

- 哪些 skill 什么时候该启用
- 哪些 skill 之间怎样交接
- 哪些 skill 不能同时保持活跃
- 什么情况下该升级、降级或退出

维护时，下面这些内容属于 governance 层：

- 触发规则
- 交接顺序
- 生命周期管理
- 并行或升级协议
- 模板 section 的组织和注入顺序

## Governance Template Content

这一节回答的是维护者最常问的一类问题：  
治理模板里到底应该放什么、不该放什么、当前这些 section 分别在承担什么职责。

### Templates Are Source Files, Not Generated Results

`templates/governance/AGENTS-template.md` 和 `templates/governance/CLAUDE-template.md` 是治理模板源文件。  
目标项目里的 `AGENTS.md` 或 `CLAUDE.md` 是安装器把这些模板落地后的结果，不应该反过来被当成模板源继续维护。

维护时要区分三层：

- `skills/*/SKILL.md`：单个技能自己的完整说明
- `templates/governance/*.md`：平台级治理模板
- 目标项目里的 `AGENTS.md` / `CLAUDE.md`：模板注入结果

### What Belongs In The Templates

治理模板应该承载的是“项目级路由与约束”，而不是技能正文。

当前模板里真正应该存在的内容类型包括：

- 多代理规则与并行预算
- skill activation / escalation / lifecycle 这类触发与退场规则
- governance fast-path 的快速分流规则
- skill protocol block 的格式与顺序
- skill family concurrency budget
- skill chain triggers、handoffs、fallbacks

这些内容的共同点是：它们决定“项目里如何组织和调度技能”，而不是解释“某个技能内部怎么执行”。

### What Must Stay Out Of The Templates

下面这些内容不应该继续堆进治理模板：

- 某个技能的完整执行步骤
- 技能专属的详细例子、边界案例、反例目录
- 只对某个 skill 成立的输出 schema
- 面向最终使用者的安装说明、工作流、排错文案
- 安装器内部实现细节和代码路径说明

如果把这些内容塞进模板，会出现三个直接后果：

- 和 `SKILL.md` 重复维护
- 模板体积继续膨胀
- 用户文档、维护文档、治理模板三层边界重新混在一起

### How To Read The Current Template Sections

以当前 `AGENTS-template.md` / `CLAUDE-template.md` 为例，可以把主要 section 理解成下面几层：

- 顶层路由约束：`Multi-Agent Rules`
- 技能进入与升级：`Skill Activation` / `Skill Escalation`
- 责任边界：`Skill Boundary`
- 治理层快速分流：`Governance Fast-Path`
- 运行中生命周期管理：`Skill Lifecycle`
- 通用执行协议：`Skill Protocol v2`
- 并发预算控制：`Skill Family Concurrency Budgets`
- 常见交接链路：`Skill Chain Triggers`

换句话说，模板的核心不是“罗列技能内容”，而是提供一套让多个技能能稳定协同的路由框架。

如果按维护视角来读，这几层其实对应一条从“要不要加载 skill”到“加载后如何协同”的判断路径：

1. 先看能不能走 governance fast-path，避免无意义加载
2. 如果不能 fast-path，再看哪些 skill 应该进入
3. 进入后，再看生命周期、协议块和并发预算如何约束执行
4. 最后用 chain triggers 约束常见 handoff 和 fallback

下面按 section 逐个展开。

#### `Multi-Agent Rules`

这部分是并行协作的总入口，负责定义：

- 什么情况下允许并行
- 并行前必须输出什么声明
- 什么时候需要因为并发规模过大而升级到 `phase-plan`
- 哪些任务根本不需要走并行治理

它解决的是“并行能不能开、开到什么程度、超过上限怎么办”。

维护时，这里应该只保留并行协作的硬约束和入口规则，不应该塞入：

- 某个具体 skill 的内部并行步骤
- 某类任务的完整执行剧本
- 需要依赖具体仓库上下文才能成立的特例

#### `Skill Activation`

这部分定义技能如何进入运行态，重点回答：

- 哪些技能可以在基础触发判断中直接进入
- 哪些情况需要先走 governance 层判断，再决定是否加载完整 skill

它解决的是“技能从哪里开始进入系统”。

维护时，这里适合放：

- task-type activation 的总规则
- mid-task escalation 的入口说明

不适合放：

- 某个 skill 的完整适用条件展开版
- 大量技能级例子和边界案例

那些内容应该留在对应 `SKILL.md`。

#### `Skill Boundary`

这部分是整个模板里最关键的“职责分界线”，它负责反复强调：

- governance 文件不是 skill manual
- 哪些内容必须留在模板里
- 哪些内容必须回到 `SKILL.md`

它解决的是“为什么模板不能越写越像技能百科”。

维护时，如果你在判断一段新内容该写到哪里，先回到这一节。  
很多模板膨胀问题，本质上都不是规则不够，而是 boundary 失守。

#### `Governance Fast-Path`

这部分定义“根本不需要加载 skill 的情况”，例如：

- 直接回答
- 单个命令
- 已知路径的小范围只读操作
- 单文件低风险修改

它解决的是“什么时候 governance 层本身就够了”。

这一节非常重要，因为如果没有 fast-path，系统会把很多本该直接完成的小任务也强行送进完整 skill 流程，导致：

- 输出变重
- 执行成本上升
- 使用体验变僵

维护时，这里只应该保留表层可判断的快速分流规则，不要把它扩写成细粒度技能判断树。

#### `Skill Escalation`

这部分定义的是：当 governance 层不够时，应该升级到哪个完整 skill。

它解决的是“什么时候基础治理已经不足，必须把判断权交给更完整的 skill 文件”。

例如：

- 设计决策还没收敛时，升级到 `design-before-plan`
- 影响面扩大时，升级到 `impact-analysis`
- 多文件编辑完成后，升级到 `self-review`

维护时，这一节要写的是“升级信号”，不是“升级后的完整执行方式”。  
一旦开始解释 skill 的详细步骤，就说明内容已经越过模板边界了。

#### `Skill Lifecycle`

这部分定义技能进入后什么时候该继续保留、什么时候应该 drop。

它解决的是“技能不是一旦加载就一直挂着”的问题。  
如果没有 lifecycle 规则，系统很容易出现：

- 技能越挂越多
- 旧 skill 没退出，新 skill 又继续叠加
- 后续输出混入已经失效的约束

维护时，这里重点写：

- load 原则
- drop 条件
- keep active 的例外
- active skill 数量上限

不要把它写成技能执行清单；它关注的是运行态管理，不是任务正文。

#### `Skill Protocol v2`

这部分定义的是 skill-driven execution 的统一协议块格式。

它解决的是“多个 skill 输出如何保持统一结构、可验证、可交接”。

这一节承担的是“公共语法层”的职责，包括：

- `[task-validation]`
- `[triggers]`
- `[precheck]`
- `[output]`
- `[validate]`
- `[drop]`
- `[loop]`

维护时，这里只应该放：

- block 的顺序
- block 的语义
- 语法格式和状态符号

不应该放：

- 某个具体 skill 的个性化输出示例堆叠
- 与单个仓库绑定的业务约束

#### `Skill Family Concurrency Budgets`

这部分不是讲“要不要并行”，而是讲“已经加载的技能可以同时活跃到什么程度”。

它解决的是执行过程中 active skills 无限制增长的问题。  
和 `Multi-Agent Rules` 的区别在于：

- `Multi-Agent Rules` 约束的是代理并行
- `Skill Family Concurrency Budgets` 约束的是技能并发与 family 级预算

维护时要特别注意 family 维度，而不是简单追求一个全局数字。  
否则很容易把执行技能、编排技能、phase 技能混成同一类预算。

#### `Skill Chain Triggers`

这部分记录的是最常见、最值得标准化的 handoff 与 fallback 路径。

它解决的是“技能之间应该怎样交接，哪些回退路径是被明确允许的”。

维护时可以把它理解成一张 canonical routing map：

- forward handoffs 负责说明正常推进路径
- fallbacks 负责说明失败或不确定时如何回退

这里不需要覆盖所有理论上可能存在的组合。  
只有那些高频、稳定、值得跨任务复用的链路，才应该进入模板。

### Why There Are Two Templates

当前有 `AGENTS-template.md` 和 `CLAUDE-template.md` 两份模板，但它们的主体内容保持镜像一致，只在头部文件名和目标平台语境上有差异。

维护时要把它们当成：

- 同一套治理内容的两个平台外壳
- 需要保持同步的镜像模板

这也是模板文件开头会明确写出 mirror 提示的原因。  
如果后续某一边单独演化，就必须先确认这是不是平台差异，还是只是同步失误。

### Maintenance Rules For Template Changes

改治理模板时，建议按下面顺序判断：

1. 这次改动是在改路由规则，还是在补技能正文
2. 如果是在补技能正文，应回到对应 `SKILL.md`
3. 如果是在改路由规则，再判断它属于哪个 template section
4. 改完后同时检查另一份镜像模板是否需要同步
5. 再检查安装结果、用户手册和 maintainer 文档有没有受影响

最容易犯的错不是“不会写模板”，而是把本该写进 skill、手册或安装器说明里的内容误塞到模板里。

### Documentation Split For Template Explanations

关于模板的说明，建议始终按下面边界分层：

- `docs/manual/`：只解释最终使用者为什么会看到 `AGENTS.md` / `CLAUDE.md`，以及这意味着项目已经接入治理规则
- `docs/maintainer/`：解释模板 section、模板边界、镜像同步、维护注意事项
- 模板文件本身：保留真正会被注入的治理规则，不承担教程职责

这样可以避免两种常见退化：

- 用户手册被写成模板维护指南
- 模板文件被写成技能百科或仓库文档目录

## 文档归属边界

开发时最容易混淆的不是代码，而是文档归属。

### 哪些内容放到 `docs/manual/`

以下内容应该放在 `docs/manual/`：

- 最终使用者如何理解 `skill` 和 `governance`
- 只装技能与装治理规则的使用差异
- `AGENTS.md` 为什么不是技能正文
- 从使用角度看，治理规则会带来什么体验变化
- 安装、选型、工作流、排错

换句话说，这里回答的是：

- 这是什么
- 我为什么会遇到它
- 我该怎么用
- 对我有什么影响

### 哪些内容放到 `docs/maintainer/`

以下内容应该放在 `docs/maintainer/`：

- governance 模板怎样拆 section
- section 注入顺序怎样维护
- `manage-governance.py` 的模式与内部边界
- `--project`、`--global`、`--sync-local` 的实现区别
- local mirror 如何校验漂移
- 改动 skill 或模板后该怎么验证

换句话说，这里回答的是：

- 这套系统内部怎么组织
- 维护时应该改哪一层
- 哪些机制会影响安装器、模板和验证流程

## Practical Writing Rule

如果你在写文档时拿不准归属，可以先问自己一个问题：

这段内容是在回答“使用者该怎么理解和使用”，还是在回答“维护者该怎么修改和维护”？

如果是在回答：

- “最终使用者会遇到什么” -> 放 `docs/manual/`
- “仓库维护者要改什么、验证什么” -> 放 `docs/maintainer/`

## Common Mistakes

### Mistake 1: 把 skill 步骤抄进 governance 文档

问题：

- 会造成同一规则在多个位置重复维护
- 后续更新时容易改漏

正确做法：

- skill 自己怎么工作，留在对应 `SKILL.md`
- governance 只写触发、交接、退场和约束

### Mistake 2: 把安装器实现细节写进用户手册

问题：

- 最终使用者不需要知道内部注入流程
- 会让用户手册混入过多维护视角

正确做法：

- 用户手册只写使用结果和决策差异
- 脚本内部模式与实现边界留在 maintainer 文档

### Mistake 3: 把 `docs/manual/` 写成仓库开发指南

问题：

- 最终使用者阅读路径会被打断
- 文档边界变得模糊

正确做法：

- `docs/manual/` 只服务使用者
- 仓库开发、镜像、内部验证放到 `docs/maintainer/`

## Recommended Next Docs

如果后续继续补 maintainer 文档，最值得新增或补强的是：

- `manage-governance.py` 模式与边界说明
- governance 模板 section 结构说明
- skill 与 governance 变更后的维护者验证清单
