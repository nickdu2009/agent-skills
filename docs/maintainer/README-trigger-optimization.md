# 触发测试优化文档导航

快速访问触发测试优化的所有相关文档。

---

## 🎯 当前状态

| 指标 | 值 |
|------|-----|
| **最新版本** | v1.0 |
| **准确率** | **89.0%** (73/82) |
| **上次更新** | 2026-04-11 |
| **测试配置** | qwen3.6-plus + 显式缓存 |

**进展**:
```
Baseline (GLM-4.7):     76.8%
v0.1 (qwen3.6-plus):    82.9% (+6.1%)
v1.0 (优化 8 技能):      89.0% (+6.1%) ← 当前
目标 (v1.1):            92-95%
```

---

## 📚 文档索引

### 核心文档

1. **[优化追踪器](./trigger-test-optimization-tracker.md)** 🔥
   - 完整的优化历史记录
   - 每轮优化的详细分析
   - 剩余问题根因分析
   - 下一步计划

2. **[变更日志](../../CHANGELOG-trigger-optimization.md)**
   - 简洁的版本变更记录
   - 按时间倒序排列
   - 遵循 Keep a Changelog 格式

3. **[优化方案](./skill-description-optimization-plan.md)**
   - P0-P3 优化方案详解
   - 每个技能的优化前后对比
   - 预期影响评估

4. **[结果报告](./skill-optimization-results.md)**
   - v1.0 优化结果分析
   - 成功修复的用例列表
   - 剩余问题统计

5. **[LLM 缓存验证](./llm-cache-verification-report.md)**
   - 显式缓存 vs 隐式缓存
   - qwen3.6-plus vs GLM-4.7
   - 成本效益分析

### 脚本文件

- **[测试脚本](../../maintainer/scripts/evaluation/run_trigger_tests.py)**
  - 支持显式缓存
  - 并发测试
  - 多种输出模式

- **[测试数据](../../maintainer/data/trigger_test_data.py)**
  - 82 个测试用例
  - 12 个分类
  - 期望触发规则

---

## 🚀 快速开始

### 运行测试

```bash
# 全量测试（推荐配置）
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --compact-mode \
  --enable-cache \
  --concurrency 5

# 测试单个用例
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --compact-mode \
  --enable-cache \
  --case incremental-multi-pr-task

# 测试特定分类
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --compact-mode \
  --enable-cache \
  --category task-type
```

### 配置说明

**推荐配置** (.env):
```bash
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen3.6-plus
OPENAI_EXTRA_BODY={"enable_thinking":false}
```

**关键参数**:
- `--compact-mode`: 使用 skill_index.json（减少 60-80% tokens）
- `--enable-cache`: 显式缓存（命中仅 10% 费用）
- `--concurrency 5`: 5 倍并发加速

---

## 📊 优化工作流

### 1. 分析失败用例
```bash
# 查看失败详情
grep "✗\|~" test_output.txt

# 分析根因
vim docs/maintainer/trigger-test-optimization-tracker.md
```

### 2. 优化技能描述
```bash
# 编辑技能描述
vim skills/<skill-name>/SKILL.md

# 重新生成索引
python3 maintainer/scripts/analysis/generate_skill_index.py
```

### 3. 验证优化效果
```bash
# 测试特定失败用例
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --compact-mode \
  --enable-cache \
  --case <failed-case-id>

# 全量回归测试
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --compact-mode \
  --enable-cache \
  --concurrency 5
```

### 4. 记录结果
```bash
# 更新追踪器
vim docs/maintainer/trigger-test-optimization-tracker.md

# 更新变更日志
vim CHANGELOG-trigger-optimization.md

# 提交更改
git add skills/*/SKILL.md maintainer/data/skill_index.json
git commit -m "feat: optimize skill descriptions (vX.X)"
```

---

## 🔍 问题排查

### 准确率下降
1. 检查 skill_index.json 是否最新
2. 验证 .env 配置（模型、缓存）
3. 对比历史测试结果

### 缓存未命中
1. 确认使用 `--enable-cache`
2. 检查模型是否支持显式缓存（qwen3.6-plus ✅, GLM-4.7 ❌）
3. 查看 API 返回的 `usage.prompt_tokens_details.cached_tokens`

### 新用例失败
1. 检查是否为边界情况
2. 分析与现有失败用例的相似性
3. 记录到追踪器的"剩余问题"部分

---

## 📈 优化原则

### 描述优化四原则

1. **数字阈值明确化**
   - ❌ "many files" 
   - ✅ "8+ files (not 7)"

2. **排他条件强化**
   - ❌ "Use when X"
   - ✅ "ONLY use when X, NOT when Y"

3. **关键词触发**
   - 添加用户常用表达
   - "don't change", "in parallel", "which search?"

4. **反例补充**
   - 每个描述包含 "Do NOT use when"
   - 特别是易混淆技能

---

## 🎯 里程碑

- [x] Baseline: 76.8% (GLM-4.7)
- [x] v0.1: 82.9% (模型切换 + 缓存)
- [x] v1.0: 89.0% (8 技能优化)
- [ ] v1.1: 92-95% (第二轮优化)
- [ ] v2.0: 95%+ (组合触发)

---

## 👥 贡献指南

### 添加新测试用例

1. 编辑 `maintainer/data/trigger_test_data.py`
2. 添加到对应分类（TASK_TYPE_CASES, BOUNDARY_CASES 等）
3. 运行测试验证
4. 更新文档

### 优化技能描述

1. 在追踪器中记录问题根因
2. 设计优化方案
3. 修改 SKILL.md frontmatter
4. 重新生成 skill_index.json
5. 验证效果
6. 更新文档

---

## 📞 联系

**问题反馈**: 在 GitHub Issues 中创建  
**文档维护**: Claude Code  
**最后更新**: 2026-04-11

---

**快速链接**:
- [完整追踪器](./trigger-test-optimization-tracker.md) ← 从这里开始
- [最新变更](../../CHANGELOG-trigger-optimization.md)
- [测试脚本](../../maintainer/scripts/evaluation/run_trigger_tests.py)
