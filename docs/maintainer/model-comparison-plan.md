# 多模型对比测试方案

## 📋 测试配置

根据阿里云 DashScope 可用性检测，**每个供应商选一个代表模型**进行对比测试。

---

## ✅ 选定的测试模型（3个）

| 供应商 | 模型 | API名称 | 缓存类型 | 特点 |
|--------|------|---------|---------|------|
| **阿里云** | 通义千问 3.6 Plus | `qwen3.6-plus` | 显式缓存 (10%命中) | 当前基线，平衡性能 |
| **智谱AI** | GLM-5 | `glm-5` | 隐式缓存 (20%命中) | 第三方模型对比 |
| **DeepSeek** | DeepSeek-V3 | `deepseek-v3` | 待确认 | DeepSeek最新模型 |

### ⚠️ 不可用/已移除的模型

**Kimi (月之暗面)**
- 在阿里云 DashScope 上**完全不可用**
- 所有模型名都失败：`kimi-2.5`, `moonshot-v2.5`, `moonshot-v1-8k`, `moonshot-v1-32k` 等
- 如需测试，需单独配置 [Moonshot API](https://platform.moonshot.cn/)

**MiniMax-M2.5**
- ❌ 已从测试中移除
- 原因：API 强制要求 `enable_thinking: true`，与我们的测试配置（`enable_thinking: false`）冲突
- 错误：`The value of the enable_thinking parameter is restricted to True.`
- 测试结果：0% 准确率（全部失败）

---

## 🎯 测试目标

1. **准确率对比**：哪个模型在触发测试中表现最好？
2. **缓存效率对比**：显式缓存 vs 隐式缓存的实际成本差异
3. **跨厂商能力对比**：阿里 vs 智谱 vs DeepSeek

---

## 📊 预期结果

| 模型 | 预期准确率 | 缓存成本 | Token/case | 备注 |
|------|-----------|---------|-----------|------|
| qwen3.6-plus | 98.8% | 10% (显式) | 1,683 | 当前基线 |
| glm-5 | 75-85% | 20% (隐式) | 未知 | 参考GLM-4.7为76.8% |
| deepseek-v3 | 未知 | 未知 | 未知 | 首次测试 |

---

## 🚀 执行命令

### 方式1：自动批量测试（推荐）

```bash
cd maintainer/scripts/evaluation
./compare_models.sh
```

执行后会生成：
- 单个结果：`docs/maintainer/model-comparison/{timestamp}_{model}.txt`
- 汇总报告：`docs/maintainer/model-comparison/{timestamp}_summary.md`

### 方式2：单独测试某个模型

```bash
# 测试智谱GLM-5
python run_trigger_tests.py --mode api --compact-mode --enable-cache --model glm-5

# 测试DeepSeek-V3
python run_trigger_tests.py --mode api --compact-mode --enable-cache --model deepseek-v3
```

### 方式3：对比千问不同档位

如果想对比千问系列的不同档位，编辑 `compare_models.sh` 取消注释：

```bash
# 编辑文件，取消这两行注释：
# MODELS["qwen-max"]="阿里千问Max (最强, 显式缓存)"
# MODELS["qwen-turbo"]="阿里千问Turbo (最便宜, 显式缓存)"
```

---

## 🔍 可用模型检测结果

根据实际API检测（2026-04-11）：

### ✅ 阿里云 DashScope 可用模型 (7个)

| 模型 | 类型 | 状态 |
|------|------|------|
| qwen-turbo | 千问系列 | ✅ 可用 |
| qwen-plus | 千问系列 | ✅ 可用 |
| qwen-max | 千问系列 | ✅ 可用 |
| **qwen3.6-plus** | 千问系列 | ✅ 可用 (当前使用) |
| qwen-long | 千问系列 | ✅ 可用 |
| **glm-5** | 智谱AI | ✅ 可用 |
| **deepseek-v3** | DeepSeek | ✅ 可用 |

### ❌ 不可用模型 (16个)

以下模型在你的账号/区域不可用：
- qwen2.5-turbo, qwen2.5-plus, qwen2.5-max
- glm-4, glm-4-flash, glm-4-plus
- deepseek-chat, deepseek-coder
- baichuan-4, baichuan2-turbo
- abab6.5-chat, abab6.5s-chat (MiniMax)
- moonshot-v1-8k, moonshot-v1-32k (月之暗面)
- yi-lightning, yi-large (零一万物)

---

## 💰 预计成本

基于 82 个测试用例，每个模型约 1,600 tokens/case：

| 模型 | 单价（元/百万Token） | 预计总成本 |
|------|---------------------|-----------|
| qwen3.6-plus | 输入2元，输出12元 | ~2元 |
| glm-5 | 待查询 | ~2-5元 |
| deepseek-v3 | 待查询 | 待确认 |

**总预计成本**: ~5-10元

---

## 📝 后续优化建议

如果某个模型表现优秀（>98.8%），可以考虑：

1. **qwen-max 深度测试**
   - 理论上准确率可能更高
   - 成本是 qwen3.6-plus 的约 25倍
   - 适合生产环境最终验证

2. **qwen-turbo 成本测试**
   - 最便宜的千问模型
   - 如果准确率接近，可节省成本

3. **长文本场景测试**
   - qwen-long (10M上下文)
   - 适合超大代码库分析

---

**创建时间**: 2026-04-11  
**维护者**: Claude Code
