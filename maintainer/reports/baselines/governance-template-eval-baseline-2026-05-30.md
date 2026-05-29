# Governance Template Eval Baseline (2026-05-30)

> Date: 2026-05-30
> Evaluator: automated via `maintainer/governance_eval/run_eval.py`
> Command: `uv run maintainer/governance_eval/run_eval.py --model sonnet --runs 1`
> Templates under test: `templates/governance/AGENTS-template.md`, `templates/governance/CLAUDE-template.md`
> Live case catalog: `maintainer/governance_eval/cases.yaml` (8 cases)
> Raw run: `maintainer/reports/runs/governance-template-eval-2026-05-30-sonnet.txt`
> Previous baseline: none

## Why This Baseline Exists

这份基线记录的是 template-first 治理第一增量完成后的首次真实 CLI 对齐结果。  
它不是安装 smoke，也不是静态引用检查，而是验证三类 agent CLI 在隔离工作区里是否都能从治理模板中读出同一套 live contract。

这份基线的目标是给后续回归一个稳定参照：

- 模板继续/停下边界是否仍然可判定
- 当前 live case catalog 是否仍和模板同步
- Claude / Cursor / Codex 三侧是否在同一组治理样例上保持一致

## Validation Performed

- 单 case reruns while stabilizing `activation_paths`
- `uv run maintainer/governance_eval/run_eval.py --case local_continue --runs 1`
- `uv run maintainer/governance_eval/run_eval.py --case delegation_bounds --runs 1`
- `uv run maintainer/governance_eval/run_eval.py --case activation_paths --runs 1`
- `uv run maintainer/governance_eval/run_eval.py --case schema_change_requires_pause --runs 1`
- full cross-CLI run:
  `uv run maintainer/governance_eval/run_eval.py --model sonnet --runs 1`

相关闭环检查在同一轮变更里也已通过：

- `python3 maintainer/scripts/analysis/check_governance_sync.py`
- `python3 maintainer/scripts/install/run_manage_governance_smoke.py`
- `python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken`

## Change Made Before Baseline

在固化这份基线前，对 live evaluator 做了两类对齐：

1. 将 `maintainer/governance_eval/cases.yaml` 从 pre-2026-05 的历史术语切换到当前 live 治理模型  
   旧的 `Skill Family Concurrency Budgets`、`Forward Handoffs` / `Fallbacks`、版本化 `Skill Protocol v1` / `Skill Protocol v2` 断言不再作为 live suite 主路径。
2. 收紧 `activation_paths` case 的 prompt  
   改为针对固定 live skill 集合检查显式 activation path，避免不同 CLI 把工作流词误识别成 skill，导致跨模型不稳定。

## Full Results

| Case ID | Claude (`sonnet`) | Cursor (`claude-4.6-sonnet-medium`) | Codex (`gpt-5.4`) |
|---|---|---|---|
| `activation_paths` | pass | pass | pass |
| `local_continue` | pass | pass | pass |
| `contract_change_requires_pause` | pass | pass | pass |
| `schema_change_requires_pause` | pass | pass | pass |
| `validation_boundary` | pass | pass | pass |
| `fast_path_vs_full_workflow` | pass | pass | pass |
| `implementation_chain_continuation` | pass | pass | pass |
| `delegation_bounds` | pass | pass | pass |

## Overall Decision

### By CLI

- Claude: `8 pass`, `0 fail`, `0 miscalibrated`
- Cursor: `8 pass`, `0 fail`, `0 miscalibrated`
- Codex: `8 pass`, `0 fail`, `0 miscalibrated`

### Baseline status

这份 governance template baseline 是 **pass**。  
当前 live evaluator、当前模板、以及三类真实 CLI 环境在 8 个 live cases 上达成完全一致的 calibrated 结果。

## Residual Risk

- 这份基线使用的是 `--model sonnet`，不是 Claude 侧默认 `opus` 路径；在本机环境里，`sonnet` 是当前可稳定复现的真实 run 入口。
- `run_eval.py` 目前保存的是文本型 raw run，而不是结构化 JSON 报告；后续如果要做更细粒度 diff，对机器可读性仍有提升空间。
- 当前 live suite 已覆盖模板第一增量的关键边界，但还没有把 dependency/tooling 变更、commit/push/deploy 等 stop 条件全部转成 live cases。

## Follow-Up Actions

- 把这份 baseline 作为后续治理模板回归的首个对照样本。
- 后续新增 live cases 时，先跑单 case smoke，再和本 baseline 做比较。
- 如果默认模型映射或 CLI 行为发生变化，重新生成 baseline，不要直接改写本文件结论。
