# Governance Health Metrics

## Purpose

这份文档定义 `P2` 治理健康度指标首增量的最小口径。  
它的目标不是引入新的治理真相源，而是把现有治理检查和评测结果汇总成一份**单次运行快照**，帮助维护者判断当前治理面是否健康。

## First Increment Scope

首增量只承诺输出当前已经有稳定数据源的指标：

- `projection_sync_ok`
- `sync_issue_count`
- `mirror_drift_event_count`
- `smoke_pass`
- `cross_ref_ok`
- `broken_reference_count`
- `eval_pass_rate`（仅在显式提供 eval JSON 时）
- `eval_calibration_rate`（仅在显式提供 eval JSON 时）
- `eval_error_count`（仅在显式提供 eval JSON 时）

这些值都是**单次运行快照**，不是长期趋势引擎，也不直接回答“是否下降”。

## Data Sources

首增量只消费现有入口：

- `python3 maintainer/scripts/analysis/check_governance_sync.py --json`
- `python3 maintainer/scripts/install/run_manage_governance_smoke.py`
- `python3 maintainer/scripts/analysis/check_cross_references.py --json`
- `uv run maintainer/governance_eval/run_eval.py --json`（可选；结果文件通过 `--eval-json` 显式传给健康度脚本）

默认健康度汇总不应隐式重跑 live eval。  
这是为了保持 deterministic 检查与 authenticated maintainer lane 的分层，避免把健康度脚本做成新的隐式调度器。

## Entrypoint

首增量的汇总入口是：

```bash
python3 maintainer/scripts/analysis/check_governance_health.py --json
```

如果要把某次快照和已晋升的 baseline 做 regression / compare，使用 companion JSON：

```bash
python3 maintainer/scripts/analysis/compare_governance_health_baseline.py \
  --baseline maintainer/reports/baselines/governance-health-baseline-2026-05-31.json \
  --current maintainer/reports/runs/governance-health-current.json
```

当 baseline 和 current 都包含 eval attach 时，compare 会按完整 scope 元数据判断兼容性，例如：

- `requested_cli_names`
- `requested_case_ids`
- `runs_override`
- `model_override`
- `skip_preflight`

只有 scope 兼容时才比较 eval rates；否则产出 `warn` 并跳过 eval rate regression 判断。

如果要把 eval 指标纳入同一份快照，先单独生成一个或多个 eval JSON，再显式传入：

```bash
uv run maintainer/governance_eval/run_eval.py --cli codex --case local_continue,fast_path_protocol_optional,delegation_bounds --runs 1 --json > maintainer/reports/runs/governance-health-eval-smoke.json
python3 maintainer/scripts/analysis/check_governance_health.py --json --eval-json maintainer/reports/runs/governance-health-eval-smoke.json
```

如果要显式聚合多 CLI attach，分别产出每个 CLI 的 JSON，再重复传 `--eval-json`：

```bash
uv run maintainer/governance_eval/run_eval.py --cli claude --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-claude.json
uv run maintainer/governance_eval/run_eval.py --cli cursor --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-cursor.json
uv run maintainer/governance_eval/run_eval.py --cli codex --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-codex.json
python3 maintainer/scripts/analysis/check_governance_health.py --json \
  --eval-json maintainer/reports/runs/governance-health-eval-claude.json \
  --eval-json maintainer/reports/runs/governance-health-eval-cursor.json \
  --eval-json maintainer/reports/runs/governance-health-eval-codex.json
```

## Refresh Rules

- 改动治理模板、根治理投影、治理分析脚本、安装 smoke、治理 evaluator 时，应重跑 deterministic 健康度快照。
- 只有在本次增量确实需要记录行为回归健康度时，才显式补跑 eval JSON。
- `reports/runs/` 放 scratch JSON；只有明确要保留的稳定健康度结论才晋升到 `reports/baselines/`。
- 已晋升的健康度 baseline 应同时保留 Markdown 解释和 companion JSON；compare 只以 JSON 为机器契约，不再从 Markdown 反解析指标。
- 如果 eval attach 的范围从单 CLI 扩到 multi-CLI，应晋升**新的 baseline 文件**，不要覆写旧 baseline 的历史语义。

## Deferred Metrics

下面两项仍是路线图目标，但不在首增量里伪造机器值：

- 额外确认率是否下降
- routing 误判率是否下降

如果后续要落地，必须先定义新的观测面和口径，而不是把现有 evaluator 结果直接包装成“真实会话指标”。

当前 follow-on 已补了一层独立观测面，见 [`governance-session-observability.md`](governance-session-observability.md)。  
它提供 curated decision-point runner，但仍然不是健康度首增量里的默认 deterministic 指标。

## Non-Goals

首增量明确不做：

- 新的长期运行服务
- dashboard 或重型 runtime
- 为指标目的而重写治理模板语义
- 把 skill/token 审计体系混进 governance 健康度主线
- 让健康度脚本成为新的治理真相源
