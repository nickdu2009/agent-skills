# 需求设计阶段覆盖分析

## 问题诊断

在添加 `design-before-plan` 技能之前，技能库存在明显的需求设计阶段覆盖缺口：

### 前期设计活动覆盖度（补充前）

| 前期设计活动 | 现有覆盖 | 覆盖程度 |
|-------------|---------|---------|
| **需求收集** | scoped-tasking Step 0（浅层澄清） | **浅层** — 仅限模糊任务的快速提问 |
| **需求深化** | 无 | **无覆盖** |
| **用户故事分析** | 无 | **无覆盖** |
| **设计方案比较** | 无 | **无覆盖** |
| **接口契约定义** | 散落在实施阶段 | **零散** — 无专门方法论 |
| **验收标准推导** | scoped-tasking、incremental-delivery、phase-plan | **零散** — 有提及但无系统流程 |
| **架构约束识别** | impact-analysis（间接）、safe-refactor（不变量） | **弱** — 以技术分析为主，非需求驱动 |

### 核心问题

现有技能的设计假设是：**需求已经基本明确，agent 的任务是把需求正确转化为代码变更。**

但实际工作中，agent 经常面对：
1. **模糊或不完整的需求** — 需要系统性提问、分解、确认
2. **多种实现方案** — 需要在架构/设计层面比较权衡
3. **跨模块的设计决策** — 需要先确定接口契约再开始编码
4. **验收标准缺失** — 需要从需求推导出可验证的完成条件

---

## 解决方案：design-before-plan 技能（增强版）

### 技能定位

- **在工作流中的位置**：scoped-tasking 之后，plan-before-action 之前
- **核心职责**：需求深化、隐性需求挖掘、设计方案比较、接口契约定义、数据迁移策略、验收标准推导
- **输出**：结构化的设计文档（design brief），作为 plan-before-action 的输入

### 技能覆盖的设计活动

| 阶段 | 活动 | 输出 |
|-----|------|-----|
| **1. 需求深化** | 提取功能需求、非功能需求、**隐性需求**（安全/性能/可观测性/韧性/运维性）、边界场景 | requirements 节（含 implicit 子节） |
| **2. 方案枚举** | 列举 2-4 种候选方案，分析优劣势和爆炸半径，考虑标准设计模式（自然涌现，非强制） | design_alternatives 节 |
| **3. 方案选择** | 基于约束、可逆性、代码库模式选择方案并记录理由 | chosen_design 节 |
| **4. 契约定义** | 定义输入/输出契约、错误处理语义、兼容性策略 | interface_contracts 节 |
| **4.5. 数据迁移** | 识别 schema 变更、设计前向/后向迁移路径、评估复杂度和风险、定义验证方法 | data_migration 节（如适用） |
| **5. 验收标准** | 从需求推导可验证的成功条件（非实现细节） | acceptance_criteria 节 |
| **6. 约束识别** | 识别必须保留的系统不变量、框架限制、平台约束 | architectural_constraints 节 |

### 工作流集成

```
用户请求
    ↓
scoped-tasking        # 界定任务边界
    ↓
read-and-locate       # 如果需要发现编辑点（可选）
    ↓
impact-analysis       # 如果爆炸半径不明确（可选）
    ↓
design-before-plan    # ← 新增：设计决策阶段
    ↓
plan-before-action    # 将设计转化为实施计划
    ↓
minimal-change-strategy + 实施
    ↓
self-review           # 审查差异（可选）
    ↓
targeted-validation   # 验证变更
```

### 关键设计决策

#### 1. 方案枚举上限：2-4 种
**理由**：太多方案导致选择瘫痪，太少方案缺乏比较基准。2-4 种覆盖：最小变更、全新设计、渐进式迁移。

#### 2. 只读探索，禁止原型实现
**理由**：防止在设计阶段陷入实现细节。设计文档是决策记录，不是代码。

#### 3. 验收标准必须从需求推导，不能从实现推导
**反例**："测试通过"、"无 lint 错误" — 这些是实现约束，不是需求验证。  
**正例**："100MB 文件上传不触发 OOM"、"网络中断后恢复上传" — 这些可从需求直接验证。

#### 4. 依赖 impact-analysis 的输出
当爆炸半径不明确时，先运行 impact-analysis 得到影响模块清单，再进入 design-before-plan。

---

## 技能组合模式更新

### 补充前的推荐组合
```
scoped-tasking + minimal-change-strategy + plan-before-action + targeted-validation
```

### 补充后的推荐组合

#### 基础模式（无设计决策）
```
scoped-tasking + minimal-change-strategy + plan-before-action + targeted-validation
```

#### 设计模式（涉及方案选择、接口契约、验收标准）
```
scoped-tasking + design-before-plan + plan-before-action + minimal-change-strategy + targeted-validation
```

#### 复杂设计模式（跨模块、爆炸半径不明确）
```
scoped-tasking + read-and-locate + impact-analysis + design-before-plan + plan-before-action + minimal-change-strategy + targeted-validation
```

---

## Escalation 规则

在 CLAUDE.md 中新增：

```markdown
- Escalate to `design-before-plan` when: 
  - The task involves choosing between multiple implementation approaches
  - The change introduces or modifies a public API or cross-module contract
  - Acceptance criteria are missing or unclear
  - scoped-tasking identified the boundary but design decisions remain open
```

## Lifecycle 规则

在 CLAUDE.md 中新增：

```markdown
- Drop `design-before-plan` after the design brief is produced and handed to plan-before-action — it does not stay active during implementation.
```

---

## 示例场景

参见 `examples/design-before-plan-scenario.md`：批量 API 设计任务。

**关键验证点**：
- ✅ Agent 枚举了 3 种设计方案（单独批量端点、扩展现有端点、GraphQL）
- ✅ Agent 记录了选择理由（契约清晰、最小爆炸半径）
- ✅ Agent 定义了完整的接口契约（请求/响应 schema、错误语义）
- ✅ Agent 从需求推导验收标准（"部分失败返回每项错误详情"，而非"返回 200 OK"）
- ✅ Agent 识别了架构约束（rate limiter 必须计数为 1 次请求）

---

## 增强后的覆盖度评估

| 前期设计活动 | 增强后的覆盖 | 技能 |
|-------------|------------|------|
| **需求收集** | 浅层澄清 + 系统性深化 | scoped-tasking Step 0 + design-before-plan Step 1 |
| **需求深化** | **强** | design-before-plan Step 1（含功能/非功能/隐性需求） |
| **隐性需求挖掘** | **强** | design-before-plan Step 1（安全/性能/可观测性/韧性/运维性五维度） |
| **用户故事分析** | 部分覆盖（功能/非功能需求提取） | design-before-plan Step 1 |
| **设计方案比较** | **强** | design-before-plan Step 2-3（含设计模式自然涌现） |
| **接口契约定义** | **强** | design-before-plan Step 4 |
| **数据迁移设计** | **强** | design-before-plan Step 4.5（前向/后向迁移、复杂度评估、验证策略） |
| **验收标准推导** | **强** | design-before-plan Step 5 |
| **架构约束识别** | **较强** | design-before-plan Step 6 + impact-analysis + safe-refactor |
| **技术债务评估** | **轻量级覆盖** | design-before-plan Guardrails（上下文依赖，不阻塞正常流程） |

**关键增强点**：

1. **隐性需求挖掘（P0）** — 最高触发频率的缺口，现已系统化覆盖：
   - Security: 认证/授权/输入验证/加密
   - Performance: 延迟/吞吐量/资源约束/查询优化
   - Observability: 日志/指标/追踪/告警
   - Resilience: 错误处理/重试/熔断/降级
   - Operability: 部署/配置/回滚

2. **数据迁移设计（P0）** — 高触发频率的缺口，现已覆盖：
   - 前向/后向迁移路径
   - 数据量和停机容忍度评估
   - 迁移验证方法（行数/校验和/抽样）
   - 性能影响和风险识别

3. **技术债务评估（P1）** — 中等价值，以 Guardrail 形式轻量级覆盖：
   - 仅在债务阻塞设计或清理能显著简化设计时触发
   - 避免与 minimal-change-strategy 的"不做 drive-by 清理"原则冲突

**结论**：通过增强 design-before-plan，技能库现在覆盖了从需求澄清到实施验证的**完整工作流**，并填补了生产环境中最关键的三个缺口（隐性需求、数据迁移、技术债务）。
