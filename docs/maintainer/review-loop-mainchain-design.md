# Review-Loop 主链 5 件套设计文档

## 1. 目标

为开发工程师在一次完整交付中需要的「评审-修复-再评审」场景，提供一组**结构对齐、边界清晰、独立可触发**的 Cursor Agent Skill。本文档把这组 skill 统称为「主链 5 件套」，主链即 SDLC 主要产物链条上、由 review-loop 类型 skill 串起来的标准评审通路。

主链覆盖 SDLC 五个关键产物：

```
需求文档  →  设计文档  →  实施计划  →  代码实现  →  测试用例
   ↓           ↓            ↓            ↓            ↓
requirements  design       plan         code         test
-review-loop  -review-loop -review-loop -review-loop -review-loop
```

每个 skill 都是 review → fix → revalidate → re-review 的循环，直到 `review_result: clean`。

### 1.1 Non-Goals（明确不做的事）

- **不**覆盖 API 契约 / 数据迁移 / 安全 / 依赖 / 发布准备度 / 事故复盘等高风险或周边场景（见 §12 的 Tier 2/3 候选）
- **不**做视觉 / UI / 可访问性 / 性能 review（agent 能力受限）
- **不**抽共享底座 skill（如 `review-loop-core`）；不做参数化合体 skill
- **不**自动串联 5 件套；编排由 AGENTS.md 的 chain 规则负责

### 1.2 成功指标（量化）

- 5 件套统一骨架达成度：100%（章节顺序、issue 分级、Output Format 字段完全一致）
- 触发命中率：对一组典型 prompt（每件套 ≥ 10 条），命中正确 skill 的准确率 ≥ 90%（与当前触发优化基线 89% 持平或更高；基线出处见 `docs/maintainer/README-trigger-optimization.md`）
- 跨 skill 误触发率 ≤ 5%（用户说"评审 X"时，触发到非 X 的 review skill 的概率）
- 每个 skill 对一组样本产物（每件套 ≥ 3 份）能稳定识别 ≥ 3 类典型问题

## 2. 设计原则

1. **形状对齐，内容差异化**：5 个 skill 共享统一骨架（章节顺序、issue 分级、输出模板、loop 协议），差异只体现在"审核维度"和"validation 手段"。
2. **单一职责**：每个 skill 只审一种产物，相邻 skill 通过反向边界声明避免触发冲突。
3. **触发优先于复用**：Cursor skill 不能互相引用，宁可少量文本重复也要让每个 SKILL.md 自包含、可独立命中。
4. **不引入第六个抽象层**：不抽 `review-loop-core` 共享文件，不做"参数化大 skill"。
5. **可执行性优先**：每个 skill 的判定维度都要落到可观测、可验证、可闭环。
6. **最小变更**：现有 `plan-review-loop` 与 `implementation-review-loop` 只做必要调整，不重写主体逻辑。

## 3. 主链定位与边界

### 3.1 五件套的语义层次

| 阶段 | Skill | 审核对象 | 核心问题 |
|---|---|---|---|
| 需求 | `requirements-review-loop` | 需求文档 / PRD / 用户故事 / 问题陈述 | 要做什么？做对了吗？能验收吗？ |
| 设计 | `design-review-loop` | 架构设计 / RFC / ADR / 接口设计 | 怎么做？方案合理吗？取舍清楚吗？ |
| 计划 | `plan-review-loop` | 实施计划 / 迁移计划 / 重构计划 | 按什么顺序做？可执行吗？ |
| 实现 | `code-review-loop` | working tree diff / commit / PR | 写得对吗？有回归吗？ |
| 测试 | `test-review-loop` | 测试用例 / 测试策略 / 覆盖矩阵 | 测得够吗？测得对吗？ |

### 3.2 与现有相邻 skill 的边界

**相邻流程类 skill**（与主链同层，需明确边界）：

| 已有 skill | 与本主链的关系 | 处理方式 |
|---|---|---|
| `self-review` | 是 agent 自己对刚生成的 diff 做一次性检查；不带循环 | 保留，作为 `code-review-loop` 的轻量前置 |
| `bugfix-workflow` | 是 bug 全流程，不只是 review | **本次保留不动**；未来如需在其内部显式引用 `code-review-loop`，作为独立任务处理（不在主链落地范围内） |

**支持型 skill**（被主链各 skill 引用，不构成相邻关系）：

| 已有 skill | 与本主链的关系 | 处理方式 |
|---|---|---|
| `targeted-validation` | 是验证选择策略 | 建议各 SKILL.md 在 `Validation` 段显式引用其作为方法论参考（落地工作见 §10.1） |

主链 5 件套与上述 skill **不冲突、不重叠、不替代**。

## 4. 统一骨架（5 件套共享）

### 4.1 文件结构（章节顺序固定）

```markdown
---
name: <skill-name>
description: "WHAT: ... WHEN: ..."
---
# <skill-name>
## Goal
## Required loop
## Optional checks            # 可选章节；承载该 skill 独有的可选维度（如 §5.4 PR 级检查）
## Issue rules
  ### blocking
  ### warning
  ### low-risk
## Scope protection
## Validation
## Clean result rule
## Output format
## Constraints
```

`Optional checks` 是骨架中**唯一允许的可选章节**；除此之外章节顺序固定不变。无可选维度的 skill 可直接省略该章节。

### 4.2 统一的 Issue 分级语义

| 级别 | 通用语义 | 处理要求 |
|---|---|---|
| `blocking` | 不修就一定出错 / 失败 / 偏离意图 | 必须修复 |
| `warning` | 大概率返工或后续踩坑 | 必须修复或显式接受+缓解 |
| `low-risk` | 真实但小的不确定性 | **必须闭环**：修复 / 加验证步骤 / 显式接受假设并写出验证方法 |

`low-risk` 不允许"仅报告不处理"，这是与传统一次性 review 的关键差异。

### 4.3 统一的 Output Format

```markdown
## Review Result
review_result: clean | issues_found

## Issues
blocking:
- None
warning:
- None
low-risk:
- None

## Changes Made
- file: ""
  summary: ""

## Validation
- ""

## Residual Assumptions
- assumption: ""
  validation_method: ""
```

字段语义不变，只是各 skill 填充内容不同。

### 4.4 Required loop 的内部协议（伪代码）

对应 §4.1 中 `Required loop` 章节的执行流程：

```
1. 识别目标产物（用户指定 / 当前工作区默认）
2. 加载相关仓库上下文（按 skill 类型选取）
3. 按本 skill 的维度清单做 findings-first review
4. 把每个发现归类 blocking / warning / low-risk
5. 在 Scope protection 约束下应用修复（或修订）
6. 跑该 skill 定义的最小 validation
7. 重读修订后的产物
8. 重新 review
9. 直到所有三个等级都为空，才返回 clean
```

### 4.5 统一的反向边界声明

每个 skill 在 `Constraints` 末尾必须有一行：

```
- Do not use for <相邻产物>; use <相邻 skill name> instead.
```

例：`design-review-loop` 写

```
- Do not use to review requirements; use requirements-review-loop.
- Do not use to review implementation plans; use plan-review-loop.
```

## 5. 各 Skill 差异化设计

### 5.1 `requirements-review-loop`（新建）

**审核对象**：需求文档、PRD、用户故事、问题陈述、AC（验收标准）草案。

**核心维度**：

| 维度 | 检查点 |
|---|---|
| 清晰性 | 每条需求能识别明确的 action + target object |
| 完整性 | inputs / outputs / 边界 / 失败场景 / 非功能约束齐全 |
| 可验证性 | 每条需求有可观测的验收标准 |
| 一致性 | 内部不冲突；术语与项目已有词表一致 |
| 范围合理 | 不过宽 / 不过窄；隐含假设显式化 |
| 可行性 | 与代码/产品现状无明显冲突（有 repo 时对照） |
| 依赖与优先级 | 前置依赖、必要 vs 可选清晰 |

**Validation 手段**：不跑代码。
- 对照仓库现状 / 现有 schema / 现有 API 反查一致性
- 用「术语对照表」检验词汇统一性
- 对每条需求尝试写一句"如何验证它满足了"，写不出即降级

**Scope protection**：只改需求文档本身，不动设计、不动计划、不动代码。

---

### 5.2 `design-review-loop`（新建）

**审核对象**：架构设计文档、RFC、ADR、接口设计、数据模型设计、技术方案。

**核心维度**：

| 维度 | 检查点 |
|---|---|
| 意图对齐 | 设计能完整支持上游需求 |
| 方案合理 | 给出 2+ 备选并说明取舍；首选有清晰理由 |
| 约束尊重 | 性能 / 安全 / 兼容性 / 部署约束被识别并应对 |
| 接口契约 | 公共 API / Schema / 事件契约定义清晰、可演化 |
| 失败设计 | 错误路径、降级、回滚、监控方案明确 |
| 复杂度合理 | 不过度设计；YAGNI 检查 |
| 影响面 | 跨模块/团队的影响显式标注，需协调点列出 |

**Validation 手段**：不跑代码。
- 对照需求文档检查是否全覆盖
- 对照现有架构图 / 接口定义检查冲突
- 关键设计点反问"如果不这样做，会怎样"

**Scope protection**：只改设计文档；不写实现代码、不写 plan。

---

### 5.3 `plan-review-loop`（改造）

**审核对象**：实施计划 / 迁移计划 / 重构计划 / 任务计划。

**核心维度**（基本保留现有定义，强调可执行性）：

| 维度 | 检查点 |
|---|---|
| 上游一致 | 与已批准的设计/需求对齐 |
| 顺序合理 | 步骤依赖正确；可回滚 |
| 范围控制 | 不偷塞未授权变更 |
| 文件级落点 | 每步指出涉及的具体路径/模块 |
| 验证步骤 | 每步附带可验证标准 |
| 风险预案 | 关键风险有缓解 |
| 与仓库现状一致 | 引用的文件/接口/约定真实存在 |

**Validation 手段**：不跑代码。
- 对照实际仓库结构 / 配置 / 测试 / 文档
- 对每步反查"实际执行会卡在哪"

**Scope protection**：只改计划文档本身。

**改造动作**（仅列本文件独有动作；共性落地工作见 §10.1）：

- 无独有动作；当前文件缺 `Scope protection` 章节，按 §10.1 共性"章节顺序严格按 §4.1 骨架"补齐即可。

---

### 5.4 `code-review-loop`（由 `implementation-review-loop` 改名+改造）

**审核对象**：working tree diff / staged diff / 指定 commit / commit range / 用户指定文件 / PR diff。

**核心维度**（保留现有；PR 级关注点下移至「可选维度」）：

| 维度 | 检查点 |
|---|---|
| 正确性 | 行为正确、边界处理完整、错误处理充分 |
| 回归 | 不破坏既有行为；测试覆盖关键路径 |
| 安全 | 注入/权限/敏感数据/密钥 |
| 数据兼容 | schema/序列化/迁移兼容性 |
| Scope 控制 | 不夹带无关变更 |
| 测试 | 新增逻辑有对应测试；既有测试未被绕过 |

**可选维度（落地在 SKILL.md 的 `Optional checks` 章节，见 §4.1）**：

| 维度 | 检查点 |
|---|---|
| PR 级 | PR 描述清晰、关联 issue 追溯、CI 通过、可合并准备度、commit message 规范 |

**Validation 手段**：跑代码。
- 优先 targeted unit / integration test
- typecheck / lint touched files
- 必要时 build；不必要时不跑
- 完全无法跑则显式说明并给最近替代

**Scope protection**：
- 修复前 inspect repository status
- 区分用户既有改动与本次任务改动
- 不修复无关文件、不重排无关代码

**改造动作**（仅列本文件独有动作；共性落地工作见 §10.1）：

1. 目录改名：`implementation-review-loop/` → `code-review-loop/`
2. SKILL.md frontmatter `name:` 改为 `code-review-loop`
3. 新增 `Optional checks` 章节承载本节「可选维度」表的 PR 级维度（这是当前 5 件套中唯一带可选维度的 skill）

---

### 5.5 `test-review-loop`（新建）

**审核对象**：测试用例代码、测试策略文档、覆盖矩阵、新增/修改的测试文件。

**核心维度**：

| 维度 | 检查点 |
|---|---|
| 场景覆盖 | 覆盖按行为场景而非行覆盖率；正常/边界/失败/异常齐全 |
| 断言质量 | 每个测试有明确断言；不只是"不抛异常" |
| 隔离性 | 测试间无隐式依赖；可单独运行 |
| 确定性 | 无 flaky 因素（时间、并发、外部依赖、随机性） |
| 可读性 | 测试名表达意图；arrange/act/assert 清晰 |
| 维护成本 | 不过度 mock；不重复脚手架 |
| 与被测代码对齐 | 测试反映当前接口契约，不测过时行为 |

**Validation 手段**：跑测试。
- 执行新增/修改的测试，确认通过
- 故意破坏被测代码，确认测试能捕获（关键测试做一次"mutation 心智演练"）
- 检查测试在隔离运行（单文件）下也通过

**Scope protection**：只改测试相关文件；不动被测产品代码。

## 6. 命名约定

### 6.1 主链 5 件套最终命名

```
requirements-review-loop
design-review-loop
plan-review-loop
code-review-loop
test-review-loop
```

### 6.2 命名规则

- **kebab-case**，与仓库现有 skill 统一
- **前缀** = 产物名（`requirements` / `design` / `plan` / `code` / `test`）
- **中段** = `-review-`
- `requirements` 用复数（一份需求文档包含多条需求，符合英文习惯）；其余为单数（一份设计/一份计划/一段代码/一组测试在产物语义上不强制复数）
- **元规则（未来新增 review skill 适用）**：默认按"产物名在英文语义下的可数性"决定单复数；若该产物天然以"一组多条"形式存在（如 requirements / dependencies），用复数；否则用单数

### 6.3 改名影响评估

经 grep 检查，`implementation-review-loop` 和 `plan-review-loop` 当前**没有任何外部引用**，改名仅需：
1. `git mv skills/implementation-review-loop skills/code-review-loop`
2. 修改新目录下 `SKILL.md` frontmatter 的 `name:` 字段

无下游 skill / 文档 / 脚本依赖需要同步。

## 7. 路由策略

为防止 5 个 skill 触发冲突，采用三层防御：

### 7.1 description 精准化

每个 skill 的 description 遵循 `WHAT: ... WHEN: ...` 模板，且 `WHEN` 必须明确产物类型关键词。

例：
- `requirements-review-loop` 的 WHEN 关键词：requirement / PRD / user story / acceptance criteria
- `design-review-loop` 的 WHEN 关键词：design doc / RFC / ADR / architecture / interface design
- `plan-review-loop` 的 WHEN 关键词：implementation plan / migration plan / task plan
- `code-review-loop` 的 WHEN 关键词：diff / commit / PR / implementation
- `test-review-loop` 的 WHEN 关键词：test cases / test strategy / coverage

### 7.2 反向边界声明（强制）

每个 skill 在 Constraints 必须显式声明"不用于"相邻产物，引导 LLM 重选。

### 7.3 路由备忘表（写进本设计文档作为维护参考）

| 用户说法关键词 | 应触发 |
|---|---|
| 需求 / requirement / PRD / 用户故事 / 验收标准 | requirements-review-loop |
| 设计 / design / RFC / ADR / 架构 / 接口设计 / 技术方案 | design-review-loop |
| 计划 / plan / 迁移方案 / 实施步骤 / roadmap | plan-review-loop |
| 代码 / code / diff / commit / PR / 实现 | code-review-loop |
| 测试 / test / 用例 / 覆盖 / coverage | test-review-loop |

### 7.4 易混淆词与归属（对抗性消歧）

中文语境下以下词容易跨 skill 触发，统一归属如下。各 skill 的 description 应在 WHEN 段落显式排除非归属用法。

| 易混淆词 | 归属 | 排除其它 |
|---|---|---|
| 方案 | 默认 `design-review-loop`；若明确"实施方案/迁移方案"则归 `plan-review-loop` | 不归 code / requirements |
| 实现思路 / 实现方案 | `design-review-loop` | 不归 code（code 审已存在的实现代码） |
| 接口 / API | `design-review-loop`（设计阶段）；已实现的接口代码归 `code-review-loop` | 用"设计""定义"等动词触发设计；用"diff""commit"等触发 code |
| 评审 / review（无宾语） | 不命中任何主链 skill；要求用户补充对象 | 触发澄清而非默选 |
| 文档 | 按文档类型再分流；无类型则要求补充 | 不允许默选 |
| 评估 / 评测 | 不归 review-loop；可能是 impact-analysis / targeted-validation | 不命中主链 |
| 思路 / 想法 | 归 `design-review-loop` | 不归 plan / code |

## 8. 与现有 skill 的协作

### 8.1 链路示例

```
新功能完整流程：
  scoped-tasking → design-before-plan → requirements-review-loop
  → design-review-loop → plan-before-action → plan-review-loop
  → [编码] → self-review → code-review-loop → test-review-loop
```

**前置条件**：示例链路任意节点缺少上游产物时（如直接修 bug 没有 design），按 §9 降级策略跳过对应 review-loop，并在最终输出的 `Residual Assumptions` 中显式记录被跳过的环节与原因。

### 8.2 主链与 phase 系列的关系

- 单 PR / 单文档场景用 `plan-review-loop`
- 两者在 description 互相声明边界

### 8.3 主链与 bugfix-workflow 的关系

- `bugfix-workflow` 覆盖"诊断 → 定位 → 修复 → 验证"全过程
- 两者职责不重叠
- 本次主链落地**不修改** `bugfix-workflow`；未来如要在其内部显式引用 `code-review-loop` 作为修复后闭环，作为独立任务处理（与 §1.1 Non-Goals 第 5 条对齐）

## 9. 失败与降级

每个 skill 必须支持以下降级：

| 场景 | 降级策略 |
|---|---|
| 上游产物缺失（如审 plan 时没有 design） | 显式标注"在缺少 X 的前提下"，缩小 review 范围 |
| Validation 无法执行（如沙箱无 DB） | 写明原因 + 最接近的替代检查 |
| 单轮 review 后 issue 数量爆炸 | 触发 `scoped-tasking` 缩小目标 |

降级不允许默默升级为 `clean`，必须在 `Residual Assumptions` 列出。

**降级报告统一要求**：所有降级（缺产物、validation 不可用、上下文压缩、目标缩窄）都在 Output Format 的 `Residual Assumptions` 字段以 `assumption + validation_method` 形式显式记录；不允许在 `Issues` 三档之外另立"已知问题"等隐式分类。

## 10. 实施计划

### 10.1 改动清单

| 文件 | 动作 | 估算行数 |
|---|---|---|
| `skills/requirements-review-loop/SKILL.md` | 新建 | ~110 |
| `skills/design-review-loop/SKILL.md` | 新建 | ~110 |
| `skills/test-review-loop/SKILL.md` | 新建 | ~110 |
| `skills/plan-review-loop/SKILL.md` | 改造 | +15 行 |
| `skills/code-review-loop/SKILL.md` | 改名+改造 | +20 行 |
| `skills/implementation-review-loop/` | 删除（已 mv） | - |

**所有 5 个 SKILL.md 的共性落地工作**（每个文件内含，不另列文件）：

- 章节顺序严格按 §4.1 骨架
- `Optional checks` 章节按需添加（无可选维度的 skill 直接省略；当前仅 `code-review-loop` §5.4 需要）
- `Validation` 段显式引用 `targeted-validation` 作为方法论参考
- `Constraints` 段含 §4.5 反向边界声明
- description 含 §7.1 关键词与 §7.4 易混淆词排除提示

### 10.2 增量交付（建议分 3 个 PR）

| PR | 内容 | 验收 |
|---|---|---|
| PR 1 | `code-review-loop` 改名 + 5 件套统一骨架调整（`plan-review-loop` 改造、`code-review-loop` 改造） | 仓库全局 grep 无 `implementation-review-loop` 残留；两个 skill 含 §4.5 反向边界声明（在 Constraints） |
| PR 2 | 新建 `requirements-review-loop` 与 `design-review-loop` | 触发测试：三段典型 prompt 命中正确 skill |
| PR 3 | 新建 `test-review-loop`；更新维护文档/索引 | 触发测试覆盖全部 5 件套 |

**PR 间依赖**：PR 1 必须先合并（确立统一骨架基线 + 命名修正）；PR 2 与 PR 3 在 PR 1 合并后可并行或串行，二者之间无强依赖。

### 10.3 验收标准

**交付形式（必须）**：

- 5 个 SKILL.md 章节顺序完全一致
- 5 个 Output Format 字段完全一致
- 触发测试：用户用"评审需求/评审设计/评审计划/评审代码/评审测试"5 种说法分别命中对应 skill

**质量门槛（必须，与 §1.2 成功指标对齐）**：

- 触发命中率 ≥ 90%（每件套 ≥ 10 条样本 prompt 的回归测试）
- 跨 skill 误触发率 ≤ 5%
- 对一组样本产物（每件套 ≥ 3 份），每个 skill 至少稳定识别出 3 类典型问题（参考各 skill §5.x 的「核心维度表」中至少 3 类）
- §7.4 易混淆词每条至少 1 条 prompt 验证归属正确

## 11. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 5 个 skill description 关键词碰撞导致误触发 | 中 | 反向边界声明 + 触发测试覆盖 |
| 文本重复带来维护漂移 | 中 | 本设计文档作为对齐参考；评审 SKILL.md 改动时对照统一骨架 |
| 用户期望 5 件套自动串联 | 低 | 文档明确"独立触发"，由 AGENTS.md 的 chain 规则负责组合 |
| `requirements` 复数与兄弟单数不齐导致视觉违和 | 低 | 在本文件 §6.2 解释原因；可接受 |
| 新增 3 个 skill 拖累 trigger 准确率 | 中 | 分 PR 增量，每次新增后跑触发回归测试 |
| 修订本文档或落地 SKILL.md 时未做波及面扫描，引入自相矛盾 | 中 | 每轮修订后强制三步：① grep 关联术语；② 跨章节交叉读相关条目；③ 扫所有同名概念。该 checklist 固化在 §13 后续动作中执行 |
| Skill 改名时 `.cursor/skills/` 与 `.claude/skills/` 本地缓存反向同步，导致旧目录反复"复活"、新目录反复"消失" | 高 | 任何 skill 改名/删除操作，必须同步清理 `.cursor/skills/<old-name>/` 与 `.claude/skills/<old-name>/`；在 git add 后用 `git status` 与 `ls .cursor/skills/` 双重确认；该步骤固化在 §13 后续动作中 |

## 12. 未列入主链的 review 场景

以下 review 场景**有意不进入主链**，避免 skill 膨胀：

- API 契约 review（Tier 2 候选，按需补 `api-contract-review-loop`）
- 数据迁移 review（Tier 2 候选）
- 安全 review（Tier 2 候选）
- 依赖变更 / 发布准备度 / 事故复盘 / 运维文档（Tier 3，按需）
- PR 描述 / commit message：作为 `Optional checks` 章节并入 `code-review-loop`（见 §5.4 可选维度表「PR 级」一行），不另开 skill
- 分支命名：写成 rule，不进入 skill 体系
- 性能 / UI / 可访问性 review（agent 能力受限，不做独立 skill）

补充策略：主链稳定运行 1–2 个迭代后，再根据团队真实痛点从 Tier 2 中选 1 个补齐，不预先建。

## 13. 后续动作

1. **评审通过的判定**：本设计文档跑 review-loop（按 requirements-review-loop 方法论自审）输出 `review_result: clean` 且用户在对话中确认 → 视为通过；进入落地阶段
2. 按 §10.2 的 PR 拆分依次落地
3. 每个 PR 落地后，运行触发测试集（如有），并在 `docs/maintainer/trigger-test-optimization-tracker.md` 记录主链相关测试结果
4. 主链稳定后，在 `AGENTS.md` 的 Skill Chain Triggers 表中增补主链 5 件套的标准链路示例
5. **修订执行规范（强制，缓解 §11 风险表"波及面"风险）**：本文档任意修订后必须按以下三步自查：
   - ① 对被改动的关键术语在全文做 grep
   - ② 跨章节交叉读所有命中条目，确认语义一致
   - ③ 修订记录写入 PR 描述或对话中
6. **Skill 改名清理规范（强制，缓解 §11 风险表"本地缓存反向同步"风险）**：任何 skill 改名或删除操作，落地步骤必须包含：
   - ① `rm -rf .cursor/skills/<old-name>/`
   - ② `rm -rf .claude/skills/<old-name>/`
   - ③ `git add -f <new-paths>` 把新文件锁定到 git index，防止 IDE watcher 反向回滚
   - ④ `ls .cursor/skills/ .claude/skills/` 双重确认无残留
