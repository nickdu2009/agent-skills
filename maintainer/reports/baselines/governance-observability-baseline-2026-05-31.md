# Governance Session Observability Baseline (2026-05-31)

> Date: 2026-05-31
> Snapshot type: curated decision-point observability snapshot
> Dataset: `maintainer/governance_observability/decision_points.yaml`
> Runner command:
> `uv run maintainer/governance_observability/run_observability_eval.py --json > maintainer/reports/runs/governance-observability-2026-05-31.json`

## Why This Baseline Exists

这份基线记录的不是生产真实遥测，而是 follow-on 第 3 项落地后的第一份**可重复运行的 session observability 快照**。  
它的作用是把“额外确认”和“routing 误判”拆成独立、带 gold label 的观测面，避免直接把现有 evaluator 包装成真实会话趋势。

## Dataset Summary

- decision point count: `26`
- extra-confirmation denominator (`should_ask_user = false`): `6`
- required-confirmation points (`should_ask_user = true`): `6`
- routing points: `14`

数据集同时包含正样本和负样本，因此这份基线的 rate 反映的是**当前 curated observation set 的命中情况**，不是生产环境总体比例。

## Snapshot Results

- `extra_confirmation_rate`: `33.3%` (`2 / 6`)
- `missed_required_confirmation_count`: `1 / 6`
- `routing_misjudgment_rate`: `35.7%` (`5 / 14`)

## Interpretation

这份快照说明：

- 当前仓库内已经有一套独立于健康度首增量的会话观测层
- `extra_confirmation_rate` 只统计“本可继续但多问了一次”的点，不把“本应 ask 但没 ask”混进同一个分子
- `routing_misjudgment_rate` 会同时捕获“该触发的没触发”“不该升级却升级了”，以及 review-loop 的最小断链症状

它**不**说明：

- 这些比例已经代表真实线上长期趋势
- 当前任何一个 CLI 在真实会话里的确认率或误路由率就是这组数字
- health snapshot 默认已经纳入这些 follow-on 指标

## Traceability

- 观测样本：`maintainer/governance_observability/decision_points.yaml`
- 与现有 evaluator 的弱关联映射：`maintainer/governance_observability/from_governance_eval_map.yaml`
- 运行脚本：`maintainer/governance_observability/run_observability_eval.py`

## Residual Risk

- 这套数据仍是 curated fixtures，不是自动采集的真实 transcripts。
- 当前 detector 依赖显式语言信号与 skill 名称字符串；现在还额外依赖 `review_result` / `drop` / `修订` 这类最小 review-loop 信号，后续如果 transcript 风格变化，需要连带更新 runner 规则。
- 这份 baseline 适合作为 follow-on regression 起点，不适合作为产品级 KPI。
