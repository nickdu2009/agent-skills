# 测试评估体系修复计划

> 基于日期：2026-03-28
> 上游评估：`docs/maintainer/skill-system-evaluation.md`
> 执行状态：R1/R3/R4/R5/R6/R7 已完成，R2 待手动执行

---

## 问题摘要

| 编号 | 缺口 | 严重度 | 当前状态 |
|------|------|--------|----------|
| G1 | 零实际测试数据 | 严重 | 模板存在，无输出 |
| G2 | 行为测试无自动化 | 中等 | 触发测试有 `--mode api`，行为测试完全人工 |
| G3 | 阶段系统零行为覆盖 | 中等 | 3 个技能无场景、无 rubric 条目 |
| G4 | 触发用例分布不均 | 低 | `discovery` 和 `context-budget` 各 2 例 |
| G5 | 技能生命周期无评分维度 | 低 | 转录模板有检查项但 rubric 无对应条目 |
| G6 | 无回归追踪机制 | 低 | 单次报告可生成，无版本间对比 |

---

## 修复项

### R1 — 执行首轮触发测试基线（解决 G1）

**优先级**：P0

**目标**：用 `run_trigger_tests.py --mode api` 产出第一份有数据的触发测试报告，填入 `cross-platform-trigger-baseline.md` 模板。

**步骤**：

1. 在 `.env` 中配置 `OPENAI_API_KEY`（已有 `dotenv` 支持）。
2. 执行全量触发测试：
   ```bash
   uv run maintainer/scripts/evaluation/run_trigger_tests.py --mode api
   ```
3. 将结果保存到 `maintainer/reports/baselines/trigger-baseline-YYYY-MM-DD.md`，按 `templates/evaluation/cross-platform-trigger-baseline.md` 格式填写。
4. 在 Cursor 中手动运行 3-5 个代表性 case，记录实际平台触发行为与 API 评估的差异。

**产出文件**：

| 文件 | 操作 |
|------|------|
| `maintainer/reports/baselines/trigger-baseline-YYYY-MM-DD.md` | 新建 |
| `.gitignore` | 确认 `maintainer/reports/baselines/` 保持可提交 |

**验收条件**：报告包含 22 个 case 的 pass/partial/miss/fail 结果和总通过率。

---

### R2 — 执行首轮行为场景测试（解决 G1）

**优先级**：P0

**目标**：对至少 2 个场景执行手动测试，填写 `templates/evaluation/transcript-evaluation-report.md`。

**步骤**：

1. 选择 `single-agent-bugfix.md` 和 `safe-refactor.md` 作为首轮场景。
2. 在 Cursor 中新建会话，粘贴 `skill-testing-playbook.md` 中的 Prompt Template。
3. 记录完整转录，按 `transcript-evaluation-report.md` 评分。
4. 保存到 `maintainer/reports/baselines/behavior-YYYY-MM-DD-<scenario>.md`。

**产出文件**：

| 文件 | 操作 |
|------|------|
| `maintainer/reports/baselines/behavior-YYYY-MM-DD-single-agent-bugfix.md` | 新建 |
| `maintainer/reports/baselines/behavior-YYYY-MM-DD-safe-refactor.md` | 新建 |

**验收条件**：每份报告包含 6 个 Global Dimension 评分和所有相关 skill-specific 评分，Decision 行已填写。

---

### R3 — 阶段系统行为覆盖（解决 G3）

**优先级**：P1

**目标**：为阶段系统补充行为场景、rubric 条目和触发测试数据。

#### R3a — 新增行为场景

在 `examples/` 新建 `phased-migration-planning.md`。

场景设计：

> 将一个跨 3 个服务的数据库 schema 迁移分解为阶段计划。需要识别 hotspot、设计 wave 顺序、产出 phaseN-plan.yaml，并通过验证器检查。

技能组合：`phase-plan`、`phase-contract-tools`、`scoped-tasking`、`plan-before-action`

观测重点：
- schema 优先于 Markdown
- 默认四文件输出契约被遵守
- 验证器在 YAML 产出后立即运行
- 不手写 prompt，使用渲染器派生

**产出文件**：

| 文件 | 操作 |
|------|------|
| `examples/phased-migration-planning.md` | 新建 |

#### R3b — 补充 rubric 条目

在 `maintainer/data/skill_test_data.py` 的 `SKILL_RUBRICS` 中新增三条：

```python
"phase-plan": (
    "Pass if the execution schema is the authority and the strict four-file doc set is produced with validators run.",
    "Fail if Markdown redefines YAML-owned fields, extra planning docs are created, or validators are skipped.",
),
"phase-execute": (
    "Pass if execution reads from the accepted schema, respects lane isolation, and reports wave state per contract.",
    "Fail if the agent reopens planning during execution, paraphrases lane contracts, or skips validation.",
),
"phase-contract-tools": (
    "Pass if contract authority stays centralized and smoke checks pass after any script change.",
    "Fail if contract rules are duplicated in sibling skills or golden files drift without update.",
),
```

在 `examples/skill-evaluation-rubric.md` 的 `Skill-Specific Pass vs. Fail` 部分新增对应条目。

#### R3c — 补充场景矩阵条目

在 `maintainer/data/skill_test_data.py` 的 `EXAMPLE_CASES` 和 `examples/skill-testing-playbook.md` 的 Scenario Matrix 中新增 `phased-migration-planning.md` 对应行。

**产出文件**：

| 文件 | 操作 |
|------|------|
| `maintainer/data/skill_test_data.py` | 修改：新增 3 个 rubric + 1 个 example case |
| `examples/skill-evaluation-rubric.md` | 修改：新增 3 个 skill-specific 段落 |
| `examples/skill-testing-playbook.md` | 修改：Scenario Matrix 新增 1 行 |

---

### R4 — 行为测试 LLM-as-judge 自动化（解决 G2）

**优先级**：P1

**目标**：新建 `maintainer/scripts/evaluation/run_behavior_eval.py`，接受转录文件输入，使用 LLM 按 rubric 自动评分。

**设计约束**：

- 复用 `skill_test_data.py` 中的 `GLOBAL_RUBRIC_DIMENSIONS` 和 `SKILL_RUBRICS`
- 输入：转录文本文件 + 场景 ID（用于关联 `EXAMPLE_CASES` 中的期望）
- 输出：JSON 评分结果 + 可读 Markdown 报告
- 模式：`--mode prompt`（生成评估提示词供手动粘贴）和 `--mode api`（调用 API 自动评分）
- 评分格式与 `skill-evaluation-rubric.md` 的 0/1/2 制对齐

**输入契约**：

```text
maintainer/scripts/evaluation/run_behavior_eval.py --transcript path/to/transcript.txt --scenario single-agent-bugfix.md [--mode api|prompt]
```

**输出契约**（`--mode api`）：

```json
{
  "scenario": "single-agent-bugfix.md",
  "global_scores": {
    "Scope discipline": {"score": 2, "evidence": "..."},
    ...
  },
  "skill_scores": {
    "bugfix-workflow": {"score": 2, "evidence": "..."},
    ...
  },
  "decision": "pass",
  "issues": []
}
```

**产出文件**：

| 文件 | 操作 |
|------|------|
| `maintainer/scripts/evaluation/run_behavior_eval.py` | 新建 |

**验收条件**：对一份手动转录运行 `--mode api` 产出的评分与人工评分在同一 Decision 级别（pass/conditional/fail 一致）。

---

### R5 — 扩充触发测试用例（解决 G4）

**优先级**：P2

**目标**：为 `discovery` 和 `context-budget` 各增加 2-3 个边界 case。

新增用例设计：

**discovery 类别**：

| Case ID | 设计意图 |
|---------|----------|
| `partial-path-known` | 知道模块但不知道具体文件，边界：是否触发 `read-and-locate` |
| `grep-sufficient` | 用户提供了明确的函数名，grep 就够了，不应触发 discovery 技能 |

**context-budget 类别**：

| Case ID | 设计意图 |
|---------|----------|
| `many-files-opened` | Agent 已读 10+ 文件但未收敛，应触发 `context-budget-awareness` |
| `repeated-hypothesis` | 同一个假设被反复测试但无进展，应触发 |
| `medium-session-focused` | 中等长度会话但目标清晰，不应触发 |

**产出文件**：

| 文件 | 操作 |
|------|------|
| `maintainer/data/trigger_test_data.py` | 修改：新增 5 个 case |

---

### R6 — 技能生命周期评分维度（解决 G5）

**优先级**：P2

**目标**：将现有的 `transcript-evaluation-report.md` 中的 Skill Lifecycle Check 升级为正式 rubric 维度。

**变更**：

在 `examples/skill-evaluation-rubric.md` 的 Global Dimensions 表中新增一行：

| Dimension | Pass Signal | Failure Signal |
|-----------|-------------|----------------|
| Skill lifecycle | Skills are loaded on demand and dropped when their phase ends; no more than 4 active simultaneously without justification | Unnecessary skills are carried throughout the session; the context budget grows from stale skill guidance |

在 `maintainer/data/skill_test_data.py` 的 `GLOBAL_RUBRIC_DIMENSIONS` 中新增对应条目。

**产出文件**：

| 文件 | 操作 |
|------|------|
| `examples/skill-evaluation-rubric.md` | 修改：Global Dimensions 新增 1 行 |
| `maintainer/data/skill_test_data.py` | 修改：`GLOBAL_RUBRIC_DIMENSIONS` 新增 1 条 |
| `maintainer/scripts/evaluation/generate-skill-test-report.py` | 无需改动（自动读取 `GLOBAL_RUBRIC_DIMENSIONS`） |

---

### R7 — 回归追踪机制（解决 G6）

**优先级**：P3

**目标**：建立轻量级的版本间对比机制，无需复杂基础设施。

**方案**：

1. 在 `maintainer/reports/baselines/` 目录下按日期命名基线报告文件（R1、R2 已定义命名规则）。
2. 在 `maintainer/scripts/evaluation/generate-skill-test-report.py` 中增加 `--compare` 参数，接受两份报告路径，输出变化的评分维度。
3. 报告文件顶部包含 git SHA，支持将评分结果与代码版本关联。

**产出文件**：

| 文件 | 操作 |
|------|------|
| `maintainer/scripts/evaluation/generate-skill-test-report.py` | 修改：新增 `--compare` 参数 |

---

## 执行顺序

```
R1 (触发基线)  ─┐
                ├─→ R4 (行为自动化) ─→ R7 (回归追踪)
R2 (行为基线)  ─┘
                 ↑
R3 (阶段覆盖)  ──┘
R5 (触发扩充)  ── 独立可并行
R6 (生命周期)  ── 独立可并行
```

- R1 和 R2 可并行，无依赖。
- R3 在 R2 之前完成更好（先有场景再跑测试），但不是硬性依赖。
- R4 依赖 R2 的手动基线数据作为校准参照。
- R5 和 R6 无依赖，任何时候可插入。
- R7 在有至少两份报告后才有意义，排在最后。

---

## 变更影响汇总

| 文件 | 类型 | 涉及修复项 |
|------|------|-----------|
| `examples/phased-migration-planning.md` | 新建 | R3a |
| `maintainer/scripts/evaluation/run_behavior_eval.py` | 新建 | R4 |
| `maintainer/reports/baselines/trigger-baseline-*.md` | 新建 | R1 |
| `maintainer/reports/baselines/behavior-*-*.md` | 新建 | R2 |
| `maintainer/data/skill_test_data.py` | 修改 | R3b, R3c, R6 |
| `maintainer/data/trigger_test_data.py` | 修改 | R5 |
| `maintainer/scripts/evaluation/generate-skill-test-report.py` | 修改 | R7 |
| `examples/skill-evaluation-rubric.md` | 修改 | R3b, R6 |
| `examples/skill-testing-playbook.md` | 修改 | R3c |
| `.gitignore` | 确认 | R1 |

---

## 不做什么

- 不重新设计测试框架架构（当前架构是正确的）。
- 不构建 CI 级别的行为测试自动化（LLM-as-judge 的结果不稳定到足以做 CI gate）。
- 不为 AGENTS.md 规则本身建立单独的测试套件（通过行为场景间接覆盖已足够）。
- 不构建 dashboard 或 web UI（`maintainer/reports/` 目录 + Markdown 足够当前阶段）。

---

## 风险

| 风险 | 缓解 |
|------|------|
| LLM-as-judge 评分与人工评分不一致 | R4 验收条件要求 Decision 级别一致，不要求逐维度完全匹配 |
| 阶段系统场景太复杂，手动测试成本高 | R3a 场景设计为"纯规划"，不要求实际执行 wave |
| 触发测试 API 结果因模型版本变化不稳定 | 报告中记录模型版本，版本变更后重新建立基线 |
