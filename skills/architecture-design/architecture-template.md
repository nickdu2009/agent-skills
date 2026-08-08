# Architecture design template

Before drafting, classify these dimensions as known, unknown, or assumed:

1. component boundary preferences
2. technology constraints
3. deployment environment
4. non-functional priorities
5. data characteristics
6. integration landscape
7. team ownership
8. scale expectations
9. security and compliance
10. migration and coexistence

Use this document shape:

```markdown
# 架构设计：<主题>

## 背景与目标
- 业务背景：
- 设计目标：
- 架构约束：
- 设计规模：系统级 / 子系统级 / 模块级

## 方案比较（如适用）
- 方案、优势、劣势、复杂度、原则对齐
- 选定方案与理由

## 架构总览
- Mermaid 组件图
- 依赖方向说明

## 组件分解
### <组件>
- 职责：
- 对外接口：
- 依赖：
- 技术选型与理由：

## 数据架构
- 核心数据模型：
- 数据归属：
- 数据流向：
- 存储选型与理由：
- 一致性策略：

## 接口契约
### <接口>
- 调用方 → 提供方：
- 输入/输出：
- 错误处理：
- 版本策略：

## 非功能架构
- 可扩展性：
- 可用性与容错：（先列失败模式评估；具体 timeout/retry/fallback/降级仅在已确认或 Accepted ADR / 架构基线授权后写入）
- 安全：
- 可观测性：

## 部署架构（系统级）
- 部署拓扑：
- 环境要求：

## 架构决策记录（ADR 索引）
| ID | 标题 | 文档状态 | Artifact/Path |
|---|---|---|---|
| ADR-0001 | … | Proposed | … |

## 风险与约束
- 已知风险：
- 技术债务：

## 待确认假设
- 【假设】…（依据：…；影响：…；blocking：true|false；若推翻则：…）
- 行为策略类假设（重试次数、降级路径、匹配阈值、失败语义）默认 `blocking: true`，未确认不得进入下游 planning。

## 验收标准（架构层面）
- …

## 下一步
- design-review-loop / implementation-planning
```
