---
name: architecture-design
description: "Guide architecture design for a system, subsystem, or module by producing a structured design document covering component decomposition, data architecture, interface contracts, non-functional design, deployment topology, and ADRs. Includes approach comparison when design direction is not yet settled. WHEN: Use when the user asks for architecture design / system design / technical proposal / 架构设计 / 系统设计 / 出个架构 / 写个技术方案, when a task involves 3+ components or a new subsystem, when technology selection decisions are needed, or when non-functional requirements (scalability, availability, security) require architectural treatment. Do NOT use for single-module internal design choices where design-before-plan suffices, for requirements clarification (use requirement-interview), or for reviewing an existing design doc (use design-review-loop)."
metadata:
  version: "0.1.0"
  tags: "coding, agents, architecture, design, system-design"
---

# architecture-design

Produce a structured architecture design for a system, subsystem, or module. The skill outputs a reviewable architecture design document — not code — covering component decomposition, data architecture, interface contracts, non-functional design, and key architecture decisions with rationale.

# Purpose

Turn a clear requirement or design direction into a concrete, reviewable architecture. Core goals:

- Decompose the system into components with clear responsibilities and dependency directions.
- Design data architecture: models, flow, storage, consistency.
- Define cross-component interface contracts.
- Address non-functional requirements at the architecture level (not as afterthoughts).
- Record architecture decisions with rationale (ADRs) so they are traceable.
- Produce a document that `design-review-loop` can review and `implementation-planning` can consume.

Success criterion: on exit, the architecture document is specific enough for implementation planning without reopening component boundaries, technology choices, or interface contracts.

# When to Use

- The user asks for architecture design / system design / technical proposal / 架构设计 / 系统设计 / 技术方案.
- A task involves building a new system, subsystem, or significant new module.
- The change requires decomposing responsibilities across 3+ components.
- Technology selection decisions are needed (database, messaging, caching, framework, etc.).
- Non-functional requirements (scalability, availability, security, observability) need architectural solutions.
- `design-before-plan` produced a design brief whose `blast_radius` is large and component decomposition is needed.
- Major architecture evolution or migration of an existing system.

# When Not to Use

- Single-module internal design choice with limited blast radius → `design-before-plan`.
- The requirement is still vague → `requirement-interview`.
- An existing architecture document needs review → `design-review-loop`.
- Simple bug fix or small refactor → `bugfix-workflow` / `safe-refactor`.
- The user explicitly says "不用出架构，直接做" → respect the user, give a one-line risk note.

# Scale Judgment

Before starting, judge the task scale to calibrate output depth:

| Scale | Signal | Output depth |
|---|---|---|
| **System-level** | New system / major evolution / 5+ components / cross-service / deployment topology matters | Full architecture document with all sections |
| **Subsystem-level** | New subsystem / 3-4 components / technology selection needed / clear non-functional requirements | Full document, deployment section optional |
| **Module-level** | Single module internal architecture / 2-3 internal layers / no cross-service impact | Lighter document: component decomposition + data architecture + key ADRs; skip deployment and some non-functional sections |

When in doubt, start with the lighter version and expand if the design reveals more complexity.

# Core Rules

- Do not write production code; output is an architecture design document only.
- Decompose before detailing: establish component boundaries first, then dive into each component.
- Every technology choice must have a rationale; do not list names without justification.
- Architecture principles are a validation tool, not a design driver. Design from requirements, then validate against principles. See [reference.md](reference.md) for the principle checklist.
- When principles conflict, record the trade-off explicitly (which principle was prioritized, which was relaxed, and why).
- Do not over-architect: component count and layer depth must match the problem scale.
- Use Mermaid diagrams for architecture visualization when helpful.
- Always run at least one architecture clarification round before starting the design.

# Architecture Information Dimensions

Check each dimension as known / unknown / assumed before designing. These are the standard dimensions for judging architecture readiness and the source pool for clarification questions.

1. **Component boundary preferences（组件边界偏好）**: monolith vs. modular monolith vs. microservices? existing decomposition to extend? preferred granularity?
2. **Technology constraints（技术约束）**: mandated languages, frameworks, platforms, or cloud providers? existing tech stack to align with? vendor lock-in tolerance?
3. **Deployment environment（部署环境）**: on-premise, cloud, hybrid? container/Kubernetes, serverless, VM? CI/CD pipeline constraints?
4. **Non-functional priorities（非功能优先级）**: which matters most — latency, throughput, availability, consistency, security, cost? acceptable trade-offs?
5. **Data characteristics（数据特征）**: read-heavy or write-heavy? data volume and growth rate? real-time or batch? structured or unstructured?
6. **Integration landscape（集成环境）**: which external systems must this integrate with? sync or async? existing API contracts or protocols?
7. **Team structure（团队结构）**: how many teams will own this? team boundaries? Conway's Law alignment considerations?
8. **Scale expectations（规模预期）**: expected user/request/data volume at launch and in 1-2 years? traffic patterns (steady, spiky, seasonal)?
9. **Security & compliance（安全合规）**: authentication/authorization model? data sensitivity (PII, financial, health)? regulatory constraints?
10. **Migration & coexistence（迁移共存）**: greenfield or brownfield? must coexist with legacy systems? migration strategy constraints?

Judgment rules:

- Not all ten must be fully known, but if **component boundary preferences, technology constraints, non-functional priorities, and data characteristics** are all unknown, the architecture generally cannot proceed — ask first.
- Dimensions that are unknown but reasonably assumable should be tagged as assumptions and recorded in the final document's "待确认假设" section.

# Execution Pattern

0. **Check inputs and judge scale**:
   - Collect available requirement doc, design brief, scoped boundary, impact summary.
   - Judge scale (system / subsystem / module) per the Scale Judgment table.
   - If the requirement is unclear, hand off to `requirement-interview`.

1. **Architecture clarification round** (mandatory, at least one round):
   - Scan architecture information dimensions; mark each as known / unknown / assumed.
   - Generate 3-5 questions for the most important unknown dimensions, ordered by impact on architecture decisions.
   - Do not ask requirement-level questions (that belongs to `requirement-interview`).
   - After receiving answers, update dimension status. If key dimensions remain unknown and cannot be reasonably assumed, run another round.
   - No hard cap on rounds; stop when enough dimensions are known or reasonably assumed to support architecture decisions. In practice, 1-2 rounds usually suffice.
   - Tag assumptions explicitly with their basis; assumptions enter the final document's "待确认假设" section, not treated as confirmed facts.

2. **Approach comparison** (if design direction is not settled):
   - List 2-4 candidate architecture approaches.
   - For each: pros, cons, complexity, blast radius, principle alignment.
   - Choose one with explicit rationale; record rejected alternatives in ADR.
   - If direction was already settled upstream, skip this step and note the source.

3. **Component decomposition**:
   - Identify core components and their responsibilities.
   - Define dependency directions (which component depends on which).
   - Validate against structural principles: cohesion, coupling, separation of concerns, single responsibility.
   - Produce a Mermaid component diagram.

4. **Data architecture**:
   - Design core data models and their ownership (which component owns which data).
   - Define data flow between components.
   - Choose storage technology with rationale.
   - Address data consistency strategy (transactions, eventual consistency, saga, etc.).

5. **Interface contract definition**:
   - Define cross-component interfaces: input/output types, error handling, versioning.
   - Validate against interface principles: interface segregation, dependency inversion, encapsulation.

6. **Non-functional architecture** (depth per scale judgment):
   - Scalability: horizontal/vertical scaling strategy, bottleneck analysis.
   - Availability & resilience: failure modes, redundancy, timeout/retry/circuit-breaker.
   - Security: authentication, authorization, data protection, defense in depth.
   - Observability: logging, metrics, tracing injection points.
   - Validate against runtime quality principles.

7. **Deployment architecture** (system-level only):
   - Deployment topology, environment requirements, infrastructure dependencies.

8. **Record ADRs**:
   - Capture key architecture decisions with: context, alternatives, rationale, principle basis, status.

9. **Write or output the architecture design document** (see Output Format).

10. **Recommend next step**:
    - `design-review-loop` when the architecture should be reviewed before planning.
    - `implementation-planning` when the architecture is accepted.

# Input Contract

Provide one or more of:

- a requirement document or requirement-clarification result
- a design brief from `design-before-plan`
- a scoped boundary from `scoped-tasking`
- user's direct architecture task description

Optional but helpful:

- existing system architecture or context
- technology constraints or preferences
- team structure (for Conway's Law alignment)
- non-functional priority ranking

# Output Format

The output format is the skill's deliverable. Templates stay in Chinese following project convention.

## Architecture design document (架构设计文档)

```markdown
# 架构设计：<主题>

## 背景与目标
- 业务背景：…
- 设计目标：…
- 架构约束：…
- 设计规模：系统级 / 子系统级 / 模块级

## 方案比较（如适用）
| 方案 | 优势 | 劣势 | 复杂度 | 原则对齐 |
|---|---|---|---|---|
| 方案 A | … | … | … | … |
| 方案 B | … | … | … | … |

选定方案：… 理由：…

## 架构总览
（Mermaid 组件图 + 文字说明）

## 组件分解
### 组件 A：<名称>
- 职责：…
- 对外接口：…
- 依赖：…
- 技术选型：…（理由：…）
- 设计原则依据：…

### 组件 B：<名称>
- …

## 数据架构
- 核心数据模型：…
- 数据归属：…（哪个组件拥有哪些数据）
- 数据流向：（Mermaid 数据流图）
- 存储选型：…（理由：…）
- 一致性策略：…

## 接口契约
### <接口名称>
- 调用方 → 提供方：…
- 输入/输出：…
- 错误处理：…
- 版本策略：…

## 非功能架构
### 可扩展性
- …
### 可用性与容错
- …
### 安全架构
- …
### 可观测性
- …

## 部署架构（系统级时提供）
- 部署拓扑：（Mermaid 部署图）
- 环境要求：…

## 架构决策记录（ADR）
| 编号 | 决策 | 备选方案 | 原则依据 | 理由 | 状态 |
|---|---|---|---|---|---|
| ADR-1 | … | … | … | … | 已接受 |

## 风险与约束
- 已知风险：…
- 技术债务：…

## 待确认假设
- 【假设】…（依据：…；影响范围：…；若被推翻则：…）

## 验收标准（架构层面）
- …

## 下一步
- 建议：design-review-loop / implementation-planning
```

For module-level scale, omit "部署架构" and simplify "非功能架构" to only relevant dimensions.

# Guardrails

- Do not skip the architecture clarification round. Always scan the information dimensions and ask at least one round before designing.
- Do not code while designing; this skill is read-only exploration and document production.
- Do not over-decompose: if the problem needs 3 components, do not create 8 for "future flexibility".
- Do not pick technologies without rationale ("用 Redis" is not architecture; "用 Redis 因为读多写少、需要亚毫秒延迟且数据可丢失" is).
- Do not skip approach comparison when direction is genuinely open, even if one approach seems obvious.
- Do not mechanically apply every architecture principle. Use principles as validation checks, not design drivers. See [reference.md](reference.md).
- If requirement gaps block architecture decisions, stop and hand off to `requirement-interview` rather than guessing.
- Ask at most 5 questions per clarification round; do not dump all architecture concerns at once.
- Do not treat an assumption as a confirmed fact — tag it and record it in the "待确认假设" section.

# Common Anti-Patterns

- **Technology-first design.** The agent picks a tech stack first and fits components around it, instead of decomposing responsibilities and then selecting appropriate technology per component.
- **Ignoring Conway's Law.** The architecture splits services across boundaries that don't align with team ownership, creating coordination overhead that outweighs the architectural benefit.
- **Non-functional afterthought.** Scalability, security, and observability are added as a last section with vague hand-waving, instead of being architectural first-class concerns that influence component design.
- **Diagram-only architecture.** A pretty Mermaid diagram is produced but component responsibilities, data ownership, and interface contracts are left vague.
- **Principle theater.** Every ADR cites five principles but the actual design doesn't reflect them; principles are used as decoration rather than decision criteria.
- **Premature distribution.** A monolithic design would suffice, but the agent splits into microservices because "that's modern architecture".

Keep anti-pattern guidance self-contained; installed skills must not depend on maintainer-only documents.

# Composition

Position: can be entered directly (for explicit architecture tasks) or after `design-before-plan` (when design brief reveals system-level complexity).

Relationship with `design-before-plan`:
- Parallel, not strictly sequential. Either can be used independently.
- `design-before-plan` focuses on approach selection and interface contracts for bounded changes.
- `architecture-design` produces a full architecture document for system/subsystem/module-level work.
- When both are used: `design-before-plan` provides direction, `architecture-design` expands it into full architecture.
- `architecture-design` includes its own approach comparison capability for cases where it is used independently.

Standard forward handoffs:

- → `design-review-loop`: when the architecture document should be reviewed
- → `implementation-planning`: when the architecture is accepted and execution planning is needed

Standard upstream options:

- `requirement-interview`: clarifies what to build
- `scoped-tasking`: narrows the boundary
- `design-before-plan`: settles design direction (optional, not required)
- `impact-analysis`: clarifies blast radius when shared callers/contracts are involved

Deactivate this skill once the architecture document is produced and handed off downstream.

# Example

Task: "为内部工单系统设计一个通知子系统，需要支持站内信、邮件、企微，后续可能加短信。"

Apply architecture-design (subsystem-level):

**Step 0 — Scale judgment:** subsystem-level — 3-4 components, technology selection needed, clear non-functional needs.

**Step 1 — Architecture dimension scan & clarification round:**

Dimension scan results:
- Component boundary preferences: unknown (monolith extension or independent service?)
- Technology constraints: assumed (工单系统已有 Java + PostgreSQL tech stack)
- Deployment environment: unknown
- Non-functional priorities: partially known (need reliability for notifications, but latency/throughput unclear)
- Data characteristics: unknown (notification volume? retention?)
- Integration landscape: known (站内信/邮件/企微 three channels)
- Team structure: unknown
- Scale expectations: unknown
- Security & compliance: assumed (internal system, no PII in notifications)
- Migration & coexistence: known (greenfield subsystem, must integrate with existing工单service)

This round's questions (3, ordered by impact):
1. 通知子系统是作为工单服务的内部模块，还是独立部署的服务？
2. 预估日均通知量大概多少？（百级/千级/万级）
3. 通知失败时的期望行为？（静默丢弃 / 重试 / 人工处理）

User answers: 独立服务；日均约千级；失败重试，重试多次仍失败则记录日志人工跟进。

Updated dimensions: component boundary → known (独立服务), data characteristics → known (千级/日), non-functional → known (reliability with retry). Remaining unknowns (deployment, team, scale expectations) can be reasonably assumed for this scale. Proceed.

**Step 2 — Approach comparison:**
1. 直接集成：每个通知渠道在工单服务中内联实现。简单，但工单服务膨胀。
2. 独立通知服务 + 消息队列：工单服务发事件，通知服务消费并分发。解耦，但增加基础设施。

选定方案 2，理由：用户要求独立服务；渠道会增加（短信），内联方式每加一个渠道都改工单服务，违反单一职责。

**Step 3 — Component decomposition:**
- 通知服务（核心调度）：接收通知请求，按用户偏好路由到对应渠道适配器
- 渠道适配器（站内信/邮件/企微）：各自封装渠道 SDK 调用
- 通知偏好存储：记录用户的渠道偏好和免打扰规则

**Key ADR:**
- ADR-1: 用消息队列解耦工单服务与通知服务（原则：低耦合、Design for Failure）
- ADR-2: 渠道适配器用策略模式，新渠道只需加适配器（原则：开闭原则、Design for Evolvability）

**待确认假设:**
- 【假设】工单系统已有 Java + PostgreSQL 技术栈（依据：内部系统常见选型；若被推翻则重新评估存储选型）
- 【假设】通知内容不含 PII（依据：工单系统为内部系统；若被推翻则需加加密和审计日志）

Recommend `design-review-loop` before proceeding to `implementation-planning`.

## Contract

### Preconditions

- The requirement is clear enough to make architecture decisions (business goal, main flow, scope boundary are known).
- The task genuinely needs architecture work (not a simple single-file edit).
- The agent can identify 2+ components or layers that need explicit boundary definition.

### Postconditions

- `status: completed` includes `components`, `data_architecture`, `interface_contracts`, `adrs`, and `acceptance_criteria`.
- The document is specific enough for `implementation-planning` to produce an execution plan without reopening component boundaries or technology choices.
- Key architecture decisions are recorded with alternatives and rationale.

### Invariants

- This skill stays read-only; no production code is written.
- Technology choices always have rationale.
- Architecture complexity matches the problem scale.
- Principles are used as validation, not as design drivers.

### Downstream Signals

- `components` defines the decomposition for implementation to follow.
- `data_architecture` grounds data modeling and storage decisions.
- `interface_contracts` gives implementation precise API boundaries.
- `adrs` prevent later phases from unknowingly revisiting settled decisions.

## Failure Handling

### Common Failure Causes

- The requirement is too incomplete to make architecture decisions.
- The technology landscape is unfamiliar and the agent cannot make informed choices.
- Architecture scale is misjudged (treating a module-level task as system-level, or vice versa).

### Retry Policy

- No hard cap on clarification rounds; stop when enough architecture dimensions are known or reasonably assumed.
- If two consecutive rounds produce no new confirmed information (user cannot or will not answer), stop and escalate to the user with the specific blocking dimensions listed.

### Fallback

- Hand off to `requirement-interview` if the requirement is not mature.
- Hand off to `design-before-plan` if only approach selection (not full architecture) is needed.
- Hand off to `impact-analysis` if blast radius is speculative.
- If the user insists on implementing directly, give a risk note and deactivate.

### Low Confidence Handling

- Mark uncertain architecture decisions as provisional in the ADR table.
- Recommend `design-review-loop` before proceeding when confidence is medium or low.

## Output Example

```
[output: architecture-design | completed medium | scale:"subsystem" components:"notification-service, channel-adapters(3), preference-store" tech_choices:"RabbitMQ(async decoupling), PostgreSQL(preference storage)" adrs:"ADR-1:message-queue-decoupling, ADR-2:strategy-pattern-for-channels" | next:design-review-loop]
```

## Deactivation Trigger

- The architecture document is produced and handed off to `design-review-loop` or `implementation-planning`.
- The task is downscaled to a simple design choice that `design-before-plan` can handle.
- The user explicitly asks to skip architecture and implement directly.
