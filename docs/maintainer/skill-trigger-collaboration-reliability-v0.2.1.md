# 技能触发与协作优化 - 最小可行方案 + 可观测性增强

**版本**: 0.2.1  
**日期**: 2026-04-10  
**状态**: 方案 A + 可观测性增强  
**作者**: 系统架构设计  

---

## 目录

- [1. 设计决策](#1-设计决策)
- [2. 核心改进](#2-核心改进)
  - [2.1 触发规则标准化](#21-触发规则标准化)
  - [2.2 技能输出格式统一与自验证](#22-技能输出格式统一与自验证)
  - [2.3 完整工作流示例](#23-完整工作流示例)
- [3. 实施路径](#3-实施路径)
- [4. 不做什么](#4-不做什么)
- [5. 成功标准](#5-成功标准)

---

## 1. 设计决策

### 1.1 为什么选择最小方案

原设计（0.1.0）存在**过度设计**问题：
- 引入了 6 种状态机状态（DORMANT → READY → ACTIVE → COMPLETED → FAILED → DROPPED）
- 创建了复杂的 `.agent-state/` 目录结构（config/runtime/outputs/checkpoints）
- 设计了三级验证体系（文本/契约/脚本）
- 假设了平台适配需求，但**核心差异在子 Agent API，不在状态管理**

**关键洞察**：
- 当前技能系统**没有显式状态管理**，靠 Agent 自然判断，已经工作得很好
- CLAUDE.md 里几行 "Escalate to XXX when..." 已经足够清晰
- 文件读写本来就是跨平台的，不需要特殊适配层

### 1.2 真正需要解决的问题

仅聚焦在**已验证存在**的问题，并识别核心风险：

1. **触发条件可读性**  
   当前 CLAUDE.md 的 "Skill Escalation" 部分是自然语言段落，难以快速查表

2. **技能输出一致性**  
   不同技能的输出格式略有差异，影响技能间数据传递的可靠性

3. **核心风险：Agent 可能不遵守规则**（新识别）  
   仅有表格和规范不够，Agent 可能：
   - 不读触发表格，直接开始编码
   - 读了表格但随意解读
   - 输出格式不按规范，导致协作失败
   
   **解决方案**：加入**可观测性增强**，强制 Agent 输出触发决策和自验证块

---

## 2. 核心改进

### 2.1 触发规则标准化

#### 当前状态

触发条件散落在 CLAUDE.md 的 "Skill Escalation" 部分，使用自然语言段落：

```markdown
- Escalate to `design-before-plan` when: the task involves choosing between 
  multiple implementation approaches, the change introduces or modifies a 
  public API or cross-module contract, acceptance criteria are missing or 
  unclear, or scoped-tasking identified the boundary but design decisions 
  remain open.
```

**问题**：
1. 难以快速查表，优先级不明确
2. **Agent 可能不读或随意解读规则**（核心风险）
3. 触发决策过程不透明，无法验证

#### 改进方案（两个层次）

**层次 1：触发条件表格化**

在 CLAUDE.md 中添加**触发条件表格**，保持 Markdown 格式（不引入 YAML）：

```markdown
## Skill Trigger Reference

| Skill | Priority | Trigger When | Dependencies |
|-------|----------|--------------|--------------|
| scoped-tasking | P0 | 任务描述 <20 词 OR 涉及 >2 模块 OR 范围未定义 | - |
| context-budget-awareness | P1 | 工作集 ≥8 文件 OR 重读次数 ≥3 OR 假设 ≥4 未验证 | - |
| design-before-plan | P2 | 有 ≥2 设计方案 OR API 变更 OR 验收标准缺失 | scoped-tasking |
| impact-analysis | P3 | 调用者 ≥3 OR 跨模块 OR 公共 API/类型变更 | read-and-locate |
| plan-before-action | P4 | 多文件编辑 OR 需要顺序协调 | scoped-tasking |
| bugfix-workflow | P5 | 报告了 bug 且根因未确认 | - |
| safe-refactor | P5 | 结构清理但保持行为不变 | - |
| read-and-locate | P6 | 需定位不熟悉的代码路径 | - |
| incremental-delivery | P7 | 计划跨 2-4 PR 但 <5 PR | plan-before-action |
| minimal-change-strategy | P8 | diff 超出任务范围 OR 有清理诱惑 | - |
| self-review | P9 | 多文件编辑完成后 | 编辑完成 |
| targeted-validation | P10 | 多种验证选项，需选最窄的 | - |
```

**好处**：
- 一目了然的优先级（P0 最高）
- 清晰的触发条件（可量化）
- 明确的依赖关系
- 无需引入新的配置文件或目录结构

**层次 2：触发决策可观测性（关键增强）**

仅靠表格不够，因为**依然依赖 Agent 自觉遵守**。加入强制性可观测性要求：

在 CLAUDE.md 中添加：

```markdown
## Trigger Decision Transparency

When evaluating a new task, you MUST output a trigger evaluation block:

[trigger-evaluation]
task: "<task summary in one line>"

evaluated:
  - scoped-tasking: ✓ TRIGGER (reason: task scope undefined, <20 words)
  - design-before-plan: ✗ SKIP (reason: no API changes detected)
  - context-budget-awareness: ✗ SKIP (reason: working set <8 files)
  - plan-before-action: ⏸ DEFER (reason: waiting for scoped-tasking output)
  - minimal-change-strategy: ✓ TRIGGER (reason: always active for edits)

activated_now: [scoped-tasking, minimal-change-strategy]
deferred: [plan-before-action]
[/trigger-evaluation]
```

**关键规则**：
- 必须评估 P0-P4 优先级的技能（scoped-tasking, context-budget-awareness, design-before-plan, impact-analysis, plan-before-action）
- 每个技能必须给出明确的 ✓ TRIGGER / ✗ SKIP / ⏸ DEFER 决策
- 必须说明原因（对照触发表格的条件）
- 如果触发了技能，稍后必须输出对应的 `[skill-output: xxx]` 块

**好处**：
- 用户能看到 Agent 是否读了触发表格
- 如果 Agent 跳过了应该触发的技能，用户能立刻发现并纠正
- 提供触发决策的审计轨迹（audit trail）
- 不需要文件系统或日志，纯文本输出到对话中

### 2.2 技能输出格式统一与自验证

#### 当前状态

大部分技能已使用 `[skill-output: xxx]` 文本块格式，但细节不一致。

**问题**：
1. 输出格式不统一，下游技能解析困难
2. **Agent 可能随意输出，不按规范**（核心风险）
3. 缺少验证机制，格式错误无法发现

#### 改进方案（两个层次）

**层次 1：输出格式规范化**

在各技能的 SKILL.md 中明确输出格式规范：

```markdown
[skill-output: <skill-name>]
status: completed | failed | partial
confidence: high | medium | low

outputs:
  <skill-specific-outputs>

signals:
  <signals-for-downstream-skills>

recommendations:
  next_skills: [...]
  skip_skills: [...]
[/skill-output]
```

**示例**（scoped-tasking）：

```markdown
[skill-output: scoped-tasking]
status: completed
confidence: high

outputs:
  objective: "Add webhook support to notification system"
  analysis_boundary:
    files: [src/webhooks/handler.py, src/webhooks/delivery.py, tests/test_webhooks.py]
    modules: [webhooks, notifications]
  excluded_areas: [billing, invoicing]

signals:
  design_decisions_open: true
  multi_file_edit: true
  estimated_file_count: 3

recommendations:
  next_skills: [design-before-plan]
  skip_skills: [read-and-locate]
[/skill-output]
```

**好处**：
- 统一的结构，方便下游技能解析
- 纯文本格式，Agent 直接可读
- 不需要写文件到 `.agent-state/outputs/`（除非需要跨会话传递）

**层次 2：输出自验证（关键增强）**

仅靠规范不够，Agent 可能忘记或随意输出。加入强制性自验证：

在 CLAUDE.md 中添加：

```markdown
## Skill Output Self-Validation

After outputting a skill result block, you MUST immediately self-validate:

[skill-output: scoped-tasking]
status: completed
confidence: high
outputs:
  objective: "Add webhook support"
  analysis_boundary:
    files: [src/webhooks/handler.py, src/webhooks/delivery.py]
  excluded_areas: [billing]
signals:
  design_decisions_open: true
  multi_file_edit: true
recommendations:
  next_skills: [design-before-plan]
[/skill-output]

[output-validation: scoped-tasking]
checking against contract in SKILL.md:
  ✓ status field present (completed)
  ✓ outputs.objective present
  ✓ outputs.analysis_boundary.files is list (2 files)
  ✓ outputs.excluded_areas present
  ✓ signals.design_decisions_open is boolean (true)
  ✓ signals.multi_file_edit is boolean (true)
  ✓ recommendations.next_skills is list
result: PASS - all required fields present
[/output-validation]
```

**关键规则**：
- 每个 `[skill-output:]` 块后必须紧跟 `[output-validation:]` 块
- 必须对照 SKILL.md 中的规范检查所有必需字段
- 如果缺少必需字段，必须重新输出技能结果
- 验证通过后，才能继续下一步

**好处**：
- Agent 强制自查输出是否完整
- 用户能看到验证过程，发现遗漏
- 下游技能可以信任上游输出的完整性
- 纯文本，无需脚本或工具

---

## 2.3 完整工作流示例

展示触发评估 → 技能执行 → 输出验证的完整流程：

```markdown
User: "Add webhook support to notification system"

Agent:
[trigger-evaluation]
task: "Add webhook support to notification system"

evaluated:
  - scoped-tasking: ✓ TRIGGER (reason: scope unclear, need boundary definition)
  - context-budget-awareness: ✗ SKIP (reason: new task, no context overload yet)
  - design-before-plan: ⏸ DEFER (reason: wait for scoped-tasking to identify design needs)
  - plan-before-action: ⏸ DEFER (reason: wait for scope definition)
  - minimal-change-strategy: ✓ TRIGGER (reason: always active for implementation tasks)

activated_now: [scoped-tasking, minimal-change-strategy]
deferred: [design-before-plan, plan-before-action]
[/trigger-evaluation]

Proceeding with scoped-tasking...

[skill-output: scoped-tasking]
status: completed
confidence: high

outputs:
  objective: "Add webhook support to notification system"
  analysis_boundary:
    files: 
      - src/webhooks/handler.py
      - src/webhooks/delivery.py
      - tests/test_webhooks.py
    modules: [webhooks, notifications]
  excluded_areas: [billing, invoicing]

signals:
  design_decisions_open: true
  multi_file_edit: true
  estimated_file_count: 3

recommendations:
  next_skills: [design-before-plan]
  skip_skills: [read-and-locate]
[/skill-output]

[output-validation: scoped-tasking]
checking against SKILL.md contract:
  ✓ status: completed
  ✓ outputs.objective present
  ✓ outputs.analysis_boundary.files is list (3 items)
  ✓ outputs.excluded_areas present
  ✓ signals.design_decisions_open is boolean (true)
  ✓ signals.multi_file_edit is boolean (true)
  ✓ recommendations.next_skills is list (1 item)
result: PASS
[/output-validation]

Based on scoped-tasking output signal 'design_decisions_open: true', 
activating design-before-plan...
```

**关键点**：
- 用户能看到哪些技能被评估、为什么触发/跳过
- 用户能看到技能输出是否完整
- 验证失败时，Agent 会立刻发现并修正
- 下游技能根据上游的 signals 决定是否激活

---

## 3. 实施路径

### 第 1 周：触发规则表格化 + 可观测性

**任务**：
1. 在 CLAUDE.md 中添加 "Skill Trigger Reference" 表格
2. 将现有的 "Skill Escalation" 部分转换为表格格式
3. **添加 "Trigger Decision Transparency" 规则**（新增）
4. 在 `templates/governance/CLAUDE-template.md` 中同步更新

**验证**（关键）：
- 表格是否覆盖所有执行技能（12 个）
- 优先级是否有冲突（同一优先级的技能是否互斥）
- 依赖关系是否正确
- **触发评估块的格式是否清晰可执行**（新增）

**真实场景验证**（在实施前必须完成）：
1. 找 3 个之前 Agent 忽略了应该触发的技能的真实场景
2. 用新的表格 + 触发评估块规则重新测试
3. 验证 Agent 是否：
   - 输出了 `[trigger-evaluation]` 块
   - 按表格正确评估了所有 P0-P4 技能
   - 触发了正确的技能
   - 给出了合理的跳过/延迟原因
4. **如果 3 个场景中有任何 1 个失败 → 暂停实施，重新评估方案**

### 第 2 周：技能输出格式规范化 + 自验证

**任务**：
1. 在每个 SKILL.md 的 "Usage" 部分添加输出格式示例
2. 确保所有技能都包含：
   - `status` 字段
   - `outputs` 部分（技能特定）
   - `signals` 部分（给下游技能的信号）
   - `recommendations` 部分（可选）
3. **在 CLAUDE.md 中添加 "Skill Output Self-Validation" 规则**（新增）
4. **为每个技能在 SKILL.md 中列出必需字段清单**（新增）

**验证**（关键）：
- 所有 SKILL.md 是否包含必需字段清单（required_outputs, required_signals）
- **自验证块的格式是否清晰可执行**（新增）

**真实场景验证**（在实施前必须完成）：
1. 找 3 个技能协作场景（如 scoped-tasking → design-before-plan → plan-before-action）
2. 用新的输出规范 + 自验证规则测试
3. 验证：
   - Agent 是否输出了规范的 `[skill-output:]` 块
   - Agent 是否输出了 `[output-validation:]` 块
   - 自验证是否捕获了缺失字段
   - 下游技能是否能正确解析上游输出
4. **如果 3 个场景中有任何 1 个失败 → 调整规范或验证规则**

### 第 3 周：文档和测试

**任务**：
1. 更新 `docs/user/` 中的使用指南，加入触发表格和输出示例
2. 在 `examples/` 中添加 2-3 个示例，展示技能协作输出格式
3. 更新 CHANGELOG

**可交付成果**：
- ✅ CLAUDE.md 新增触发规则表格
- ✅ 所有 SKILL.md 包含输出格式示例
- ✅ 用户文档更新完成

---

## 4. 不做什么

为了保持最小可行方案，**明确不做**以下内容：

### ❌ 不引入状态机
- **不做**：DORMANT → READY → ACTIVE → COMPLETED 状态转移
- **原因**：当前 Agent 自然判断已足够，无需显式状态管理
- **替代**：靠触发优先级和依赖关系隐式控制激活顺序

### ❌ 不创建 `.agent-state/` 目录
- **不做**：复杂的 config/runtime/outputs/checkpoints 目录结构
- **原因**：大部分状态不需要跨会话持久化，输出块在对话中已足够
- **例外**：如果未来确实需要跨会话传递数据，再考虑最小化的文件持久化

### ❌ 不引入触发日志
- **不做**：`.agent-state/runtime/trigger-log.jsonl`
- **原因**：没有验证过需要调试触发历史的场景
- **替代**：如果需要调试，Agent 可输出 `[trigger-evaluation]` 块到对话中

### ❌ 不写契约验证脚本
- **不做**：Python 脚本验证技能输出是否符合契约
- **原因**：Agent 自己能判断输出是否符合预期
- **替代**：在 SKILL.md 中明确输出格式即可，靠 Agent 自验证

### ❌ 不创建平台适配层
- **不做**：`platform_detector.py` 和 `cross_platform_installer.py`
- **原因**：当前 `manage-governance.py` 已经处理了平台差异（`.cursor/` vs `.claude/`）
- **替代**：保持现有安装逻辑，核心问题不在平台适配

### ❌ 不设计降级策略
- **不做**：复杂的 fallback chains 和 recovery actions
- **原因**：技能失败时，Agent 可以自然地降级或请求用户输入
- **替代**：在 SKILL.md 中写明常见失败场景和建议处理方式（自然语言）

---

## 5. 成功标准

**方案 A + 可观测性增强是否成功，基于以下标准**：

### 文档层面
1. **可读性提升**：维护者能在 30 秒内查到某个技能的触发条件和优先级
2. **零复杂度增长**：不引入新的配置文件、目录结构或验证脚本（仅增加 CLAUDE.md 规则）

### 行为层面（关键）
3. **触发决策可见性**：Agent 在 90% 的任务中输出 `[trigger-evaluation]` 块
4. **触发准确性**：对照触发表格，Agent 在 80% 的场景中正确触发应该触发的技能
5. **输出格式一致性**：Agent 在 90% 的场景中输出规范的 `[skill-output:]` 块
6. **自验证执行率**：Agent 在 80% 的场景中输出 `[output-validation:]` 块
7. **协作可靠性**：技能间数据传递因格式问题导致的失败率 <10%

### 验证方法
- 收集 20 个真实任务场景
- 人工审查 Agent 的输出
- 统计触发评估块、输出验证块的出现率
- 统计触发准确性和格式一致性
- **如果任何核心指标（3-7）低于阈值 → 方案失败**

**失败标准**（触发重新评估）：

- 表格维护成本过高（每次新增技能需要大量协调）
- **Agent 忽略 `[trigger-evaluation]` 或 `[output-validation]` 规则**（新增，核心风险）
- 输出格式不一致问题仍然存在
- 触发决策依然不透明，用户无法理解为什么某个技能没被触发
- 用户反馈需要更强的强制机制（如脚本验证）

如果失败，需要考虑：
1. **先尝试**：强化 CLAUDE.md 的规则表述（如"MUST output"）
2. **再考虑**：引入轻量级验证脚本（但仅在行为验证失败后）
3. **最后考虑**：0.1.0 版本的部分设计（但仅在真实失败案例驱动下）

---

## 变更历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| 0.2.1 | 2026-04-10 | 系统架构 | 方案 A + 可观测性增强：加入触发决策透明性和输出自验证 |
| 0.2.0 | 2026-04-10 | 系统架构 | 简化为方案 A：最小可行方案 |
| 0.1.0 | 2026-04-10 | 系统架构 | 初始设计文档（已废弃，过度设计） |

---

**文档结束**
