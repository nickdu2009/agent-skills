# 当前项目测试评价

> 日期：2026-04-27
> 范围：`agent-skills` 仓库当前已存在的测试资产、执行入口、自动化程度与主要缺口

---

## 结论摘要

当前仓库的测试体系不是传统应用项目的“单元测试 + 集成测试”模型，而是更适合本仓库性质的混合模式：

- CI 静态校验
- 安装器烟雾测试
- 阶段系统的自动化 `pytest`
- 触发测试矩阵
- 行为场景验收与人工评分

这个方向是正确的，因为仓库的核心产物是 **skills、governance 规则、安装器与评估工具**，而不是一个单一运行时服务。

但从“当前健康度”看，测试体系仍有三个明显问题：

1. 自动化覆盖深度不均衡，最扎实的是 `phase-contract-tools`，其他区域更多停留在语法或人工评估层。
2. 核心检查没有形成稳定绿灯闭环，本次抽样里已有 2 项关键检查失败。
3. 缺少统一测试入口，维护者很难快速回答“这个仓库现在算不算测过了”。

**总体评价：方向正确，体系分层清楚，但离“稳定可回归”的维护体验还有一段距离。**

---

## 当前测试版图

| 层级 | 当前资产 | 作用 | 当前观察 |
|------|-----------|------|----------|
| CI 静态校验 | `.github/workflows/ci.yml` | 校验 `SKILL.md` 边界、frontmatter、仓库布局、Python 语法 | 覆盖基础约束，但偏静态 |
| 安装器烟雾测试 | `maintainer/scripts/install/run_manage_governance_smoke.py` | 在临时目录验证安装和本地 mirror 核心路径 | 有价值，但当前抽样失败 |
| 自动化单测/契约测试 | `skills/phase-contract-tools/scripts/test_contract_validators.py` | 验证 phase 契约工具、负例、fixture 正例 | 当前最扎实，抽样 `36 passed` |
| 触发测试 | `maintainer/data/trigger_test_data.py` + `run_trigger_tests.py` | 检查技能触发/不触发是否符合预期 | 数据面较完整，82 个 case、12 个类别 |
| 行为场景测试 | `maintainer/data/skill_test_data.py` + `examples/` + 报告生成脚本 | 用场景验证技能链是否按设计工作 | 有 6 个场景、6 个全局维度、15 个技能 rubric |
| 人工交互验收 | `docs/user/SKILL-TESTING-QUICK-START.md`、Claude 交互式清单/计划 | 验证真实多轮 Agent 行为 | 适合高价值回归，但成本较高 |

---

## 本次抽样结果

本次没有做全量回归，只执行了最能代表当前健康度的 3 组检查：

### 1. 阶段系统自动化测试

命令：

```bash
uv run pytest skills/phase-contract-tools/scripts/test_contract_validators.py -q
```

结果：**通过，36 项测试全部通过。**

这说明仓库里最工程化、最契约驱动的一块目前是健康的，也是现有测试体系里自动化程度最高的区域。

### 2. 仓库布局校验

命令：

```bash
python3 maintainer/scripts/install/validate_repo_layout.py
```

结果：**失败。**

失败信息指向当前仓库结构与校验器假设不一致，例如：

- 顶层存在未被接受的追踪项
- `docs/manual/` 被视为意外子目录
- `scripts/` 顶层路径被判定为 forbidden

这更像是“仓库已经演化，但校验器规则没有同步更新”，说明 **测试存在，但规则与现状已经出现漂移**。

### 3. 安装器烟雾测试

命令：

```bash
python3 maintainer/scripts/install/run_manage_governance_smoke.py
```

结果：**失败。**

失败点是生成的 `CLAUDE.md` 未包含测试脚本期待的固定字符串 `base-level CLAUDE.md rules`。这说明当前烟雾测试对模板文本的断言偏脆弱，只要文案演进但语义未必改变，测试就会红。

---

## 优点

### 1. 测试形态和仓库性质是匹配的

这个仓库的核心风险不是“函数算错”，而是：

- skill 描述漂移
- governance 路由失真
- 安装器注入错误
- 场景行为与设计哲学偏离

因此把测试拆成静态校验、安装器烟雾、触发矩阵、行为验收，是合理的。

### 2. phase 子系统已经形成真正的自动化契约保护

`phase-contract-tools` 不只是“有脚本”，而是已经具备：

- `pytest` 自动化测试
- 负例校验
- fixture 正例
- CLI 级调用验证

这部分最接近“可以放心重构”的状态，说明仓库已经验证过：**高风险、强契约区域值得投入更重的自动化。**

### 3. 评估数据面已经不小

当前可见的数据资产并不算薄：

- 82 个 trigger case
- 12 个 trigger category
- 6 个 example case
- 6 个 global rubric dimension
- 15 个 skill-specific rubrics

这意味着仓库并不是“没有测试设计”，而是 **设计已经有了，闭环还不够自动和稳定**。

---

## 主要缺口

### 1. 自动化覆盖非常不均衡

目前最强的是 `phase-contract-tools`，但其余区域大多是：

- 语法检查
- 手工脚本
- prompt/report 级评估
- 人工执行的场景测试

这会导致仓库整体质量看上去“测试很多”，但真正可重复、可机器判定的覆盖主要集中在少数模块。

### 2. CI 还不是完整回归门

当前 CI 更像“基础卫生检查”，并没有把以下高价值能力纳入常规门禁：

- trigger matrix 执行结果
- 行为场景评分
- 维护者常用评估脚本的功能级回归

这使得仓库可以在 CI 通过时，依然存在“行为层”或“工具层”的真实退化。

### 3. 核心检查已经出现漂移

本次抽样中两项关键检查失败：

- 布局校验器与当前仓库结构不一致
- 安装器烟雾测试与当前模板文案不一致

这类失败比“没有测试”更危险，因为它会逐渐削弱维护者对测试结果的信任。

### 4. 缺少统一入口

当前 `Makefile` 只提供文档预览，没有提供例如：

- `make test`
- `make test-fast`
- `make test-maintainer`

这会抬高维护门槛，也让“改完后到底该跑什么”变成文档记忆题。

### 5. 行为测试仍然重人工

行为测试设计是合理的，但现实问题是：

- 执行成本高
- 评分波动大
- 难直接作为稳定 CI gate

因此它更像“维护者评审工具”，还不是“日常自动回归工具”。

---

## 改进优先级

### P0：先恢复红灯项可信度

1. 对齐 `validate_repo_layout.py` 与当前仓库真实边界。
2. 调整 `run_manage_governance_smoke.py` 的断言方式，减少对固定文案的脆弱依赖，优先断言结构和关键 section。
3. 明确一组“当前必须为绿”的基础命令，并写入维护者文档。

### P1：建立统一测试入口

建议至少增加：

- `make test-fast`：布局校验 + 关键 smoke + phase pytest
- `make test-eval`：trigger/report 相关检查
- `make test`：组合前两者

这样能把“测试资产”变成“可执行工作流”。

### P1：扩大自动化覆盖到高价值脚本

优先补的不是所有脚本，而是最常改、最影响维护闭环的几类：

- `maintainer/scripts/evaluation/` 下的核心入口
- `maintainer/scripts/install/` 下的安装与同步路径
- 关键数据加载与报告生成逻辑

### P2：把行为测试固定为基线流程，而不是偶发动作

不建议把 LLM-as-judge 直接变成硬 CI gate，但建议：

- 保留人工/半自动基线报告
- 固定抽样场景
- 在重要改版后更新 retained baseline

这样更符合这类仓库的实际约束。

---

## 建议的维护者最小测试清单

如果目标是“低成本但不失真”，建议当前仓库先收敛到下面这组最小回归清单：

1. `python3 maintainer/scripts/install/validate_repo_layout.py`
2. `python3 maintainer/scripts/install/run_manage_governance_smoke.py`
3. `uv run pytest skills/phase-contract-tools/scripts/test_contract_validators.py -q`
4. `python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report`
5. 选择 1 个 `examples/` 场景做人工或半自动行为抽样

这 5 步组合起来，基本能覆盖：

- 仓库边界
- 安装器主路径
- phase 契约工具
- trigger 层
- 行为层

---

## 最终判断

当前项目的测试体系 **不是弱，而是“分层正确、闭环不足”**。

它已经具备成为一套优秀维护体系的骨架：

- 有静态规则
- 有可执行 smoke
- 有真正的自动化 pytest
- 有行为评估数据模型
- 有人工验收清单

但它还缺两件决定成熟度的事情：

1. 让核心检查重新回到稳定绿色。
2. 把分散入口收敛成维护者默认工作流。

只要这两点补上，这个仓库的测试体系就会从“设计合理”迈向“日常可依赖”。
