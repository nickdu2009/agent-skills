# Review-Loop 主链 5 件套 实施计划

> 配套设计文档：`docs/maintainer/review-loop-mainchain-design.md`（已通过 review-loop clean）
> 本计划只做"怎么实施"，不重复"为什么这样设计"。任何与设计文档冲突时以设计文档为准。

## 1. 范围与依据

### 1.1 范围
- 落地主链 5 件套 SKILL.md
- 一次重命名（`implementation-review-loop` → `code-review-loop`）
- 一份触发测试集
- 更新维护文档索引

### 1.2 不在范围
- 新建 Tier 2/3 review skill（`api-contract-review-loop` 等）
- 任何对 `AGENTS.md` 主体结构的改动（仅在主链稳定后追加 Skill Chain Triggers 示例，作为后续动作）

### 1.3 关键依据章节
| 依据 | 对应设计文档章节 |
|---|---|
| 命名 | §6.1 / §6.2 |
| 统一骨架 | §4.1–§4.5 |
| 各 skill 维度 | §5.1–§5.5 |
| 路由策略 | §7.1–§7.4 |
| 共性落地工作 | §10.1 |
| 验收门槛 | §1.2 / §10.3 |
| 修订执行规范 | §13 第 5 条 |

## 2. 总体路线

### 2.1 里程碑
```
M1: PR 1 合并 → 统一骨架基线确立，命名修正完成
M2: PR 2 合并 → requirements + design 两个新 skill 上线
M3: PR 3 合并 → test skill 上线，5 件套完整
M4: 触发测试通过 → 达到 §1.2 量化指标
```

### 2.2 PR 依赖图
```
PR 1 (必须先合并)
  ├── PR 2 (可并行)
  └── PR 3 (可并行)
        ↓
     触发测试回归 → §1.2 指标达成
```

### 2.3 PR 拆分汇总

| PR | 标题 | 包含文件 | 行数估算 |
|---|---|---|---|
| PR 1 | 主链骨架基线 + code-review-loop 改名 | `skills/code-review-loop/SKILL.md`（改名+改造）、`skills/plan-review-loop/SKILL.md`（改造） | +35 行 |
| PR 2 | 新建 requirements + design review-loop | `skills/requirements-review-loop/SKILL.md`、`skills/design-review-loop/SKILL.md`、`tests/triggers/review-loop-mainchain.yaml`（部分） | +220 行 |
| PR 3 | 新建 test-review-loop + 索引/维护文档更新 | `skills/test-review-loop/SKILL.md`、`tests/triggers/review-loop-mainchain.yaml`（完整化）、`docs/maintainer/_sidebar.md`、`docs/maintainer/index.html` | +130 行 |

---

## 3. PR 1：主链骨架基线 + 改名

### 3.1 任务清单

| 序号 | 任务 | 输入 | 输出 |
|---|---|---|---|
| 1.1 | `git mv` 改名 | `skills/implementation-review-loop/` | `skills/code-review-loop/` |
| 1.2 | 修改 frontmatter `name:` | `skills/code-review-loop/SKILL.md` | 同文件 `name: code-review-loop` |
| 1.3 | code-review-loop 章节按 §4.1 骨架对齐 | 改名后的 SKILL.md | 含 `Optional checks` 章节 + `Scope protection` 在 `Validation` 之前 |
| 1.4 | code-review-loop 共性落地（§10.1） | 同上 | description / Constraints / Validation / Scope protection 段全部到位 |
| 1.5 | plan-review-loop 章节按骨架对齐 | `skills/plan-review-loop/SKILL.md` | 新增 `Scope protection` 章节 |
| 1.6 | plan-review-loop 共性落地（§10.1） | 同上 | description / Constraints / Validation / Scope protection 段全部到位 |
| 1.7 | 仓库全局 grep 验证旧名清零 | 仓库根 | `rg implementation-review-loop` 0 命中 |

### 3.2 操作步骤
```bash
# 1.1
git mv skills/implementation-review-loop skills/code-review-loop

# 1.2–1.6 用编辑器逐项改

# 1.7 验证
rg -n 'implementation-review-loop' .  # 期望 0 命中
```

### 3.3 验证（PR 1）
- 仓库全局 `rg implementation-review-loop` 0 命中
- `code-review-loop/SKILL.md` 与 `plan-review-loop/SKILL.md` 章节顺序对照 §4.1 完全一致
- 两个 SKILL.md 的 Constraints 含 §4.5 反向边界声明
- 两个 SKILL.md 的 description 含 §7.4 易混淆词排除提示
- 跑现有触发测试集（如有），确认 plan-review-loop 与 code-review-loop 命中率不下降

### 3.4 回滚
- `git revert <PR1 merge sha>` 即可；无 DB 迁移、无外部接口变更

### 3.5 风险
- 改名后若有未发现的外部引用，触发名失效 → 缓解：3.3 的全局 grep；如有遗漏，补 alias 或更新引用
- 章节顺序调整可能影响 SKILL.md 现有 trigger → 缓解：3.3 的触发测试回归

---

## 4. PR 2：新建 requirements-review-loop + design-review-loop

### 4.1 任务清单

| 序号 | 任务 | 输出 |
|---|---|---|
| 2.1 | 新建 `skills/requirements-review-loop/SKILL.md`（参考 §6.1 §7） | ~110 行，完全符合 §4.1 骨架与 §10.1 共性 |
| 2.2 | 新建 `skills/design-review-loop/SKILL.md`（参考 §6.2 §7） | ~110 行，同上 |
| 2.3 | 新建 `tests/triggers/review-loop-mainchain.yaml`（仅含 req + design 部分） | 每件套 ≥ 10 条正向 prompt + §7.4 易混淆词 prompt |
| 2.4 | 跑触发测试 | requirements + design 命中率 ≥ 90% |

### 4.2 SKILL.md 大纲（按 §4.1 骨架，仅列必填要点）

#### `requirements-review-loop/SKILL.md`
```
frontmatter:
  name: requirements-review-loop
  description: 含 WHAT/WHEN，关键词 = requirement / PRD / user story / acceptance criteria
              + 排除"方案/实现思路/接口/思路" → 重定向到对应 skill

Goal: 一句话定位"审核需求文档，反复直到 review_result: clean"

Required loop: 7 步（按 §4.4 协议，针对需求文档实例化）

Issue rules:
  blocking: 需求缺失关键 input/output；与已有需求冲突；无验收标准
  warning: 边界场景未覆盖；术语不统一；隐含假设
  low-risk: 单条需求表述含糊；优先级缺失（必须闭环）

Validation: 不跑代码；
  - 对照仓库现状反查可行性
  - 术语对照表检验词汇统一
  - 对每条需求写一句"如何验证"
  - 引用 targeted-validation 作为方法论

Clean result rule: 三档为空 + 修复已应用 + Residual 已记录

Output format: 复用设计文档 §4.3 完整模板

Constraints:
  - 不停留在仅报告
  - 不修无关文档
  - Do not use for design / plan / code / test review; use 对应 skill
```

#### `design-review-loop/SKILL.md`
结构同上，差异点：
- 关键词：design doc / RFC / ADR / architecture / interface design
- 维度按 §5.2：意图对齐 / 方案合理 / 约束尊重 / 接口契约 / 失败设计 / 复杂度合理 / 影响面
- Validation：对照需求文档 / 对照现有架构 / 反问"如果不这样做"
- 反向边界：排除 requirements / plan / code

### 4.3 触发测试集片段（PR 2 部分）
```yaml
# tests/triggers/review-loop-mainchain.yaml
requirements-review-loop:
  positive:
    - "评审一下这份需求文档"
    - "帮我看看 PRD 写得是否完整"
    - "审核用户故事的验收标准"
    - "需求里有没有边界条件没写"
    - "review this requirements doc"
    - "帮我检查需求文档的可验证性"
    - "看看这个需求是否清晰"
    - "需求文档有没有内部冲突"
    - "评审 acceptance criteria"
    - "PRD review"
  must_not_trigger:
    - "评审实现代码"        # → code-review-loop
    - "评审实施计划"        # → plan-review-loop
    - "评审架构设计"        # → design-review-loop

design-review-loop:
  positive:
    - "评审一下架构设计"
    - "帮我看看这份 RFC"
    - "审核 ADR 文档"
    - "接口设计是否合理"
    - "review this design doc"
    - "评审技术方案"
    - "评审实现思路"
    - "看看接口定义有没有问题"
    - "帮我评估这个数据模型设计"
    - "评审 architecture"
  must_not_trigger:
    - "评审需求文档"        # → requirements-review-loop
    - "评审实施计划"        # → plan-review-loop
    - "评审代码"            # → code-review-loop

# §7.4 易混淆词
disambiguation:
  - prompt: "评审实现方案"
    expected: design-review-loop  # 不是 code
  - prompt: "评审迁移方案"
    expected: plan-review-loop    # 不是 design
  - prompt: "评审接口"
    expected: design-review-loop  # 默认设计阶段
```

### 4.4 验证（PR 2）
- 两个 SKILL.md 章节顺序对照 §4.1 完全一致
- 两个 SKILL.md 通过仓库已有的 skill linter（如有）
- 触发测试结果：requirements + design 各 ≥ 90% 命中
- 跨 skill 误触发率 ≤ 5%
- §7.4 易混淆词 prompt 命中 expected skill

### 4.5 回滚
- `git revert <PR2 merge sha>`；新增文件回退即可
- 触发测试 yaml 是新建文件，删除无影响

### 4.6 风险
- 新增 2 个 skill 触发关键词与现有 skill 冲突 → 缓解：4.4 触发测试 + 反向边界声明
- design 与 plan 在中文"方案"一词上易混 → 缓解：§7.4 已显式约定，触发测试已覆盖

---

## 5. PR 3：新建 test-review-loop + 索引更新

### 5.1 任务清单

| 序号 | 任务 | 输出 |
|---|---|---|
| 3.1 | 新建 `skills/test-review-loop/SKILL.md` | ~110 行，符合 §4.1 / §10.1 |
| 3.2 | 完整化 `tests/triggers/review-loop-mainchain.yaml`（补 test 部分） | 5 件套全覆盖 |
| 3.3 | 更新 `docs/maintainer/_sidebar.md` / `index.html`，加入主链 5 件套设计与计划链接 | 索引可见 |
| 3.4 | 在 `docs/maintainer/trigger-test-optimization-tracker.md` 追加主链触发测试结果一节 | 数据归档 |
| 3.5 | 跑全套触发测试 | 5 件套全部达 §1.2 指标 |

### 5.2 SKILL.md 大纲（test-review-loop）
- 关键词：test / 测试 / test cases / coverage / 用例 / 覆盖
- 维度按 §5.5：场景覆盖 / 断言质量 / 隔离性 / 确定性 / 可读性 / 维护成本 / 与被测代码对齐
- Validation：跑测试；mutation 心智演练；单文件隔离运行
- 反向边界：排除 requirements / design / plan / code（特别强调"测试代码"≠"实现代码"）

### 5.3 触发测试集片段（PR 3 完整化）
```yaml
test-review-loop:
  positive:
    - "评审测试用例"
    - "帮我看看测试覆盖是否够"
    - "审核测试策略"
    - "review test cases"
    - "测试有没有 flaky 风险"
    - "测试断言够不够强"
    - "评审 coverage 矩阵"
    - "看看测试是否过度 mock"
    - "测试是否能单独运行"
    - "审核新增的单元测试"
  must_not_trigger:
    - "评审被测的产品代码"  # → code-review-loop
    - "评审测试需求"        # → requirements-review-loop（需求里包含可测性要求）
```

### 5.4 验证（PR 3）
- 全套触发测试：每件套 ≥ 90% 命中率
- 跨件套总误触发率 ≤ 5%
- 易混淆词全部归属正确（§7.4 表 7 条）

### 5.5 回滚
- `git revert <PR3 merge sha>`；新增文件回退

### 5.6 风险
- test-review-loop 与 code-review-loop 在"测试"词上重叠 → 缓解：description 明确"审测试用例本身"vs"审被测代码"

---

## 6. 五件套 SKILL.md 内容大纲索引

避免在本计划文件里写全文（落地时直接生成）；这里列每个文件应包含的关键决策点，供落地时核对。

| Skill | 维度数 | 反向边界对象 | 关键易混淆词 | Validation 类型 |
|---|---|---|---|---|
| `requirements-review-loop` | 7（§5.1） | design / plan / code / test | 方案 / 接口 / 思路 | 不跑代码 |
| `design-review-loop` | 7（§5.2） | requirements / plan / code | 实施方案 / 迁移方案 | 不跑代码 |
| `plan-review-loop` | 7（§5.3） | requirements / design / code | 思路 / 方案（指设计时） | 不跑代码 |
| `code-review-loop` | 6 核心 + 1 可选（§5.4） | requirements / design / plan / test | 测试用例（指 test） | 跑代码 |
| `test-review-loop` | 7（§5.5） | requirements / design / plan / code | 被测代码 | 跑测试 |

---

## 7. 触发测试集设计

### 7.1 文件位置
`tests/triggers/review-loop-mainchain.yaml`（若已有触发测试目录约定，沿用；否则按设计文档 §13 第 3 条归档进 `trigger-test-optimization-tracker.md`）

### 7.2 样本规模
- 每件套 positive prompt ≥ 10 条
- 每件套 must_not_trigger prompt ≥ 3 条（指向相邻 skill）
- §7.4 易混淆词逐条 ≥ 1 条 prompt

总计 ≥ 5 × (10 + 3) + 7 = 72 条 prompt

### 7.3 通过门槛（与 §1.2 / §10.3 一致）
- 命中率 ≥ 90%
- 跨件套误触发率 ≤ 5%
- 易混淆词归属 100% 正确

### 7.4 测试输出
- 每个 PR 跑一次，结果追加进 `trigger-test-optimization-tracker.md`
- PR 3 跑完作为 v1.x 主链发布基线

---

## 8. 工作量估算

| PR | 估算 | 主要时间消耗 |
|---|---|---|
| PR 1 | 30–60 分钟 | 改名 + 两个 SKILL.md 章节调整 |
| PR 2 | 90–150 分钟 | 两个新 SKILL.md + 触发测试 yaml 初版 |
| PR 3 | 60–120 分钟 | 一个新 SKILL.md + 触发测试完整化 + 文档索引 |
| 触发测试回归（每 PR 一次） | 5–15 分钟/次 | 取决于测试基础设施 |

**总计**：3–6 小时纯实施时间

## 9. 风险与全局回滚

### 9.1 全局风险表
| 风险 | 严重度 | 触发条件 | 缓解 |
|---|---|---|---|
| PR 1 改名遗漏外部引用 | 中 | 仓库或文档中有未发现的 `implementation-review-loop` 字符串 | PR 1 验证 3.3 强制 `rg` 全局；如有遗漏，热修一次 |
| PR 2/3 触发关键词碰撞 | 中 | 新 skill description 与现有 skill 重叠 | 反向边界声明 + 触发测试 + §7.4 易混淆词验证 |
| 修订设计文档时引入新矛盾 | 中 | 落地过程发现设计文档需要修订 | 按 §13 第 5 条三步规范执行 |
| 触发测试基础设施缺失 | 中 | 仓库当前没有自动化触发测试 | 退化为人工"试触发"checklist；记入 tracker |

### 9.2 全局回滚策略
- 任一 PR 出问题：`git revert` 该 PR；其余 PR 不受影响（依赖图保证）
- 全部回滚到 PR 1 之前状态：依次 revert PR 3 → PR 2 → PR 1
- 灾备：本计划文档 + 设计文档保留在仓库，重做时可直接复用

## 10. 跟踪表

| 项 | 状态 | 关联 PR | 负责人 | 备注 |
|---|---|---|---|---|
| 设计文档评审通过 | ✅ done | — | — | review-loop 4 轮 clean |
| 实施计划评审通过 | ⏳ pending | — | — | 等待用户确认 |
| PR 1 改动准备 | ⏳ pending | PR 1 | — | |
| PR 1 触发测试回归 | ⏳ pending | PR 1 | — | |
| PR 1 合并 | ⏳ pending | PR 1 | — | M1 |
| PR 2 改动准备 | ⏳ pending | PR 2 | — | |
| PR 2 触发测试 | ⏳ pending | PR 2 | — | |
| PR 2 合并 | ⏳ pending | PR 2 | — | M2 |
| PR 3 改动准备 | ⏳ pending | PR 3 | — | |
| PR 3 触发测试完整化 | ⏳ pending | PR 3 | — | |
| PR 3 合并 | ⏳ pending | PR 3 | — | M3 |
| §1.2 量化指标达成 | ⏳ pending | — | — | M4 |
| AGENTS.md 链路示例追加 | ⏳ pending | 后续 | — | 设计文档 §13 第 4 条 |

## 11. 后续动作（落地后）

1. 5 件套稳定运行 1–2 迭代后，根据团队痛点决定是否补 Tier 2（`api-contract-review-loop` 等）
2. 若新增 review skill，遵循 §6.2 命名元规则与 §4.1 骨架
3. 若设计文档需要修订，遵循 §13 第 5 条三步规范
