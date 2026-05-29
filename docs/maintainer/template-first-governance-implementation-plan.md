# Template-First Governance Implementation Plan

**Status**: Partial implementation
**Implementation note**: The PR1-PR3 slice described in this plan is now implemented in the working tree. This document remains as the execution contract and maintenance record for that first increment; it does not claim that the later `P2` consolidation work is finished.

> 配套路线路图：`docs/maintainer/template-first-governance-roadmap.md`
>  
> 本计划只做“怎么实施”，不重复“为什么要 template-first”。如与路线图或治理分层文档冲突，以：
> 1. `skill-and-governance-architecture.md` 的边界定义  
> 2. `template-first-governance-roadmap.md` 的优先级与目标  
> 为准。

## 1. 范围与依据

### 1.1 范围

本次实施计划只覆盖路线图中的第一批可执行工作：

- 在现有模板 section 内补全 `continue` / `ask` / `must stop` 的治理边界
- 保持 `AGENTS-template.md` 与 `CLAUDE-template.md` 镜像一致
- 更新仓库根 `AGENTS.md` / `CLAUDE.md` 的共享治理正文，同时保留 repo-specific overlay
- 为治理模板新增或收敛隔离工作区下的行为回归用例
- 加固安装 smoke 与治理同步检查，使模板改动能触发下游验证
- 给维护者补一条固定的模板改动验证链

### 1.2 不在范围

- 新增 skill、拆分 skill 或修改 `skills/` canonical source
- 重写 `Skill Protocol` 为新版本
- 引入新的顶层模板 section
- 把治理主线与 skill 写作优化（chain alias、contract template）混在同一增量
- 引入重型 workflow runtime、图状态机或新的长期运行服务

### 1.3 关键依据

| 依据 | 本计划使用方式 |
|---|---|
| `docs/maintainer/skill-and-governance-architecture.md` | 确认模板是治理权威、生成结果不是模板源 |
| `docs/maintainer/template-first-governance-roadmap.md` | 提供 `P0` / `P1` / `P2` 优先级和阶段目标 |
| `docs/maintainer/low-intervention-agent-workflow.md` | 提供“默认继续 / 风险升级才停下”的目标行为 |
| `docs/maintainer/manual-and-repo-development.md` | 约束 `skills/` canonical source 与 maintainer 工作流 |
| `maintainer/docs/governance-template-eval.md` | 提供隔离工作区治理评测的执行模型 |
| `maintainer/scripts/install/run_manage_governance_smoke.py` | 现有安装 smoke 入口 |
| `maintainer/scripts/analysis/check_governance_sync.py` | 现有模板/根文件同步检查入口 |

## 2. 当前实现约束

在真正拆任务前，先固定几个仓库现实约束：

1. `templates/governance/AGENTS-template.md` 与 `templates/governance/CLAUDE-template.md` 是共享治理源  
   任何治理正文改动都必须先落模板，再处理投影与验证。
2. 仓库根 `AGENTS.md` / `CLAUDE.md` 不是模板源，但也不是纯自动生成物  
   当前它们包含 repo-specific overlay，至少包括：
   - `Behavioral Guidelines` 中的项目特定规则
   - `Validation Rules` 中的临时项目安装测试说明
3. `maintainer/governance_eval/` 已经存在隔离工作区治理评测能力  
   模板行为回归不应退回到“在整个仓库内直接跑 agent”。
4. `run_manage_governance_smoke.py` 与 `check_governance_sync.py` 已覆盖一部分投影与同步校验  
   本次应在现有入口上增强，而不是平行再造新工具。
5. 当前 `maintainer/governance_eval/` 与 `maintainer/docs/governance-template-eval.md` 仍带有 pre-2026-05 的历史术语与 case 设计  
   `PR 2` 不能只“追加新样例”，还必须先把 live suite 收敛到当前治理模型，再继续扩 case。

## 3. 实施目标

第一增量完成后，应同时满足下面 5 个结果：

1. 模板能直接表达 `default continue`、`must ask`、`must stop`
2. 维护者能指出这些规则分别落在哪些现有 template sections
3. 隔离工作区下的治理行为回归能验证至少 8 到 12 个代表性样例
4. 安装 smoke 与 sync lint 会在模板投影漂移时失败
5. 维护者文档明确给出“改模板后该跑哪些检查”的固定顺序

## 4. 总体路线

### 4.1 里程碑

```text
M1: PR 1 合并 → 模板中的 continue / ask / stop 边界落地
M2: PR 2 合并 → 隔离工作区行为回归覆盖新边界
M3: PR 3 合并 → 安装 smoke / sync lint / 维护者验证链完成闭环
M4: 集成验证通过 → 路线图可从纯 proposal 进入 partial implementation
```

### 4.2 PR 依赖图

```text
PR 1 (必须先合并)
  ├── PR 2: governance_eval 行为回归
  └── PR 3: smoke + sync + maintainer 验证链
        ↓
     集成验证 → M4
```

### 4.3 执行块

```text
[parallelism:
- independent lanes: PR 2 与 PR 3 可并行；二者都依赖 PR 1 的模板正文稳定
- sequential blockers: 先定模板边界，再固化回归与投影验证
- shared write surfaces: templates/governance/*, AGENTS.md, CLAUDE.md, maintainer/governance_eval/*, maintainer/scripts/install/*, maintainer/scripts/analysis/*, docs/maintainer/*
- delegation: 0 with reason: 本计划先按单线 maintainer 实施编排，避免并行改动模板与验证时互相踩面
]
```

## 5. PR 1：模板行为边界基线

### 5.1 目标

在**不新增顶层 H2 section** 的前提下，把路线图 `P0` 里的行为边界落进现有模板：

- 哪些动作可以默认继续
- 哪些动作必须人工确认
- fast path 与 full path 的最小区分
- review clean、局部编辑、本地验证之间何时可自动衔接

### 5.2 任务清单

| 序号 | 任务 | 输入 | 输出 |
|---|---|---|---|
| 1.1 | 为 `Behavioral Guidelines` 增补默认继续边界 | 两份模板 | 明确局部编辑、本地验证、非破坏性下一步可默认继续 |
| 1.2 | 为 `Validation Rules` 增补本地验证 vs 必停边界 | 两份模板 | 明确外部系统、真实数据、高成本验证不默认执行 |
| 1.3 | 为 `Skill Activation` 增补 fast path 与 full path 区分 | 两份模板 | 轻量任务不过度升级；高风险任务进入完整链路 |
| 1.4 | 为 `Escalation Rules` 增补必须停下的升级信号 | 两份模板 | 公共接口、schema/migration、依赖/工具链、需求歧义等进入澄清或升级 |
| 1.5 | 为 `Common Flow Patterns` 增补自动衔接与中断边界 | 两份模板 | 明确哪些链路遇到契约/迁移/依赖/发布即中断 |
| 1.6 | 为 `Multi-Agent Rules` 明确“允许并行”不等于“默认并行” | 两份模板 | 不可干净拆分时应显式 `[delegate: 0]` |
| 1.7 | 枚举根文件允许保留的 repo-only overlay | 根文件 | 一份显式 overlay 清单，列出宿主 section、保留原因、后续 sync lint 应如何忽略 |
| 1.8 | 同步仓库根 `AGENTS.md` / `CLAUDE.md` 共享治理正文 | 根文件 + 模板 | 根文件反映模板改动，同时保留已枚举的 repo-only overlay |

### 5.3 文件落点

- `templates/governance/AGENTS-template.md`
- `templates/governance/CLAUDE-template.md`
- `AGENTS.md`
- `CLAUDE.md`

### 5.4 验证（PR 1）

- `python3 maintainer/scripts/analysis/check_governance_sync.py`
- 定向人工 diff：
  - 模板两份镜像是否保持同义
  - 根文件共享正文是否跟上模板
  - repo-specific overlay 是否仍只留在根文件，且能对照到 5.2 的 overlay 清单
- `python3 maintainer/scripts/install/run_manage_governance_smoke.py`

### 5.5 回滚

- `git revert <PR1 merge sha>`
- 如果只出现根文件 overlay 误删，可先单独恢复根文件 overlay，再重新同步共享正文

### 5.6 风险

- **风险：** 模板边界写得太抽象，行为回归无法判定  
  **缓解：** 每条新增边界都要能映射到后续 PR 2 的具体样例
- **风险：** 根文件同步时误删 repo-only overlay  
  **缓解：** PR 1 必须显式列出允许保留的根文件特定段落，并在 diff 中单独复核

## 6. PR 2：治理模板行为回归

### 6.1 目标

把“模板看起来写清楚了”升级成“agent 在隔离工作区里能按模板做出正确判断”。

这一步只测试治理模板语义，不测试安装投影，不测试 skill 内容本身。

### 6.2 任务清单

| 序号 | 任务 | 输出 |
|---|---|---|
| 2.1 | 先清理或重写当前 live governance_eval suite 中的历史语义 case | `cases.yaml` 与评测说明只保留 post-2026-05 仍有效的模板概念 |
| 2.2 | 为 `continue` / `ask` / `must stop` 新增行为用例 | `maintainer/governance_eval/cases.yaml` 增补样例 |
| 2.3 | 收敛 fast path / full path 的行为判定 | 同上；覆盖轻量本地改动与高风险升级场景 |
| 2.4 | 增补并行边界样例 | 覆盖“能并行”与“必须 `[delegate: 0]`”的分界 |
| 2.5 | 必要时扩 `run_eval.py` 的响应抽取或 judge 支持 | 保证新用例可被稳定执行与判分 |
| 2.6 | 更新 `maintainer/docs/governance-template-eval.md` | 说明 live suite 的适用范围、新增样例类别与隔离原则 |

### 6.3 建议新增样例类别

在新增样例前，live suite 里不应再保留面向退役 section 的主路径断言，例如：

- `Skill Family Concurrency Budgets`
- `Forward Handoffs` / `Fallbacks`
- 已退役的 `Skill Protocol v1` / `Skill Protocol v2` 语义

这些历史 case 如果仍需保留，应转入历史快照说明，而不是继续作为 live evaluator 的主入口。

新增样例至少覆盖下列 6 类：

1. 小范围本地改动应默认继续
2. 多文件但无公共契约变更的任务应进入计划后继续
3. 公共接口 / cross-module contract 变更必须 ask 或升级
4. schema / migration 必须 ask 或升级
5. 依赖、工具链、提交、推送、发布动作必须 ask
6. 不可干净拆分的并行请求必须 `[delegate: 0]`

### 6.4 文件落点

- `maintainer/governance_eval/cases.yaml`
- `maintainer/governance_eval/run_eval.py`
- `maintainer/docs/governance-template-eval.md`

### 6.5 验证（PR 2）

- `uv run maintainer/governance_eval/run_eval.py --case <new-case-id> --runs 1`
- 对新增 case 做一次最小批量回归，确认 judge 与 prompt 没有自相矛盾
- 静态检查 live evaluator 已不再把退役 section 当作当前主路径：
  - `rg "Skill Family Concurrency Budgets|Forward Handoffs|Fallbacks|Skill Protocol v1|Skill Protocol v2" maintainer/governance_eval maintainer/docs/governance-template-eval.md`
  - 如果仍保留这些词，必须只出现在明确的历史说明中，而不是 live case 主体
- 如果本地 CLI 凭据不可用，至少完成：
  - prompt / judge 静态复核
  - `run_eval.py` 代码路径自检
  - 阻塞说明写回 PR 描述或计划执行记录

### 6.6 回滚

- `git revert <PR2 merge sha>`
- 若只有个别 case 判定不稳定，可先 revert case 变更，保留文档说明和 runner 小修

### 6.7 风险

- **风险：** case 写成“读懂仓库后才能答”，破坏模板隔离原则  
  **缓解：** 所有 prompt 默认只允许 agent 读取部署后的治理文件，不引用仓库其他路径
- **风险：** `expect_current` / judge 与模板新语义不同步  
  **缓解：** 模板改动与 case 更新必须在同一批次完成，不允许先改 evaluator expectation 再晚些时候补模板

## 7. PR 3：投影 smoke、同步 lint 与维护者验证链

### 7.1 目标

让模板改动之后的下游闭环更强，不再只靠维护者记忆补检查。

### 7.2 任务清单

| 序号 | 任务 | 输出 |
|---|---|---|
| 3.1 | 把 5.2 产出的 overlay 清单转成可执行的同步约束 | 定义 root 文件中哪些位置允许 repo-only overlay，以及比较时如何忽略 |
| 3.2 | 增强 `check_governance_sync.py` | 从 H2 顺序检查提升到“共享正文 + 允许 overlay”级别的同步约束 |
| 3.3 | 增强 `run_manage_governance_smoke.py` | 对新加入的治理边界补代表性断言 |
| 3.4 | 在 maintainer 文档中固定模板改动验证链 | 维护者能按固定顺序跑 sync、smoke、behavior eval、cross-reference |
| 3.5 | 更新相关维护入口 | `docs/maintainer/README.md` / `_sidebar.md` / 必要的 maintainer 文档交叉引用 |

### 7.3 建议同步规则

`check_governance_sync.py` 的增强目标不是要求根文件与模板字节相等，而是：

- 模板镜像仍然保持一致
- 根文件共享治理正文与模板一致
- 允许的 repo-only overlay 是显式、可枚举、可忽略的
- 根文件之间仍保持镜像，不允许无说明 drift

在真正修改脚本前，应先固定 overlay contract 的表达方式，至少明确：

- overlay 位于哪个 section、哪一段
- overlay 是通过文本锚点、结构化注释，还是显式 whitelist 做忽略
- 什么情况算“新增了未经批准的 overlay”

### 7.4 文件落点

- `maintainer/scripts/analysis/check_governance_sync.py`
- `maintainer/scripts/install/run_manage_governance_smoke.py`
- `docs/maintainer/manual-and-repo-development.md`
- `docs/maintainer/README.md`
- `docs/maintainer/_sidebar.md`

### 7.5 验证（PR 3）

- `python3 maintainer/scripts/analysis/check_governance_sync.py`
- `python3 maintainer/scripts/install/run_manage_governance_smoke.py`
- `python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken`

### 7.6 回滚

- `git revert <PR3 merge sha>`
- 若 sync lint 收得过严，可先降级到“允许 overlay”的较弱规则，再补第二轮 tightening

### 7.7 风险

- **风险：** sync lint 过严，误伤根文件允许存在的 repo-only 说明  
  **缓解：** 先把允许 overlay 的位置和文本类型枚举清楚，再写比较逻辑
- **风险：** smoke 断言绑定到过细 wording，导致模板文案微调时频繁误报  
  **缓解：** 只挑代表性、稳定、高信号的 snippet 做断言

## 8. 集成验收

### 8.1 集成验证顺序

1. `python3 maintainer/scripts/analysis/check_governance_sync.py`
2. `python3 maintainer/scripts/install/run_manage_governance_smoke.py`
3. `uv run maintainer/governance_eval/run_eval.py --runs 1`
4. `python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken`

### 8.2 Done Criteria

这一增量完成时，应满足：

- 模板正文中已经能读出 `continue` / `ask` / `must stop`
- 隔离工作区行为回归能覆盖新边界，并且至少有一轮**经过认证的 maintainer 本地 run** 产生可信通过结果
- 根文件共享治理正文已与模板同步，repo-only overlay 仍保留且可解释
- 安装 smoke、sync lint、cross-reference 都通过
- maintainer 文档能告诉后来者“模板改动后要先跑什么、再跑什么”

这里的“可信通过结果”不是指所有环境都必须能自动跑通。  
如果当前执行环境缺少 CLI 凭据、模型权限或本地信任配置，PR 级验证可以先停在静态复核 + 阻塞记录；但进入 `M4` 前，必须至少补一轮经过认证的 maintainer 本地 run。

## 9. 后续门槛（进入 P2 前）

下面这些事项不进入本计划的实施范围，但可作为进入 `P2` 的前置门槛：

- 模板边界改动在两个平台模板上稳定运行至少一轮
- 行为回归 case 不再频繁抖动
- 根文件 overlay 已有显式允许清单
- 维护者验证链被实际使用，而不是只写在文档里

在这些条件未满足前，不建议同时推进更大的 `Skill Protocol` 收敛或模板镜像抽象。
