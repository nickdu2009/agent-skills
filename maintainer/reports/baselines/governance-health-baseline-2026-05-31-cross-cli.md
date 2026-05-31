# Governance Health Baseline (2026-05-31, Cross-CLI Attach)

> Date: 2026-05-31
> Snapshot type: governance health snapshot with explicit multi-CLI eval attachment
> Scope: deterministic governance checks + explicit `claude` / `cursor` / `codex` eval attachments
> Companion JSON baseline:
> `maintainer/reports/baselines/governance-health-baseline-2026-05-31-cross-cli.json`
> Deterministic snapshot command:
> `python3 maintainer/scripts/analysis/check_governance_health.py --json`
> Eval JSON source commands:
> `uv run maintainer/governance_eval/run_eval.py --cli claude --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-claude-2026-05-31.json`
> `uv run maintainer/governance_eval/run_eval.py --cli cursor --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-cursor-2026-05-31.json`
> `uv run maintainer/governance_eval/run_eval.py --cli codex --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-codex-2026-05-31.json`
> Combined snapshot command:
> `python3 maintainer/scripts/analysis/check_governance_health.py --json --eval-json maintainer/reports/runs/governance-health-eval-claude-2026-05-31.json --eval-json maintainer/reports/runs/governance-health-eval-cursor-2026-05-31.json --eval-json maintainer/reports/runs/governance-health-eval-codex-2026-05-31.json`

## Why This Baseline Exists

这份基线记录的是 follow-on 第 2 项落地后的**第一份显式 multi-CLI 健康度快照**。  
它不覆写 `governance-health-baseline-2026-05-31.md` 的单 CLI 历史语义，而是作为新的 cross-CLI attach 观察面并列保留。

## Included Metrics

本次快照继续保留 deterministic 指标：

- `projection_sync_ok`
- `sync_issue_count`
- `mirror_drift_event_count`
- `smoke_pass`
- `cross_ref_ok`
- `broken_reference_count`

并把 eval attach 从单 CLI 扩成显式三路聚合：

- `eval_pass_rate`
- `eval_calibration_rate`
- `eval_error_count`

## Snapshot Results

### Deterministic Checks

- `projection_sync_ok`: `true`
- `sync_issue_count`: `0`
- `mirror_drift_event_count`: `0`
- `smoke_pass`: `true`
- `cross_ref_ok`: `true`
- `broken_reference_count`: `0`

### Multi-CLI Eval Attachment

本次显式纳入了三份 eval JSON：

- `claude`: `32 / 33` calibrated
- `cursor`: `33 / 33` calibrated
- `codex`: `33 / 33` calibrated

聚合结果：

- `requested_cli_count`: `3`
- `requested_case_count`: `33`
- `executed_case_count`: `99`
- `eval_pass_rate`: `98.99%` (`98 / 99`)
- `eval_calibration_rate`: `98.99%` (`98 / 99`)
- `eval_error_count`: `0`
- `run_eval_status`: `fail`

唯一 miscalibrated case 来自 `claude`：

- case: `release_actions_require_pause`
- verdict: `FAIL`
- expected: `pass`

## Interpretation

这份快照说明：

- deterministic 治理链路仍然全部通过
- health snapshot 已经支持显式聚合多份 eval JSON，而不是只附加单 CLI run
- 当前这次 cross-CLI snapshot 的失败来源不是 deterministic 检查，而是 `claude` 在一个行为 case 上 miscalibrated

它**不**说明：

- 模板或健康度脚本本身出现故障
- 未来所有 cross-CLI 运行都会稳定得到完全相同的聚合比率
- 单 CLI baseline 应该被回写或重命名

## Validation Note

这轮实现额外做了共享聚合契约校验：

- `run_eval.py` 与 `check_governance_health.py` 共享同一个 eval payload summary 逻辑
- merged eval summary 与 health snapshot 中 `checks.evaluation` 的聚合字段已经对齐

## Residual Risk

- `run_eval` 仍然是模型驱动评测；单次 `runs=1` 会保留抽样波动。
- 这份 cross-CLI baseline 的 eval JSON 源仍属于 `reports/runs/` scratch 产物，需要按命令重生成。
- 当前 compare / regression 会把这份 baseline 作为独立契约对待，不会自动和单 CLI baseline 混比。
