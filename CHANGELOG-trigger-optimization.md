# 触发测试优化变更日志

记录触发测试准确率优化的所有变更。

---

## [v1.0] - 2026-04-11

### ✨ 新增
- 显式缓存支持 (`--enable-cache` 参数)
- 消息结构分离（system + user）
- 技能排序保证一致性

### 🔧 优化
**技能描述优化（8个）**:

#### P0 - 高频失败
- `incremental-delivery`: 明确 2-4 PR 边界，添加 vs phase-plan 排他条件
- `minimal-change-strategy`: 添加"不可逆操作"、"约束性语言"触发词

#### P1 - 阈值优化
- `context-budget-awareness`: 明确"8+ 文件（不是 7）"、"4+ 假设"阈值
- `impact-analysis`: 明确"3+ 调用者（不是 2）"阈值

#### P2 - 边界清晰化
- `read-and-locate`: 强调"BEFORE making changes"，排除纯信息查询
- `scoped-tasking`: 区分"范围不清 vs 位置不清 vs 设计不清"

#### P3 - 特殊场景
- `multi-agent-protocol`: 添加隐式并行识别规则
- `phase-contract-tools`: 强调"ONLY when"元工作场景

### 📊 测试结果
- 准确率: 82.9% → **89.0%** (+6.1%)
- 通过: 68/82 → 73/82 (+5)
- 失败: 9/82 → 6/82 (-3)
- 部分通过: 5/82 → 3/82 (-2)

### 📝 文件变更
```
skills/incremental-delivery/SKILL.md
skills/minimal-change-strategy/SKILL.md
skills/context-budget-awareness/SKILL.md
skills/impact-analysis/SKILL.md
skills/read-and-locate/SKILL.md
skills/scoped-tasking/SKILL.md
skills/multi-agent-protocol/SKILL.md
skills/phase-contract-tools/SKILL.md
maintainer/data/skill_index.json
maintainer/scripts/evaluation/run_trigger_tests.py
```

### 🐛 已知问题
- `multi-file-uncertain`: plan-before-action 仍未触发
- `broad-request-small-surface`: scoped-tasking 未触发（新问题）
- `context-multi-hypothesis`: "4+ 假设"模式未识别
- `locate-vs-scope`: read-and-locate 边界混淆
- `refactor-vs-minimal`: minimal-change-strategy 误触发（新问题）

---

## [v0.1] - 2026-04-11

### ✨ 新增
- 切换到 qwen3.6-plus 模型
- 实现显式缓存（cache_control）
- 添加 `build_eval_messages()` 函数

### 📊 测试结果
- 准确率: 76.8% → 82.9% (+6.1%)
- 模型: GLM-4.7 → qwen3.6-plus

### 💰 成本优化
- 缓存创建: 125% 标准单价（首次）
- 缓存命中: 10% 标准单价（vs 隐式 20%）
- 总成本: ~15% 无缓存成本

---

## [Baseline] - 2026-04-11

### 📊 基线测试
- 模型: GLM-4.7
- 缓存: 隐式（自动）
- 准确率: **76.8%** (63/82)
- 失败: 14/82

### 🔍 主要问题
- 技能边界混淆严重
- 复杂场景判断能力弱
- 阈值判断不准确
- 隐式缓存命中不确定

---

## 路线图

### v1.1 (计划中)
**目标准确率**: 92-95%

**优化重点**:
- [ ] plan-before-action: 添加"uncertainty"关键词
- [ ] scoped-tasking: 强化"多系统单症状"识别
- [ ] context-budget-awareness: 添加"could be X or Y"模式
- [ ] read-and-locate: 强化"Find where"模式

**预期提升**: +3-5%

### v2.0 (未来)
- [ ] 组合触发优化（3+ 技能同时触发）
- [ ] 链式触发规则强化
- [ ] 测试用例补充

---

**维护**: 每次优化后更新此文件  
**格式**: 遵循 [Keep a Changelog](https://keepachangelog.com/)
