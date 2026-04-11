# 技能描述优化方案

基于触发测试结果（qwen3.6-plus: 82.9%，GLM-4.7: 76.8%），以下是针对性优化建议。

---

## 🔴 优先级 P0：高频失败（影响 3+ 用例）

### 1. incremental-delivery

**当前描述**：
```
Split a multi-step plan into 2-4 independently mergeable increments when the task is too large for a single PR but too small for the full phase system. Use when plan-before-action produces a plan spanning 2-4 PRs across 1-2 modules.
```

**问题**：与 phase-plan 边界不清，模型倾向选择"更大"的 phase-plan

**优化后**：
```
Split a plan into 2-4 independently mergeable PRs when the task is medium-sized. ONLY use when: (1) explicitly mentions "3 PRs" or "4 PRs", OR (2) spans exactly 1-2 modules without parallel work or external specs. If 5+ PRs, 3+ modules, or needs parallel lanes → use phase-plan instead.
```

**改进点**：
- ✅ 强调"ONLY use when"排他条件
- ✅ 明确数字边界（3-4 个明确提到的 PR）
- ✅ 对比 phase-plan 的升级条件

---

### 2. minimal-change-strategy

**当前描述**：
```
Constrain a code change to the smallest viable patch when the diff is growing beyond the task, cleanup temptation is high, or multiple edit strategies compete. Not needed for simple single-file fixes where AGENTS.md Change Rules suffice.
```

**问题**：关键触发词不够明显（"约束"、"不要改"、"不可逆"）

**优化后**：
```
Constrain a code change to the smallest viable patch. Use when: (1) user says "don't change X" or "keep Y unchanged", (2) multiple implementation approaches exist and smallest must be chosen, (3) diff is growing beyond task scope, (4) operation is irreversible (database drop, force push), or (5) cleanup temptation is high. Not needed for simple edits.
```

**改进点**：
- ✅ 添加"不可逆操作"触发条件
- ✅ 明确"约束性语言"关键词
- ✅ 强调"多策略选择"场景

---

## 🟡 优先级 P1：阈值判断问题（2个用例）

### 3. context-budget-awareness

**当前描述**：
```
Narrow working state by compressing and refocusing when an investigation is stuck or spinning. Use when many files are read without convergence, the same areas checked repeatedly without progress, hypotheses accumulate without evidence to rank them, or recent actions fail to advance the objective. Uses a structured Context Ledger to make self-monitoring observable and verifiable.
```

**问题**：
- "many files" 模糊，导致 7 vs 8 误判
- "hypotheses accumulate" 未明确数量

**优化后**：
```
Compress working state when investigation is stuck. Use when: (1) 8+ files read without convergence, (2) same file read 3+ times without new leads, (3) 4+ competing hypotheses without evidence ranking, or (4) last 3+ actions didn't advance the goal. Do NOT trigger for 7 or fewer files if progress is steady.
```

**改进点**：
- ✅ 明确阈值：8+ 文件（不是 7）
- ✅ 明确阈值：4+ 假设（不是 3）
- ✅ 添加反例："7 或更少且有进展时不触发"

---

### 4. impact-analysis

**当前描述**：
```
Assess the blast radius of a planned code change by tracing outward from the edit point to affected callers, dependents, and contracts before planning. Use when the change touches shared interfaces, public APIs, data models, or has 3+ tentative leads from discovery.
```

**问题**：2 vs 3 调用者边界判断

**优化后**：
```
Assess blast radius of code changes. Use when: (1) function/API has 3+ callers across modules, (2) modifies public API or shared interface, (3) changes data model used by 3+ modules, or (4) read-and-locate found 3+ tentative leads. Do NOT use for 2 or fewer callers in single module.
```

**改进点**：
- ✅ 明确"3+ 调用者"（不是 2）
- ✅ 强调"跨模块"特性
- ✅ 添加反例

---

## 🟢 优先级 P2：边界混淆（2-3个用例）

### 5. read-and-locate

**当前描述**：
```
Find the relevant files, code paths, and edit points in an unfamiliar area of the codebase when the agent must trace a runtime, data, ownership, or configuration path. Do not use when an exact symbol, class, function, or file search is sufficient.
```

**问题**：信息查询也被误触发

**优化后**：
```
Find files and edit points in unfamiliar code BEFORE making changes. Use when: (1) user wants to modify code but location is unknown, (2) must trace runtime/data/ownership path to find where to edit. Do NOT use for: (1) information queries with no edit intent ("What database does this use?"), (2) exact symbol search with known name, (3) questions about existing code without modification plans.
```

**改进点**：
- ✅ 强调"BEFORE making changes"（编辑前提）
- ✅ 明确排除"纯信息查询"
- ✅ 添加具体反例

---

### 6. scoped-tasking

**当前描述**：
```
Narrow a broad or ambiguous task to the smallest useful boundary before exploring or editing. Use when the request is wide but the likely edit surface is small, or when scope is expanding without evidence.
```

**问题**：与 read-and-locate、design-before-plan 边界不清

**优化后**：
```
Narrow broad/ambiguous tasks to smallest boundary. Use when: (1) request mentions multiple systems but target unclear ("search is broken" - which search?), (2) task is expanding without evidence, (3) user request has no clear action or target. Do NOT use when: (1) scope is clear but location unknown (use read-and-locate), (2) scope is clear but design choices remain (use design-before-plan).
```

**改进点**：
- ✅ 与其他技能明确边界
- ✅ 添加"多系统歧义"示例
- ✅ 区分"范围不清"vs"位置不清"vs"设计不清"

---

## 🔵 优先级 P3：特殊场景（1-2个用例）

### 7. multi-agent-protocol

**当前描述**：
```
Guide parallel subagent launching, coordination, and synthesis through complete operational protocol. Use when the AGENTS.md multi-agent rules indicate Tier 1 or Tier 2 parallelism and the agent needs the full decision framework, subagent prompt templates, merge checklist, and failure handling procedures.
```

**问题**：隐式并行机会识别不足

**优化后**：
```
Launch and coordinate parallel subagents. Use when: (1) user explicitly says "in parallel", (2) task describes 3+ independent investigation areas owned by different teams/modules, or (3) AGENTS.md rules indicate Tier 2 parallelism. Implicit parallel opportunity: "understand X system, Y service, and Z pipeline" = 3 independent areas.
```

**改进点**：
- ✅ 添加"隐式并行"识别规则
- ✅ 强调"3+ 独立区域"
- ✅ 提供具体示例

---

### 8. phase-contract-tools

**当前描述**：
```
Review and validate phase contract schemas, execution docs, and rendering tools. Usually loaded by phase-plan or phase-execute. Use directly when the task is to fix, extend, or validate the phase contract scripts, schema definitions, or renderers themselves.
```

**问题**：单独触发场景不够明显

**优化后**：
```
Maintain phase system infrastructure. Use ONLY when: (1) task explicitly mentions "fix phase schema validator", "update plan.yaml contract", or "repair phase rendering", (2) working on phase-contract-tools directory itself, or (3) validating phase plan format. Do NOT use for regular phase planning or execution.
```

**改进点**：
- ✅ 强调"ONLY when"元工作场景
- ✅ 明确排除常规 phase 工作
- ✅ 添加关键词提示

---

## 📊 优化影响预估

基于失败用例分布：

| 优化技能 | 受影响用例数 | 预计提升 |
|---------|------------|---------|
| incremental-delivery | 3 | +3.7% |
| minimal-change-strategy | 3 | +3.7% |
| context-budget-awareness | 2 | +2.4% |
| impact-analysis | 1 | +1.2% |
| read-and-locate | 2 | +2.4% |
| scoped-tasking | 2 | +2.4% |
| multi-agent-protocol | 1 | +1.2% |
| phase-contract-tools | 1 | +1.2% |
| **总计** | **15** | **+18.3%** |

**预期准确率**：82.9% → **~95%+**

---

## 🚀 实施计划

### Phase 1：高优先级（P0）
1. ✏️ 修改 `incremental-delivery/SKILL.md` frontmatter
2. ✏️ 修改 `minimal-change-strategy/SKILL.md` frontmatter
3. 🔄 重新生成 `skill_index.json`
4. 🧪 运行触发测试验证

### Phase 2：阈值优化（P1）
1. ✏️ 修改 `context-budget-awareness/SKILL.md`
2. ✏️ 修改 `impact-analysis/SKILL.md`
3. 🔄 更新索引
4. 🧪 测试验证

### Phase 3：边界清晰化（P2-P3）
1. ✏️ 批量修改 6 个技能
2. 🔄 更新索引
3. 🧪 全量测试
4. 📊 对比报告

---

## 📋 验证清单

- [ ] 所有优化后的描述 ≤ 250 字符（适合 LLM 处理）
- [ ] 每个描述包含明确的"Use when"条件
- [ ] 边界技能之间有明确的"Do NOT use when"排他条件
- [ ] 数字阈值明确（3+, 8+）且带有反例（不是 2, 不是 7）
- [ ] skill_index.json 与 SKILL.md 同步
- [ ] 触发测试准确率 ≥ 95%

---

## 🔧 自动化脚本

```bash
# 1. 修改技能描述后重新生成索引
python3 maintainer/scripts/maintenance/generate_skill_index.py

# 2. 运行触发测试
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --compact-mode \
  --enable-cache \
  --concurrency 5

# 3. 对比前后结果
diff <(cat old_results.txt) <(cat new_results.txt)
```
