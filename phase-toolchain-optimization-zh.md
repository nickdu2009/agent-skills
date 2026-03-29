# Phase Toolchain 优化方案

## 文档目的

本文档沉淀对 `phase-plan`、`phase-execute`、`phase-contract-tools` 这一套工具链的完整优化讨论，并给出最小可实施改造包。

目标不是推翻现有 phase 四文档模型，而是在保留现有使用方式的前提下，补齐这套工具对 external contract 的建模、校验、渲染和执行约束能力，避免执行者把 “execution authority” 误读成 “public API contract authority”。

## 背景问题

当前工具链已经能较好处理以下问题：

- 把大任务拆成多 wave、多 PR 的 execution schema
- 通过 `phaseN-plan.yaml` 统一 phase 执行 authority
- 通过 validator 和 renderer 保证 schema 可消费
- 通过 `phase-execute` 消费 phase 文档并执行

但当前工具链在 external contract 场景下存在结构性缺口：

- `phaseN-plan.yaml` 被定义为 execution authority，但没有配套定义 external contract authority
- planner 可以产出“可执行但 contract 不对齐”的 phase
- executor 可以完成 wave、跑绿 validation、清零 direct-call scan，但仍然交付一个 public contract 偏离外部 spec 的结果
- validator 只能验证 phase schema 是否完整，不能验证 phase 是否把 spec authority 编码进来了
- renderer 能渲染 lane contract，但不能自动把 external contract constraints 带给执行者

## 根因判断

问题的根因不是 wave 拆分能力不足，而是 authority model 不完整。

当前模型只有一层 authority：

- `phaseN-plan.yaml` 是 execution authority

但实际执行需要两层 authority：

- execution authority
- external contract authority

当任务涉及 OpenAPI、YAML 协议、外部 webhook 契约或用户明确点名的 spec 时，如果 external contract authority 没有进入 phase contract，执行者很容易做出“repo-safe 的过渡实现”，而不是“spec-first 的完成实现”。

## 优化目标

本次优化的目标是：

- 保留现有 strict four-file phase doc set
- 保留 `phaseN-plan.yaml` 作为仓库内 execution authority
- 引入 external contract authority 作为一等概念
- 让 planner 必须识别并编码 external contract
- 让 validator 能拒绝 contract-incomplete 的 phase
- 让 renderer 自动把 contract constraints 带给执行者
- 让 executor 在 preflight、done_when 和 wave status 中检查 contract readiness

## 设计原则

1. 不新增新的默认 planning 文档类型。
2. 不引入第二套 execution schema。
3. external contract authority 不能由 phase 执行层覆盖。
4. phase 只能缩小 owned subset，不能用 legacy public shape 替代目标 spec。
5. `fail-closed` 只能表示风险控制，不能表示 contract complete。
6. 对旧 phase 保持兼容，对涉及 public contract 的新 phase 提高约束。

## 目标模型

### 双层 Authority 模型

建议将 authority 明确拆成两层：

- `phaseN-plan.yaml`
  角色：execution authority
  职责：wave、PR、scope、guardrails、validation、merge、status
- external contract
  角色：public contract authority
  来源：OpenAPI、YAML、协议文档、PDF、用户明确点名的 spec
  职责：路径、请求字段、响应字段、webhook shape、owned subset

### Owned Subset 模型

external contract 不是简单的“全量 spec 引入”，而是：

- 必须声明 external contract
- 必须声明当前仓库 owned subset
- 必须声明明确不归仓库负责的 excluded subset

### Accepted Gap 模型

允许存在 gap，但必须显式声明，而不是隐式放过。

gap 需要包含：

- gap id
- 对应 contract
- 对应 scope
- 原因
- 是否 blocking
- 谁接受了这个 gap

## Schema 增量设计

建议在 `phaseN-plan.yaml` 中新增以下字段。

### 顶层字段

```yaml
external_contracts:
  - id: "contract_a"
    path: "some-spec.yaml"
    kind: "openapi"
    authority: "external_contract"
    owned_scope:
      mode: "subset"
      include:
        - "/foo"
        - "/bar"
      exclude:
        - "paths owned by another system"

accepted_contract_gaps: []
```

### PR 级字段

```yaml
prs:
  - id: "P1-07"
    required_contracts:
      - "contract_a"
    contract_guardrails:
      - "Do not substitute legacy route shapes."
      - "Do not reuse legacy DTOs unless they already match the owned spec."
    contract_done_when:
      - "Generated routes align with owned spec paths."
      - "Request and response bindings align with owned spec fields."
```

### Wave Status 字段

```yaml
contract_status:
  state: "aligned"
  checked_contracts:
    - "contract_a"
  blocking_gaps: []
  accepted_gaps: []
```

## 对 `phase-contract-tools` 的优化

`phase-contract-tools` 是本次优化的核心，因为它是 schema、validator、renderer、snapshot 的唯一 contract authority。

### Skill 文本层改造

在 skill 说明中新增 `External Contract Authority` 章节，明确：

- `phaseN-plan.yaml` 是 execution authority，不是 external contract authority
- external contract authority 必须在 phase schema 中被显式声明
- execution phase 可以缩小 owned subset，但不能回退到 legacy public contract
- `fail-closed` 不是 contract complete

### References 层改造

新增参考文档：

- `references/external-contract-authority.md`
- `references/contract-alignment-checklist.md`

补充现有参考：

- `machine-execution-schema.md`
  增加 external contract 相关字段语义
- `schema-consumption-rules.md`
  增加 executor 如何消费 `required_contracts`
- `prompt-derivation-from-schema.md`
  增加 contract constraints 渲染规则
- `wave-status-snapshot.schema.md`
  增加 `contract_status`

### Validator 改造

#### `validate_phase_execution_schema.py`

新增规则：

- 如果 phase 输入中出现明确 spec 文件，plan 必须声明对应 `external_contracts`
- 如果 PR 涉及 public API、webhook、DTO、def-driven route，则必须声明 `required_contracts`
- 如果 PR 声明 `required_contracts`，则必须有 `contract_guardrails`
- 如果 PR 声明 `required_contracts`，则必须有 `contract_done_when`
- 禁止把 `adapter unavailable`、`legacy DTO reuse`、`temporary route alias` 这类状态写成完成态

#### `validate_phase_doc_set.py`

新增规则：

- roadmap 的 `Inputs`、`Outputs`、`Goals`、`Phase Done-When` 必须体现 contract alignment
- roadmap 与 YAML 中对 external contract 的描述必须一致

### Renderer 改造

#### `render_agent_prompt.py`

新增渲染片段：

- external contract authority
- owned subset
- excluded subset
- forbidden substitutions
- accepted contract gaps

#### `render_wave_kickoff.py`

新增渲染片段：

- 本 wave 相关 contract
- contract ownership
- public shape 禁止替代规则

#### `render_lane_handoff.py`

新增渲染片段：

- lane 必须遵守的 contract constraints
- contract-level done checks

#### `render_wave_status_snapshot.py`

新增输出：

- `contract_status.state`
- `checked_contracts`
- `blocking_gaps`
- `accepted_gaps`

### Preflight 改造

#### `preflight_phase_execution.py`

新增 contract gate：

- 本 wave 相关 `required_contracts`
- 当前 contract readiness
- 是否存在 blocking contract gap
- 当前 wave 的 closeout 是否依赖 working adapter

### Smoke Fixture 改造

在 `run_smoke_checks.py` 的 fixture 中新增回归场景：

- phase 引用了 spec，但 plan 未声明 external contract
- PR 只写 compile 和 scan，没有 contract alignment
- closeout 把 fail-closed adapter 作为 done_when
- prompt 未渲染 contract constraints

## 对 `phase-plan` 的优化

planner 的核心变化是：先冻结 authority，再拆 wave。

### Workflow 改造

将 workflow 调整为：

1. 读取 baseline 和设计输入
2. 识别 external contract
3. 冻结 authority matrix
4. 冻结 owned subset 与 excluded subset
5. 写 roadmap
6. 写 YAML
7. 写 wave guide
8. 写 execution index
9. 跑 validators

### 新增 Authority Matrix 步骤

planner 在开始写 phase 之前，必须先确认：

- execution authority
- external contract authority
- owned subset
- excluded subset

### Roadmap 职责增强

`phaseN-roadmap.md` 必须显式写出：

- external contract authority
- owned subset
- excluded subset
- contract alignment goals
- contract alignment success metrics
- contract-complete done-when

### YAML 职责增强

`phaseN-plan.yaml` 必须在以下字段体现 external contract 约束：

- `hard_rules`
- `expected_changes`
- `guardrails`
- `done_when`
- `validation`

### Planner Guardrails 增强

新增 guardrails：

- 不要用 legacy route shape 作为新 public contract 的临时替代
- 不要用 legacy DTO 作为新 public contract 的临时替代，除非与目标 spec 同构
- 不要只写 “generated API exists”，必须写 “generated API aligns with owned spec”
- 不要只写 “router exists”，必须写 “router emits owned webhook contract”
- 不要把 fail-closed adapter 规划成完成态

### Planner Done Criteria 增强

如果 phase 涉及 public API 或 webhook，则 planning pass 只有在以下条件满足时才算完成：

- external contract authority 已识别
- owned subset 已冻结
- 相关 PR 已声明 `required_contracts`
- 相关 PR 已声明 `contract_guardrails`
- 相关 PR 已声明 `contract_done_when`
- closeout 明确区分 `working adapter` 与 `gap`

## 对 `phase-execute` 的优化

executor 的核心变化是：按 phase 做事，但不能偏离 declared external contract。

### Quickstart 改造

在 preflight 中增加 contract 检查：

- 本 wave 涉及哪些 `required_contracts`
- 这些 contract 是否在 YAML 中存在
- owned subset 是否完整
- 当前 wave 是否存在 blocking contract gap

### Manual Fallback 改造

当 preflight helper 缺失时，manual checklist 也必须包含：

- external contract authority 检查
- required_contracts 检查
- contract gaps 检查

manual fallback 不能降级为“只看 execution schema”。

### Execution Guardrails 增强

新增规则：

- 如果实现方案开始偏离 declared external contract，必须停止并返回 planning
- 如果 owned subset 不清楚，必须停止并返回 planning
- 如果 wave done_when 需要 working adapter，不允许用 fail-closed 占位冒充完成
- compile、scan、registration 通过，不代表 contract complete

### Output Contract 增强

执行结果除了 wave state，还必须报告：

- contract checks completed
- blocking contract gaps
- accepted contract gaps
- current contract status
- execution done but contract not done 的情况

### Completion Rule 增强

wave 不得仅凭以下条件判定完成：

- 编译通过
- 注册成功
- direct-call scan 清零

还必须满足：

- `contract_done_when` 已满足
- external contract alignment 未被破坏
- blocking gap 已清零或显式升级

## 最小可实施改造包

建议首轮改造只覆盖最关键的文件和脚本。

### Skill 文件

- `phase-contract-tools/SKILL.md`
- `phase-plan/SKILL.md`
- `phase-execute/SKILL.md`

### References

- `references/external-contract-authority.md`
- `references/contract-alignment-checklist.md`
- `references/machine-execution-schema.md`
- `references/schema-consumption-rules.md`
- `references/prompt-derivation-from-schema.md`
- `references/wave-status-snapshot.schema.md`
- `references/phase-execution-schema-template.yaml`

### Scripts

- `scripts/validate_phase_execution_schema.py`
- `scripts/validate_phase_doc_set.py`
- `scripts/preflight_phase_execution.py`
- `scripts/render_agent_prompt.py`
- `scripts/render_wave_kickoff.py`
- `scripts/render_lane_handoff.py`
- `scripts/render_wave_status_snapshot.py`
- `scripts/run_smoke_checks.py`

### Fixtures

- `fixtures/smoke/*`
- `fixtures/smoke/golden/*`

## 兼容性策略

本次改造应保持对旧 phase 的兼容。

### 对旧 phase 的兼容原则

- 没有声明 external contract 的旧 phase 继续可用
- 如果旧 phase 不涉及 public API 或 webhook，validator 不应强制失败
- 如果旧 phase 涉及 public API 或 webhook，但未声明 external contract，可以先给 warning，再逐步升级为 hard error

### 升级策略

建议分阶段收紧：

1. 新增字段和渲染支持
2. validator 先给 warning
3. 新 phase 默认要求 contract fields
4. 对 public contract phase 升级为 hard error

## 实施顺序

建议按以下顺序改造：

1. 先改 `phase-contract-tools`
2. 再改 `phase-plan`
3. 最后改 `phase-execute`

原因：

- contract layer 是 shared authority
- 如果先改 planner 或 executor，而 contract layer 没改，规则会分散
- renderer 和 validator 先升级后，planner 和 executor 才有稳定的消费面

## 验收标准

改造完成后，系统应能稳定阻止以下错误再次发生：

- 用户点名 spec，但 planner 没把 spec authority 写进 phase
- PR 只写 compile 和 scan，没有 contract alignment done_when
- executor 完成 repo-safe adapter，但没有实现目标 public contract
- closeout 把 `adapter unavailable` 当成完成态

最终验收信号：

- planner 能显式输出 authority matrix
- plan schema 能表达 external contract、owned subset 和 contract gaps
- validator 能拒绝 contract-incomplete 的 phase
- renderer 会自动把 contract constraints 带给执行者
- executor 在 preflight 和 wave completion 时检查 contract readiness
- status snapshot 能区分 execution done 与 contract done

## 非目标

本次优化不做以下事情：

- 不改变 strict four-file 默认 phase doc set
- 不引入第二套 phase schema
- 不把 baseline discovery 迁移到 `phase-contract-tools`
- 不让 `phase-plan` 或 `phase-execute` 各自维护一套 contract 语义
- 不在首轮改造中强制所有历史 phase 全量迁移

## 结论

这套工具链最需要补的不是更多 phase prose，也不是更多波次拆分能力，而是 external contract 的结构化建模能力。

只要把 external contract authority 纳入 shared contract，并让 planner、validator、renderer、executor 都消费同一套字段，现有 phase 模型就足够继续使用，不需要再新增新的默认文档或备用流程。

后续如果进入实施，可直接以本方案作为修 skill、修 references、修 schema、修 validator、修 renderer 的执行输入。
