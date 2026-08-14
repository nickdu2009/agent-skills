# Architecture design template

```markdown
# 架构设计：<主题>

## 背景、目标与范围
- 业务目标：
- 约束：
- 规模：系统 / 子系统 / 模块

## 方案比较（如适用）
- 方案、优势、代价、复杂度、可逆性
- 选择、理由、牺牲、重访条件

## 架构总览
- 组件/数据流图：
- 依赖方向：

## 组件分解
### <组件>
- 职责与 owner：
- 接口与依赖：
- 技术选择及理由：

## 数据架构
- 业务 truth owner：
- 模型、流向、存储、一致性、生命周期：
- 迁移/共存：

## 接口契约
- 调用方 → 提供方：
- 输入/输出/错误：
- 版本、兼容、owner：

## 非功能与部署
- 失败模式、规模、安全、可观测性、运维：
- 部署拓扑与环境约束：

## ADR 索引
| ID | 标题 | 状态 | Artifact/Path |
|---|---|---|---|

## 风险、约束与待确认假设
- 【假设】内容；依据；影响；blocking；验证/owner decision

## 架构验收标准
- …

## 下一步
- artifact-review-loop(type=design) / implementation-planning
```

Omit deployment only when scale makes it irrelevant. Do not omit truth ownership, interface compatibility, decision lifecycle, blocking assumptions, or acceptance.
