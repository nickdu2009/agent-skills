# Manual And Repo Development

**Status**: Current authority
**Current implementation note**: This guide reflects the current repo-maintainer workflow and the post-2026-05 governance model. Planning examples should follow `AGENTS.md` / `CLAUDE.md` Behavioral Guidelines, not retired planning skills.

## Scope

这篇文档面向正在开发 `agent-skills` 仓库本身的人，而不是把这套 skills 接入外部项目的普通使用者。

这里集中放三类内容：

- `docs/manual/` 的本地预览方式
- 当前仓库的静态校验与安装冒烟
- 与当前仓库维护直接相关的工作流示例

## Manual Preview

这套手册可以单独本地预览，不需要把整个仓库文档一起挂起来。

```bash
make docs-manual-serve
```

如果你想改端口：

```bash
make docs-manual-serve PORT=3001
```

如果你想预览维护者文档：

```bash
make docs-maintainer-serve
```

如果你想改端口：

```bash
make docs-maintainer-serve PORT=3001
```

## Canonical Source

`skills/` 是唯一 canonical source。

这意味着：

- 每个 skill 只在一个正式位置维护
- 仓库内不再维护 repo-local `.cursor/skills/` 或 `.claude/skills/`
- `.cursor/`、`.claude/` 等目录不应被当成正式源头继续手工维护

如果出现不一致，默认以 `skills/` 为准。

## Repository Validation

### 何时使用

适合以下场景：

- 你刚改了 `SKILL.md` 或相关文档，想先做静态完整性检查
- 你刚改了安装器或治理模板，想做一次安装冒烟
- 你需要确认 canonical `skills/` 树和相关文档引用仍然一致

### 常用检查

```bash
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
python3 maintainer/scripts/install/run_manage_governance_smoke.py
```

### 改治理模板时的固定顺序

如果这次改动落在 `templates/governance/`、根 `AGENTS.md` / `CLAUDE.md`，或治理评测/投影链路，按下面顺序检查：

```bash
python3 maintainer/scripts/analysis/check_governance_sync.py
python3 maintainer/scripts/install/run_manage_governance_smoke.py
uv run maintainer/governance_eval/run_eval.py --cli codex --case local_continue,scoped_tasking_entrypoint,fast_path_protocol_optional,task_validation_required_for_skill_chain,precheck_only_for_real_prerequisite,triggered_skill_requires_output_validate_drop,repeated_skill_retry_requires_rescope,delegation_bounds,parallelism_not_automatic --runs 1
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
```

说明：

- `check_governance_sync.py` 检查模板与仓库根治理文件的共享正文是否同步
- `check_governance_sync.py` 也会检查两份治理模板除顶部 mirror 注释外是否仍保持正文镜像；如果未来真要引入平台差异，先更新约束与校验，再改模板
- `run_manage_governance_smoke.py` 检查安装投影链路是否仍可生成预期治理文件
- `governance_eval/run_eval.py` 是 authenticated maintainer lane；先跑这次新增/改动的 case，再用上面的组合命令做一轮代表性回归 smoke
- `check_cross_references.py` 检查文档与 skill 引用是否仍然完整
- `.github/workflows/ci.yml` 现在会在治理相关路径变更时自动 gate `sync + smoke + cross-ref`；behavior eval 仍保留在本地维护者链路，不放进公共 CI

### 治理健康度快照

治理健康度首增量只做**单次运行快照**，默认汇总 deterministic 检查：

```bash
python3 maintainer/scripts/analysis/check_governance_health.py --json
```

如果要和已晋升 baseline 做 regression / compare，使用 companion JSON：

```bash
python3 maintainer/scripts/analysis/compare_governance_health_baseline.py \
  --baseline maintainer/reports/baselines/governance-health-baseline-2026-05-31.json \
  --current maintainer/reports/runs/governance-health-current.json
```

如果本次需要把行为回归指标一起记进健康度快照，先单独生成一个或多个 eval JSON，再显式传入：

```bash
uv run maintainer/governance_eval/run_eval.py --cli codex --case local_continue,fast_path_protocol_optional,delegation_bounds --runs 1 --json > maintainer/reports/runs/governance-health-eval-smoke.json
python3 maintainer/scripts/analysis/check_governance_health.py --json --eval-json maintainer/reports/runs/governance-health-eval-smoke.json
```

如果这次要做 cross-CLI attach，就按 CLI 各自产出 JSON，再重复传 `--eval-json`：

```bash
uv run maintainer/governance_eval/run_eval.py --cli claude --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-claude.json
uv run maintainer/governance_eval/run_eval.py --cli cursor --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-cursor.json
uv run maintainer/governance_eval/run_eval.py --cli codex --model sonnet --runs 1 --skip-preflight --json > maintainer/reports/runs/governance-health-eval-codex.json
python3 maintainer/scripts/analysis/check_governance_health.py --json \
  --eval-json maintainer/reports/runs/governance-health-eval-claude.json \
  --eval-json maintainer/reports/runs/governance-health-eval-cursor.json \
  --eval-json maintainer/reports/runs/governance-health-eval-codex.json
```

默认不要让健康度脚本隐式重跑 live eval；保持 deterministic 检查与 authenticated maintainer lane 分层。
如果把 attach 范围从单 CLI 扩成 cross-CLI，应该晋升新的 baseline 文件，而不是直接覆写旧 baseline。

### Repo Overlay Contract

仓库根 `AGENTS.md` / `CLAUDE.md` 允许保留少量 repo-only overlay，但必须满足：

- 只出现在根文件，不写回模板
- 用 `repo-overlay` 注释块显式标记
- 每一块 overlay 都能说清楚“为什么只属于本仓库”
- 修改模板共享正文时，不要顺手改动未标记的根文件内容

### 如果静态检查失败怎么办

先回到 canonical `skills/` 树和相关文档引用本身，不要尝试在仓库里补一层本地镜像来掩盖问题。  
修正源内容后，再重新运行静态检查或安装冒烟。

## Repository Workflows

下面这些示例适合开发当前仓库时参考，不属于普通使用者手册主线。

### 给单个 Skill 补边界说明

- 任务场景：你发现 `skills/scoped-tasking/SKILL.md` 的边界解释还不够直观，想补一小段更贴近仓库实际用法的说明。
- 执行顺序：
  1. 把范围压到一个目标 skill 文件。
  2. 在编辑前先说清楚这次只补什么。
  3. 按最小改动补充文字，沿用仓库里已经存在的概念。
  4. 自检新增内容是否和相关手册章节保持一致。
- 结束信号：
  - 改动仍然只落在一个 skill 文件
  - 新增说明已经能帮助使用者区分边界
  - 不需要连带修改其他 skill 或手册章节

### 先判断安装说明该改在哪一章

- 任务场景：使用者仍分不清 `install user` 和 `install project` 的区别，但你还不确定真正 edit point 在 `docs/manual/QUICK-START.md`、`docs/manual/INSTALLATION.md` 还是 `docs/manual/TROUBLESHOOTING.md`。
- 执行顺序：
  1. 先看 `docs/manual/QUICK-START.md` 的首次上手路径。
  2. 再看 `docs/manual/INSTALLATION.md` 的安装路径分工。
  3. 只在必要时再看 `docs/manual/TROUBLESHOOTING.md`。
  4. 一旦主 edit point 清楚，就停止继续扩展并进入计划阶段。
- 结束信号：
  - 已经能说清楚主 edit point 属于哪一章
  - 其他章节最多只是对照或交叉引用
  - 下一步已经从“继续找”变成“准备做单点修改”

### 修正 `examples/` 里的 Skill 引用

- 任务场景：`examples/` 中某个场景文档引用了不存在的 skill 名称，或者名字和 `skills/` 目录中的真实名称对不上。
- 执行顺序：
  1. 先把症状说清楚。
  2. 以 `skills/` 目录作为基线，确认真实存在的 skill 名称。
  3. 只修确认错误的引用，不顺手重写整个示例。
  4. 定向复查改后的每个名字都能在 `skills/` 对上。
- 结束信号：
  - 每个改动都有 `skills/` 目录中的真实名称作证据
  - 示例文档的结构和任务意图没有被顺手改写
  - 目标引用已经和仓库里的真实 skill 名称一致

### 整理手册目录页的导航结构

- 任务场景：`docs/manual/README.md` 的入口仍然偏散，想把导航结构整理得更清楚，同时不改变已有章节顺序、不删除现有链接。
- 执行顺序：
  1. 先确认这次目标是整理结构，而不是重写手册内容本身。
  2. 明确不变条件，例如章节文件名、阅读顺序和已有入口不变。
  3. 只在 `docs/manual/README.md` 内做局部收拢。
  4. 自查是否引入了重复说明、遗漏链接或改变了原有阅读逻辑。
- 结束信号：
  - 导航结构更清楚了，但章节内容和阅读顺序没有被改写
  - 所有既有入口仍然有效，没有丢链接
  - 改动仍然局限在导航层

### 一条线补阅读路径图，一条线补工作流案例

- 任务场景：你想同时增强手册的“怎么读”和“怎么用”两部分内容，一条线处理 `docs/manual/README.md`，一条线处理 `docs/manual/COMMON-WORKFLOWS.md`。
- 推荐 skill 组合：治理里的规划纪律（`AGENTS.md` / `CLAUDE.md` Behavioral Guidelines） + `multi-agent-protocol` + `targeted-validation`
- 执行顺序：
  1. 先判断这两项工作是否低耦合。
  2. 把工作拆成两条独立子线，避免交叉编辑。
  3. 每条子线独立完成自己的文档增强。
  4. 集成时统一检查术语、章节顺序和入口逻辑。
- 结束信号：
  - 两条子线的结果能直接汇总
  - 术语、章节顺序和入口逻辑保持一致
  - 集成后没有引入重叠编辑
