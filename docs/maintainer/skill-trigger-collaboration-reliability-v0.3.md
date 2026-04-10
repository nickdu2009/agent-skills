# 技能触发与协作优化 - 全技能协议化升级方案

**文档版本**: 0.3.1  
**协议目标版本**: Skill Protocol v1  
**兼容性**: 不兼容升级（breaking change）  
**日期**: 2026-04-10  
**状态**: 建议采纳  
**作者**: 系统架构设计  
**覆盖范围**: `skills/` 下全部 18 个技能（12 execution + 2 orchestration + 4 phase）  
**基于**: v0.2.1 + `industry-best-practices-analysis.md` + 文档评审反馈

---

## 变更摘要

本次不再把 v0.3 定义为“在 v0.2.1 上继续打补丁”，而是明确升级为一套**覆盖全部技能族的统一协议**。

核心变化：

- 从“部分技能增强”升级为“全技能统一协议”
- 从“只描述执行技能”升级为“execution / orchestration / phase 三类技能一起定义”
- 从“自然语言软约束”升级为“协议块 + 生命周期 + 契约 + 评测入口”四件套
- 从“英文启发式”升级为“语言无关的输入/输出判断标准”
- 从“零散验证脚本设想”升级为“统一接入 `maintainer/scripts/evaluation/`”

本方案的目标不是让技能系统变成复杂 runtime，而是让仓库中的技能、模板、示例、评测脚本围绕**一个协议**工作。

---

## 1. 设计决策

### 1.1 为什么选择不兼容升级

继续兼容 v0.2.1 的问题是：旧语义和新语义会长期并存。

具体表现：

- 一部分技能只有 `[skill-output]`，另一部分技能还有契约和失败恢复
- execution 技能有协议，orchestration/phase 技能没有同等约束
- 生命周期规则只对少数技能明确，长会话行为不可预测
- 验证入口可能分裂成“旧 smoke”与“新脚本”两套真相源

因此，本次直接采用 **Skill Protocol v1**，要求所有技能族一起迁移。

### 1.2 为什么这种做法更简单、更安全

这是更简单的方案，因为它只保留一个中心概念：**协议优先**。

也是更安全的方案，因为它把关键问题都变成可检查对象：

- 触发前有输入验证
- 激活前有前置条件检查
- 运行后有结构化输出和输出验证
- 长会话有循环检测和显式卸载
- 全部验证都走现有 `evaluation/` 入口

### 1.3 输入、输出、边界、失败场景

**输入**：

- 用户任务请求
- 当前会话上下文
- 技能定义（`SKILL.md`）
- 模板规则（`templates/governance/*`）
- 评测脚本和示例场景

**输出**：

- 标准化协议块
- 更新后的技能契约与失败处理规范
- 统一的评测结果

**边界条件**：

- 本文档覆盖 `skills/` 中全部 18 个技能
- 本文档定义协议和迁移路径，不直接充当运行时实现
- 平台接入示例是附属内容，不是协议本体

**主要失败场景**：

- 只迁移部分技能，形成新旧混用
- orchestration/phase 技能仍停留在自然语言说明层
- 评测脚本无法识别协议块顺序或缺失字段
- 规则继续依赖英文词数或英文动词判断

---

## 2. 覆盖范围

### 2.1 Execution Skills（12）

| Skill | 主要职责 | 协议重点 | 卸载条件 |
|-------|----------|----------|----------|
| `scoped-tasking` | 缩小任务边界 | `objective`、`analysis_boundary`、`excluded_areas` | 边界已被下游消费 |
| `design-before-plan` | 形成设计简报 | `requirements`、`alternatives`、`chosen_design`、`acceptance_criteria` | 设计简报被计划阶段接收 |
| `minimal-change-strategy` | 约束 diff 范围 | `change_boundary`、`scope_guardrails`、`stop_conditions` | 任务完成或无需继续约束 |
| `plan-before-action` | 输出执行计划 | `assumptions`、`working_set`、`sequence`、`validation_boundary` | 执行开始且无需重规划 |
| `targeted-validation` | 选择最小验证面 | `checks_to_run`、`risks_not_covered`、`pass_criteria` | 验证完成或升级验证 |
| `context-budget-awareness` | 压缩并重聚焦上下文 | `current_state`、`dropped_hypotheses`、`open_questions` | 工作集恢复可控 |
| `read-and-locate` | 定位代码路径和编辑点 | `entry_points`、`candidate_files`、`edit_points` | 编辑点已确认 |
| `safe-refactor` | 做小范围行为不变重构 | `behavior_invariants`、`refactor_boundary`、`rollback_notes` | 重构完成或转入实现 |
| `bugfix-workflow` | 证据驱动修 bug | `symptom`、`repro`、`fault_domain`、`fix_hypothesis` | 根因被确认并移交实现 |
| `impact-analysis` | 评估变更影响面 | `affected_callers`、`contracts`、`compatibility_risks` | 影响已被计划吸收 |
| `self-review` | 自查 diff 风险 | `findings`、`residual_risks`、`scope_violations` | 评审通过或阻塞上抛 |
| `incremental-delivery` | 拆成 2-4 个增量 | `increments`、`merge_order`、`gates` | 增量方案已确定 |

### 2.2 Orchestration Skills（2）

| Skill | 主要职责 | 协议重点 | 卸载条件 |
|-------|----------|----------|----------|
| `multi-agent-protocol` | 协调并行子 Agent | `split_dimension`、`lanes`、`integration_plan`、`synthesis` | 合并结论完成 |
| `conflict-resolution` | 仲裁冲突结论 | `claims`、`evidence`、`resolution`、`residual_uncertainty` | 决议被主流程吸收 |

### 2.3 Phase Skills（4）

| Skill | 主要职责 | 协议重点 | 卸载条件 |
|-------|----------|----------|----------|
| `phase-plan` | 生成 phase/wave 计划 | `plan_artifacts`、`waves`、`gates`、`ownership` | 计划被接受或被阻塞 |
| `phase-execute` | 执行已接受 wave | `wave_status`、`lane_results`、`gate_outcomes`、`rollback_state` | wave 完成或阻塞 |
| `phase-plan-review` | 审核 phase 计划 | `alignment_findings`、`blocking_issues`、`approval_status` | 给出批准或阻塞结论 |
| `phase-contract-tools` | 验证和渲染 phase 契约工件 | `schema_checks`、`rendered_views`、`contract_issues` | 结果被 phase 技能消费 |

### 2.4 关键覆盖结论

- 这 18 个技能必须全部迁移到统一协议
- `skills/` 是唯一真相源，镜像目录不单独定义协议
- 任何“先只覆盖 12 个执行技能”的做法都不再作为目标状态

---

## 3. Skill Protocol v1

### 3.1 标准协议块

Skill Protocol v1 定义 7 个标准块：

| 阶段 | 协议块 | 适用范围 | 作用 |
|------|--------|----------|------|
| 输入 | `[task-input-validation]` | 每个新任务 | 在触发技能前先检查任务是否清晰、可界定、安全、可匹配 |
| 触发 | `[trigger-evaluation]` | 每个新任务 / 重大重规划 | 明确评估哪些技能应触发、跳过或延后 |
| 激活前 | `[precondition-check: <skill>]` | 每次激活技能前 | 验证前置条件满足 |
| 执行后 | `[skill-output: <skill>]` | 每个技能 | 提供结构化输出 |
| 执行后 | `[output-validation: <skill>]` | 每个技能 | 验证输出满足契约 |
| 保护 | `[loop-detected: <skill>]` | 发生重复激活风险时 | 中止盲目重试，要求解释或升级 |
| 生命周期 | `[skill-deactivation: <skill>]` | 技能退出活跃集合时 | 显式记录为什么卸载 |

### 3.2 标准顺序

默认顺序：

1. `[task-input-validation]`
2. `[trigger-evaluation]`
3. `[precondition-check: skill]`
4. `[skill-output: skill]`
5. `[output-validation: skill]`
6. 如有需要，输出 `[skill-deactivation: skill]`

如果检测到循环风险，则在重新激活前插入 `[loop-detected: skill]`。

### 3.3 最小骨架

```yaml
[task-input-validation]
task: "<user request verbatim>"
checks:
  clarity:
    status: PASS | FAIL
    reason: "<action and target are / are not identifiable>"
  scope:
    status: PASS | WARN | FAIL
    reason: "<bounded / can be scoped / unbounded>"
  safety:
    status: PASS | FAIL
    reason: "<safe / risky>"
  skill_match:
    status: PASS | WARN | FAIL
    reason: "<at least one skill family applies / none applies>"
result: PASS | WARN | REJECT
action: proceed | ask_clarification | reject
[/task-input-validation]

[trigger-evaluation]
task: "<one-line task summary>"
evaluated:
  - scoped-tasking: ✓ TRIGGER | ✗ SKIP | ⏸ DEFER
  - plan-before-action: ✓ TRIGGER | ✗ SKIP | ⏸ DEFER
  - multi-agent-protocol: ✓ TRIGGER | ✗ SKIP | ⏸ DEFER
activated_now: [...]
deferred: [...]
[/trigger-evaluation]

[precondition-check: <skill-name>]
checks:
  - <field>: ✓ PASS | ✗ FAIL
result: PASS | FAIL
[/precondition-check]

[skill-output: <skill-name>]
status: completed | failed | partial
confidence: high | medium | low
outputs: {...}
signals: {...}
recommendations: {...}
[/skill-output]

[output-validation: <skill-name>]
checks:
  - outputs.<field>: ✓ PASS | ✗ FAIL
result: PASS | FAIL
[/output-validation]

[skill-deactivation: <skill-name>]
reason: "<why>"
outputs_consumed_by: [...]
remaining_active: [...]
[/skill-deactivation]
```

### 3.4 语言无关规则

协议不允许使用英文中心规则，例如：

- `<5 words`
- `contains verb`
- `Add|Fix|Refactor|Implement` 这类英文动词正则

统一改为语言无关判断：

- **Clarity PASS**：能识别“动作 + 目标对象”
- **Scope PASS**：目标边界明确；或虽宽但可通过 `scoped-tasking` 收敛
- **Safety PASS**：没有无保护的破坏性或越权请求
- **Skill Match PASS**：至少一类技能可以合理接手

这条规则对中文、英文和混合输入都成立。

---

## 4. 各技能族的必备契约

### 4.1 Execution Skills

每个 execution skill 的 `SKILL.md` 必须新增或标准化以下部分：

- `Contract`
- `Failure Handling`
- `Output Example`
- `Deactivation Trigger`

**Contract 最低要求**：

- Preconditions：调用前必须满足的输入条件
- Postconditions：`status: completed` 时保证提供的字段
- Invariants：执行期间始终成立的约束
- Downstream Signals：给下游技能的结构化信号

**Failure Handling 最低要求**：

- 常见失败原因
- 是否允许重试，最多几次
- fallback skill 或用户升级条件
- `confidence: low` 时下游如何处理

### 4.2 Orchestration Skills

orchestration 技能不只是“也输出一个普通结果块”，还必须定义并行/仲裁语义。

每个 orchestration skill 的 `SKILL.md` 必须包含：

- `Delegation Contract`
- `Synthesis Contract`
- `Failure Handling`
- `Deactivation Trigger`

**`multi-agent-protocol` 最低要求**：

- 如何拆 lane
- 每个 lane 的目标和边界
- 如何回收子结果
- 如何给出 synthesis
- 子结果缺失或冲突时如何处理

**`conflict-resolution` 最低要求**：

- 冲突 claim 的表达格式
- 每条 claim 的证据来源
- 仲裁规则
- 不能裁定时的残余不确定性表达

### 4.3 Phase Skills

phase 技能是协议中最容易被漏掉的一组，因此必须单独定义工件契约。

每个 phase skill 的 `SKILL.md` 必须包含：

- `Artifact Contract`
- `Gate Contract`
- `Failure Handling`
- `Lifecycle`

**`phase-plan` 最低要求**：

- 输出哪些计划工件
- `wave` 的结构
- gate、owner、PR 顺序如何表达

**`phase-plan-review` 最低要求**：

- 审核输入是什么
- 阻塞条件是什么
- 通过/不通过如何结构化表达

**`phase-execute` 最低要求**：

- 读哪些计划工件
- wave 状态、lane 结果、回滚状态如何输出
- gate 未满足时如何停止

**`phase-contract-tools` 最低要求**：

- 校验哪些 schema / contract
- 输出哪些报告或渲染结果
- 失败时如何把问题回传给 phase 技能

---

## 5. 激活与卸载模型

### 5.1 新的硬规则

本次升级是 breaking change，因此生命周期规则也一并升级。

并发预算按技能族分别计算：

- **Execution**：最多 4 个同时活跃
- **Orchestration**：最多 1 个同时活跃
- **Primary Phase**：最多 1 个同时活跃
- **`phase-contract-tools`**：仅允许与 1 个 primary phase skill 同时存在，或在直接维护 phase 契约工具时单独激活

### 5.2 为什么按技能族分预算

如果继续用“全局统一 4 技能上限”，会让 phase/orchestration 场景和普通 execution 场景彼此打架。

按技能族分预算后：

- execution 会话仍保持紧凑
- orchestration 不会和普通技能混成一团
- phase 流程保留清晰的主状态

### 5.3 卸载规则

所有技能都必须显式卸载，不允许“自然遗忘”。

卸载触发：

- 输出已经被下游消费
- 当前阶段已切换
- 并发预算即将超限
- 失败后已升级到 fallback 或用户澄清

卸载时必须输出 `[skill-deactivation: <skill>]`。

---

## 6. 评测与工具链

### 6.1 统一评测入口

Skill Protocol v1 不新建一条独立的临时验证体系，而是统一接入现有：

- `maintainer/scripts/evaluation/run_trigger_tests.py`
- `maintainer/scripts/evaluation/run_claude_trigger_smoke.py`
- 相关 `maintainer/data/*` 与 `maintainer/reports/*`

### 6.2 评测脚本新增能力

评测脚本需要新增以下检查：

- 是否出现必需协议块
- 协议块顺序是否正确
- `[skill-output]` 是否都有对应 `[output-validation]`
- 是否缺少 `[precondition-check]`
- 是否存在未卸载的长期活跃技能
- 是否违反按技能族划分的并发预算
- orchestration/phase 技能是否缺少家族特有字段

### 6.3 机器可读 schema 的定位

可以引入 JSON Schema 或等价结构化定义，但其定位应为：

- 供评测脚本和未来平台适配使用
- 不作为当前仓库唯一运行方式
- 不绑定某个供应商 API 的专有参数

也就是说：

- **协议本体** 在文档、模板、技能定义中
- **schema** 是验证和适配层
- **vendor strict mode** 是可选平台集成，不是主设计

---

## 7. 全技能迁移路线图

### 7.1 原则

这是 breaking change，因此迁移必须按**原子批次**推进，不能长期混用新旧协议。

### 7.2 阶段划分

| 阶段 | 范围 | 交付物 | 完成门槛 |
|------|------|--------|----------|
| **阶段 0** | 协议冻结 | 本文档 + 块语法 + 家族预算规则 | 文档评审通过 |
| **阶段 1** | 模板与评测 | `templates/governance/*` + `maintainer/scripts/evaluation/*` 更新 | 脚本能识别 v1 协议 |
| **阶段 2** | 12 个 execution skills | 全部 execution `SKILL.md` 增加 Contract / Failure Handling / Deactivation | execution 用例通过 |
| **阶段 3** | 2 个 orchestration + 4 个 phase | 全部家族特有契约补齐 | 并行 / phase 用例通过 |
| **阶段 4** | 文档与示例 | `docs/user/`、`examples/`、CHANGELOG | 示例全部使用 v1 |

### 7.3 详细任务

#### 阶段 0：协议冻结

- [ ] 确认 7 个标准协议块
- [ ] 确认三类技能族预算规则
- [ ] 确认语言无关的输入判断标准
- [ ] 确认 schema 只是验证层，不是协议本体

#### 阶段 1：模板与评测

- [ ] 更新 `templates/governance/CLAUDE-template.md`
- [ ] 更新 `templates/governance/AGENTS-template.md`
- [ ] 扩展 `run_trigger_tests.py` 的协议块检查
- [ ] 扩展 `run_claude_trigger_smoke.py` 的协议顺序和预算检查

#### 阶段 2：Execution Skills

- [ ] 为 12 个 execution skills 统一补 `Contract`
- [ ] 为 12 个 execution skills 统一补 `Failure Handling`
- [ ] 为 12 个 execution skills 统一补 `Deactivation Trigger`
- [ ] 为 12 个 execution skills 补统一输出示例

#### 阶段 3：Orchestration + Phase Skills

- [ ] 为 `multi-agent-protocol` 补 `Delegation Contract` 和 `Synthesis Contract`
- [ ] 为 `conflict-resolution` 补冲突裁决契约
- [ ] 为 4 个 phase skills 补 `Artifact Contract`、`Gate Contract`、`Lifecycle`
- [ ] 明确 `phase-contract-tools` 的协同边界

#### 阶段 4：示例与用户文档

- [ ] 更新 `examples/`，覆盖 execution / orchestration / phase 三类场景
- [ ] 更新 `docs/user/` 使用指南
- [ ] 更新 CHANGELOG

---

## 8. 成功标准

### 8.1 覆盖率指标

| 指标 | 目标 |
|------|------|
| 纳入 v1 协议的技能数 | 18 / 18 |
| 具备 `Contract` 的技能数 | 18 / 18 |
| 具备 `Failure Handling` 的技能数 | 18 / 18 |
| 具备 `Deactivation Trigger` 的技能数 | 18 / 18 |
| 具备家族特有契约的 orchestration / phase 技能数 | 6 / 6 |

### 8.2 行为指标

| 指标 | 目标 |
|------|------|
| `[task-input-validation]` 出现率 | ≥95% |
| `[trigger-evaluation]` 出现率 | ≥95% |
| `[skill-output]` 与 `[output-validation]` 配对完整率 | 100% |
| 缺少 `[precondition-check]` 的技能激活次数 | 0 |
| 未显式卸载的技能退出次数 | 0 |
| 技能族预算超限次数 | 0 |
| 中文场景被英文规则误判次数 | 0 |

### 8.3 发布门槛

发布 Skill Protocol v1 前，必须同时满足：

- 18 个技能全部完成迁移
- `examples/` 不再使用旧协议块
- 评测脚本可识别并校验 v1 协议
- execution / orchestration / phase 三类代表场景全部通过

---

## 9. 非目标

以下内容不是本轮方案目标：

- 不把仓库改造成强绑定某个平台 API 的 runtime
- 不在仓库里新增“临时独立验证旁路”作为长期真相源
- 不继续维护“旧协议 + 新协议”双轨并存
- 不依赖英文词数、英文动词或英文正则来判断任务是否合法

---

## 10. 结论

本方案的核心判断是：

**如果决定升级，就应该一次性升级为覆盖全部技能的 Skill Protocol v1，而不是继续在 v0.2.1 的局部增强上叠加例外。**

这样做的收益是：

- 规则边界清晰
- 技能家族语义一致
- 长会话生命周期可控
- 评测入口统一
- 后续平台适配有稳定协议可依附

---

## 变更历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 0.3.1 | 2026-04-10 | 改写为**全技能协议化升级方案**：覆盖 18 个技能，采用 breaking-change 视角，统一 execution / orchestration / phase 三类技能协议 |
| 0.3.0 | 2026-04-10 | 业界最佳实践增强版（仅部分覆盖） |
| 0.2.1 | 2026-04-10 | 方案 A + 可观测性增强 |
| 0.2.0 | 2026-04-10 | 简化为方案 A：最小可行方案 |
| 0.1.0 | 2026-04-10 | 初始设计（已废弃，过度设计） |

---

**文档结束**
