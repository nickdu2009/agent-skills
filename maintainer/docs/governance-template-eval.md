# Governance Template Evaluation

**Status**: Current maintainer workflow
**Current implementation note**: The live evaluator targets the post-2026-05 governance model centered on `Behavioral Guidelines`, `Validation Rules`, `Skill Activation`, `Escalation Rules`, `Common Flow Patterns`, and `Multi-Agent Rules`. Older concepts such as `Skill Family Concurrency Budgets`, `Forward Handoffs` / `Fallbacks`, and versioned `Skill Protocol v1` / `Skill Protocol v2` sections are not part of the live suite.

## Purpose

治理模板不是给解析器消费的，它是给 agent 直接读取并执行的。  
因此这个 evaluator 关心的不是 markdown 语法是否漂亮，而是：

- agent 只能看到治理模板本身时，能否读出正确的治理边界
- 模板里引用的 skills 是否都有进入路径
- “默认继续 / 必须停下 / 可以并行 / 必须 `[delegate: 0]`” 这些规则是否真的可判定

这套评测是 template-first 治理闭环的一部分，不替代：

- `run_manage_governance_smoke.py` 的安装投影 smoke
- `check_governance_sync.py` 的模板/根文件同步检查
- `check_cross_references.py` 的仓库引用完整性检查

## Isolation Contract

### Why isolation matters

如果直接在仓库工作区里跑 agent，结果会被这些额外上下文污染：

- 仓库根 `AGENTS.md` / `CLAUDE.md`
- `skills/` 树里的详细 skill 正文
- `maintainer/` 下的历史报告、fixtures、评测脚本

这会让 agent “答对”并不一定是模板写得对，而可能只是偷看了别的文件。

### What the evaluator does

`maintainer/governance_eval/run_eval.py` 会为每个 CLI 建一个临时工作区，只放：

- 一个空 git repo
- 被测治理文件（部署为 `AGENTS.md` 或 `CLAUDE.md`）

agent 在那个隔离工作区里只能读取它真正会在目标项目里看到的治理文件。

### Prompt rule

所有 live case 都必须只引用 `{{GOVERNANCE_FILE}}`，不能引用仓库其他路径。

允许：

```yaml
prompt: |
  Read {{GOVERNANCE_FILE}}.
  Based ONLY on the governance file, ...
```

不允许：

- 要求读取 `skills/`
- 要求读取 `templates/`
- 要求读取 `maintainer/`
- 要求理解当前仓库业务上下文后再回答

## File Layout

```text
maintainer/
├── governance_eval/
│   ├── cases.yaml
│   └── run_eval.py
└── docs/
    └── governance-template-eval.md
```

职责分工：

- `cases.yaml`: live case catalog，定义 prompt、judge 与 `expect_current`
- `run_eval.py`: 隔离工作区 driver，负责运行 CLI、抽取响应、判定 PASS/FAIL
- 本文档：解释 live suite 测什么、不测什么，以及怎样维护

## Current Live Cases

当前 live suite 包含 33 个 case，全部面向当前治理模型：

| ID | Category | What it validates | Expected now |
|---|---|---|---|
| `activation_paths` | static | 模板里引用的 skills 是否都有显式进入路径 | `pass` |
| `local_continue` | behavioral | 小范围本地改动是否可默认继续 | `pass` |
| `requirements_change_requires_pause` | behavioral | 需求 / 验收标准 / 用户可见行为变化是否必须停下 | `pass` |
| `acceptance_criteria_unclear_requires_pause` | behavioral | 验收标准不清时是否必须停下 | `pass` |
| `contract_change_requires_pause` | behavioral | 公共接口 / cross-module contract 变更是否必须停下 | `pass` |
| `ownership_boundary_requires_pause` | behavioral | ownership boundary 不清时是否必须停下 | `pass` |
| `schema_change_requires_pause` | behavioral | schema / migration 是否必须停下 | `pass` |
| `migration_strategy_requires_pause` | behavioral | migration strategy 决策是否必须停下 | `pass` |
| `dependency_or_tooling_change_requires_pause` | behavioral | 依赖 / toolchain / runtime 变更是否必须停下 | `pass` |
| `validation_boundary` | behavioral | 本地验证与外部/真实数据验证的边界是否清楚 | `pass` |
| `manual_or_expensive_validation_requires_pause` | behavioral | 手动 / 高成本验证环境是否必须停下 | `pass` |
| `remote_production_access_requires_pause` | behavioral | 远程生产样环境 / 真实用户数据访问是否必须停下 | `pass` |
| `fast_path_vs_full_workflow` | behavioral | 轻路径与完整链路是否可区分 | `pass` |
| `scoped_tasking_entrypoint` | behavioral | bugfix / unclear-boundary 场景是否先进入 `scoped-tasking` | `pass` |
| `skip_escalation_on_clear_local_work` | behavioral | clear local work 是否默认停留在当前实现链路 | `pass` |
| `multi_file_plan_then_continue` | behavioral | multi-file plan 完成后是否可自动续跑实现链路 | `pass` |
| `design_before_plan_escalation` | behavioral | 多方案 / 公共契约 / 验收不清时是否升级到 `design-before-plan` | `pass` |
| `impact_analysis_escalation` | behavioral | shared model / broad caller impact 时是否升级到 `impact-analysis` | `pass` |
| `review_clean_next_step_continuation` | behavioral | `review_result: clean` 后的明确非破坏性下一步是否可自动继续 | `pass` |
| `fast_path_protocol_optional` | behavioral | fast path 是否可以省略完整 protocol block set | `pass` |
| `task_validation_required_for_skill_chain` | behavioral | non-trivial skill chain 前是否需要 `task-validation` | `pass` |
| `precheck_only_for_real_prerequisite` | behavioral | `precheck` 是否只在真实前置条件下出现 | `pass` |
| `triggered_skill_requires_output_validate_drop` | behavioral | triggered skill 是否需要 `output` / `validate` / `drop` | `pass` |
| `repeated_skill_retry_requires_rescope` | behavioral | 无新证据重复尝试时是否必须停止并 re-scope / escalate / ask | `pass` |
| `release_actions_require_pause` | behavioral | `commit` / `push` / deploy / release 是否必须额外确认 | `pass` |
| `force_push_requires_pause` | behavioral | `force push` 这类 remote destructive 动作是否必须停下 | `pass` |
| `implementation_chain_continuation` | behavioral | 实现后进入 `self-review` / `targeted-validation` 是否可自动衔接 | `pass` |
| `scope_expansion_requires_pause` | behavioral | 执行中超出已接受任务边界时是否必须停下 | `pass` |
| `destructive_action_requires_pause` | behavioral | 破坏性本地动作是否必须停下 | `pass` |
| `overwrite_user_changes_requires_pause` | behavioral | 会覆盖现有用户改动时是否必须停下 | `pass` |
| `bulk_file_moves_require_pause` | behavioral | 批量文件移动 / 布局重组是否必须停下 | `pass` |
| `delegation_bounds` | behavioral | 并行默认值、共享写面与 overflow 规则是否可判定 | `pass` |
| `parallelism_not_automatic` | behavioral | 未显式 opt-in 时并行是否默认关闭 | `pass` |

## Calibration Model

每个 case 都包含 `expect_current`，表示：

- 当前 live 模板应该得到什么结果
- evaluator 本身是否和当前治理模型保持同步

现在的 live suite 目标是：

- 当前模板全部 `PASS`
- 如果出现 `FAIL`，优先怀疑模板或评测用例真的有回归
- 如果出现 `MISCALIBRATED`，优先检查 prompt / judge / `expect_current` 是否没跟上 live 模型
- 如果出现 `ERROR`，优先检查 CLI 可用性、网络/认证状态，或 runner timeout 是否不足

## Protocol Semantics In Scope

这轮 `P2` 首增量没有重写大号 `Skill Protocol`，而是只收敛一组最小、可测的协议语义：

- `trigger / defer / escalate / stop`
- `task-validation`
- `precheck`
- `output / validate / drop`
- repeated retry without new evidence 的最小 loop guard

这些语义的模板落点是：

- `Skill Activation`: `trigger / defer / escalate`
- `Escalation Rules`: `stop`
- `Skill Protocol`: `task-validation`, `precheck`, `output`, `validate`, `drop`, loop guard
- `Common Flow Patterns`: 默认链路、升级链路和自动续跑边界

这轮增量的非目标也应保持明确：

- 不是 parser
- 不是重型 runtime
- 不是历史 `Skill Protocol v1` / `Skill Protocol v2` 的复活
- 不是要求所有 fast path 回复都带完整 protocol block

## Driver Behavior

`run_eval.py` 的关键行为：

- 为每个 CLI 建隔离工作区
- 把模板部署为 `AGENTS.md` 或 `CLAUDE.md`
- 默认 `static` case 跑 3 次、`behavioral` case 跑 5 次
- 用多数票决定 `PASS` / `FAIL`
- preflight 失败时把该 CLI 标为 `SKIPPED`
- 已在当前会话确认 CLI 可用时，可用 `--skip-preflight` 把 suite 结果和 preflight 抖动分开
- 只要有 case 失去 calibration，或出现 `ERROR`，就以非零退出
- `--json` 会输出机器可读 summary，适合被治理健康度快照显式消费；默认文本模式仍保留给维护者直接阅读

## Commands

### Full run

```bash
uv run maintainer/governance_eval/run_eval.py
```

### Current baseline

当前已固化的真实 CLI 基线（2026-05-30 的 33-case cross-CLI）：

- `maintainer/reports/baselines/governance-template-eval-baseline-2026-05-30.md`

这份基线使用的是：

- parallel per-CLI full run
- `--model sonnet --runs 1 --skip-preflight`
- 先做增量 smoke，再固化 full baseline

对应原始 run 记录（按 CLI 并行生成后合并）：

- `maintainer/reports/runs/governance-template-eval-2026-05-30-claude-sonnet.txt`
- `maintainer/reports/runs/governance-template-eval-2026-05-30-cursor-sonnet.txt`
- `maintainer/reports/runs/governance-template-eval-2026-05-30-codex-sonnet.txt`
- `maintainer/reports/runs/governance-template-eval-2026-05-30-sonnet.txt`（合并视图）

### Parallel full run (per CLI)

```bash
uv run maintainer/governance_eval/run_eval.py --cli claude --model sonnet --runs 1 --skip-preflight
uv run maintainer/governance_eval/run_eval.py --cli cursor --model sonnet --runs 1 --skip-preflight
uv run maintainer/governance_eval/run_eval.py --cli codex --model sonnet --runs 1 --skip-preflight
```

### Single case smoke

```bash
uv run maintainer/governance_eval/run_eval.py --case local_continue --runs 1
```

### Single CLI with multiple cases

```bash
uv run maintainer/governance_eval/run_eval.py --cli codex --case local_continue --case scoped_tasking_entrypoint --case fast_path_protocol_optional --case triggered_skill_requires_output_validate_drop --case delegation_bounds --runs 1
```

也可以在一个参数里传逗号分隔的 case 列表：

```bash
uv run maintainer/governance_eval/run_eval.py --cli codex --case local_continue,scoped_tasking_entrypoint,fast_path_protocol_optional,triggered_skill_requires_output_validate_drop,delegation_bounds --runs 1
```

### JSON summary

```bash
uv run maintainer/governance_eval/run_eval.py --cli codex --case local_continue,fast_path_protocol_optional,delegation_bounds --runs 1 --json
```

如果要把行为回归指标纳入治理健康度快照，先单独生成这份 JSON，再显式传给 `check_governance_health.py --eval-json <path>`；默认不要让 deterministic 健康度链隐式重跑 live eval。

### Cheaper model

```bash
uv run maintainer/governance_eval/run_eval.py --model sonnet
```

## How To Update The Live Suite

当治理模板变化时，按这个顺序更新：

1. 先改模板，确认 live contract 真的变了
2. 再改 `cases.yaml`
3. 必要时改 `run_eval.py`
4. 再更新本文档
5. 重新跑单 case smoke；条件允许时再跑 full run

### Keep

- prompt 只依赖 `{{GOVERNANCE_FILE}}`
- judge 表达式尽量简单、可解释
- case 名称直接对应当前治理能力
- 失败能够区分“模板真有问题”与“评测本身没跟上”

### Do Not Keep In The Live Suite

下面这些内容如果还需要保留，只能放到历史说明或基线报告里，不能继续作为 live case 主体：

- `Skill Family Concurrency Budgets`
- `Forward Handoffs` / `Fallbacks`
- 版本化 `Skill Protocol v1` / `Skill Protocol v2` 断言
- phase-system 时代的退役 skill 路由

## Minimal Validation For Maintainers

改完 live suite 后，最小建议检查是：

- 先跑这次新增或改动过的 case；不要把下面这组固定命令当成对新增 case 的替代
- 条件允许时，再补跑一组代表性旧 case，确认没有把已有 judge / prompt 路径带坏

```bash
uv run maintainer/governance_eval/run_eval.py --cli codex --case local_continue,requirements_change_requires_pause,scoped_tasking_entrypoint,fast_path_protocol_optional,task_validation_required_for_skill_chain,precheck_only_for_real_prerequisite,triggered_skill_requires_output_validate_drop,repeated_skill_retry_requires_rescope,delegation_bounds,parallelism_not_automatic --runs 1
```

如果本地凭据、模型权限或 CLI 信任配置不可用，至少要做：

- prompt / judge 静态复核
- `run_eval.py` 代码路径自检
- 在执行记录里明确写下阻塞原因

## Relationship To Other Checks

- 模板改动后要先看投影是否没断：`python3 maintainer/scripts/install/run_manage_governance_smoke.py`
- 要看模板与根文件是否同步：`python3 maintainer/scripts/analysis/check_governance_sync.py`
- 要看文档与 skill 引用是否完好：`python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken`
- `.github/workflows/ci.yml` 已把 `sync + smoke + cross-ref` 提升为治理相关路径变更时的 deterministic CI gate
- live evaluator 仍保留为 authenticated maintainer lane，不放进公共 CI

不要用 live evaluator 去替代这些检查；它只负责“模板语义能不能被 agent 正确读出来”。
