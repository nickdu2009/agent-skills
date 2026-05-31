# Governance Health Baseline (2026-05-31)

> Date: 2026-05-31
> Snapshot type: single-run governance health snapshot
> Scope: deterministic governance checks + explicit codex eval attachment
> Deterministic snapshot command:
> `python3 maintainer/scripts/analysis/check_governance_health.py --json`
> Companion JSON baseline:
> `maintainer/reports/baselines/governance-health-baseline-2026-05-31.json`
> Eval JSON source command:
> `uv run maintainer/governance_eval/run_eval.py --cli codex --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-codex-2026-05-31.json`
> Combined snapshot command:
> `python3 maintainer/scripts/analysis/check_governance_health.py --json --eval-json maintainer/reports/runs/governance-health-eval-codex-2026-05-31.json`
> Compare command:
> `python3 maintainer/scripts/analysis/compare_governance_health_baseline.py --baseline maintainer/reports/baselines/governance-health-baseline-2026-05-31.json --current maintainer/reports/runs/governance-health-current.json`

## Why This Baseline Exists

这份基线记录 `P2` 治理健康度指标首增量的**第一份单次运行快照**。  
它的目标不是替代模板、sync lint、安装 smoke 或 live evaluator，而是把当前已经稳定存在的治理检查结果收敛成一个可复用的健康度观察面。

从这一轮开始，Markdown 基线旁边维护**同名 companion JSON**，用于做机器 compare / regression；Markdown 继续承担人类可读解释，JSON 负责稳定比较契约。

## Included Metrics

本次快照只包含首增量承诺的可机器统计指标：

- `projection_sync_ok`
- `sync_issue_count`
- `mirror_drift_event_count`
- `smoke_pass`
- `cross_ref_ok`
- `broken_reference_count`
- `eval_pass_rate`
- `eval_calibration_rate`
- `eval_error_count`

这些值都属于**单次运行快照**，不是跨时间趋势统计。

## Snapshot Results

### Deterministic Checks

- `projection_sync_ok`: `true`
- `sync_issue_count`: `0`
- `mirror_drift_event_count`: `0`
- `smoke_pass`: `true`
- `cross_ref_ok`: `true`
- `broken_reference_count`: `0`

### Eval Attachment

本次显式纳入了一份 eval JSON：

- source: local scratch run `maintainer/reports/runs/governance-health-eval-codex-2026-05-31.json`（不随仓库长期保留；需要按文档命令重生成）
- CLI scope: `codex`
- case scope: current full 33-case live suite
- run mode: `--model sonnet --runs 1 --skip-preflight --json`

结果：

- `eval_status`: `included`
- `eval_pass_rate`: `100%` (`33 / 33`)
- `eval_calibration_rate`: `100%` (`33 / 33`)
- `eval_error_count`: `0`

## Interpretation

这份快照说明：

- 当前模板投影链路、安装 smoke、引用完整性检查都处于通过状态
- 当前 mirror drift 事件数为 `0`
- 在显式附加的 codex 33-case eval JSON 上，行为回归通过率与 calibration 率都为 `100%`

它**不**说明：

- 真实会话里的额外确认率已经下降
- routing 误判率已经有长期趋势结论
- 任何未来时间点都会自动保持同样结果

## Deferred Metrics

路线图里还列出两项后续指标，但这份首增量基线没有伪造它们的机器值：

- 额外确认率是否下降
- routing 误判率是否下降

如果后续要落地，必须先补新的观测面和口径，而不是把当前 snapshot 直接包装成长期趋势指标。

## Residual Risk

- 这份首版健康度基线的 eval 部分只附加了一条 `codex` full-suite JSON run，不代表 cross-CLI 长期趋势。
- deterministic 健康度默认不隐式重跑 live eval；如果后续维护者没有显式提供新的 eval JSON，健康度快照会只保留 deterministic 指标。
- `maintainer/reports/runs/` 仍是 scratch 区；只有明确要保留的快照或结论才应晋升到 `maintainer/reports/baselines/`。
