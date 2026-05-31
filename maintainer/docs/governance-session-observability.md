# Governance Session Observability

## Purpose

这份文档定义治理后续第 3 项的最小观测面：  
不用真实线上遥测，也不把健康度脚本升级成新的调度器，而是在仓库内维护一套**带 gold label 的 curated decision points**，稳定产出两项 follow-on 指标：

- `extra_confirmation_rate`
- `routing_misjudgment_rate`

## What This Is

当前实现不是“真实生产会话统计”，而是一个**可重复运行的会话观察层**：

- 观测样本保存在 `maintainer/governance_observability/decision_points.yaml`
- 每个 decision point 记录一段会话摘录、所属指标口径和 gold label
- runner `maintainer/governance_observability/run_observability_eval.py` 用同一套规则对这些样本重新打分

这样做的目标，是先把“什么算额外确认、什么算 routing 误判”写清楚，并让维护者能重复验证，而不是直接声称已经拥有真实长期趋势。

## Metric Definitions

### Extra Confirmation Rate

`extra_confirmation_rate` 的定义是：

- 分母：`should_ask_user = false` 的 decision points
- 分子：assistant 仍然显式向用户追问确认的 points

这对应的是“本可继续，但 agent 多问了一次”。

### Routing Misjudgment Rate

`routing_misjudgment_rate` 的定义是：

- 分母：`metric = routing` 的 decision points
- 分子：缺失 `expected_skills` 或命中了 `forbidden_skills` 的 points

这对应的是“该触发的没触发，或不该升级的被升级了”。

## Dataset Contract

`decision_points.yaml` 当前采用最小 schema：

- `id`
- `metric`: `extra_confirmation` 或 `routing`
- `transcript_excerpt`
- `should_ask_user`（仅 extra confirmation）
- `expected_skills` / `forbidden_skills`（仅 routing）

这套数据集要求：

- 至少覆盖 20 个 decision points
- 同时覆盖“应继续”“应停下确认”“应触发 skill”“不应过度升级”四类情况
- 允许 mixed fixtures，也就是既有符合治理预期的样本，也有故意保留的负样本

## Entrypoint

```bash
uv run maintainer/governance_observability/run_observability_eval.py --json
```

输出包含：

- 总 decision point 数
- `extra_confirmation_rate`
- `missed_required_confirmation_count`
- `routing_misjudgment_rate`
- 每个 point 的逐项判定结果

## Relationship To Existing Eval

这层观测面和 `maintainer/governance_eval/` 的关系是：

- `governance_eval` 仍然负责模板行为回归
- `governance_observability` 负责把“额外确认”和“routing 误判”拆成独立口径
- `from_governance_eval_map.yaml` 只做 closest-case traceability，不让两套数据强耦合，也不要求一一精确同构

## Non-Goals

当前实现明确不做：

- 真实线上 telemetry
- 自动抓取全部 agent transcripts
- 把 observability runner 默认并入公共 CI
- 用这套 curated 数据替代健康度快照中的 deterministic 指标

## Refresh Rules

- 改动治理模板中 continue / ask / stop / routing 语义时，应同步复核 `decision_points.yaml`
- 如果修改了 runner 规则，应重跑观测基线并更新对应 baseline 文档
- 需要新增样本时，优先补 decision point，而不是临时改 metric 定义
