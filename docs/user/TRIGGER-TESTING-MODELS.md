# 触发测试模型选择指南

本文档说明如何为技能触发测试选择最佳 GLM 模型配置（速度与成本平衡）。

## 推荐配置总结

| 平台 | 模型 | extra_body 参数 | 平均速度 | 成本 |
|------|------|----------------|---------|------|
| **阿里云 DashScope** | `glm-4.7` | `{"enable_thinking":false}` | **~1s** | 低 |
| **z.ai** | `GLM-5-Turbo` | 无需配置（默认） | ~6s | 中 |
| **z.ai** | `GLM-5.1` | `{"thinking":{"type":"disabled"}}` | ~5s | 中高 |

## 平台差异说明

### 阿里云 DashScope（推荐）

**优势：**
- 速度极快：`glm-4.7 + enable_thinking=false` 只需 ~1 秒
- 成本较低
- 国内访问稳定

**劣势：**
- 模型选择少（只有 `glm-4.7` 和 `glm-5`）
- `glm-5` 关闭推理效果不明显，不推荐

**配置示例：**
```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_MODEL="glm-4.7"
export OPENAI_EXTRA_BODY='{"enable_thinking":false}'
```

### z.ai（备选）

**优势：**
- 模型选择多（GLM-4.5/4.6/4.7/5/5.1/5-Turbo 等）
- `GLM-5-Turbo` 无需额外配置即可获得较快速度
- Coding Plan 套餐可用

**劣势：**
- 速度比阿里云慢（6 秒 vs 1 秒）
- 偶尔 429 限流（免费模型或余额不足）
- 某些模型需要手动关闭推理

**配置示例 1（推荐）：**
```bash
export OPENAI_API_KEY="your-z-ai-key"
export OPENAI_BASE_URL="https://api.z.ai/v1"
export OPENAI_MODEL="GLM-5-Turbo"
# 无需 OPENAI_EXTRA_BODY
```

**配置示例 2（最快但偶尔失败）：**
```bash
export OPENAI_API_KEY="your-z-ai-key"
export OPENAI_BASE_URL="https://api.z.ai/v1"
export OPENAI_MODEL="GLM-5.1"
export OPENAI_EXTRA_BODY='{"thinking":{"type":"disabled"}}'
```

## 推理参数说明

### 阿里云 `enable_thinking`

| 值 | 效果 | 触发测试推荐 |
|----|------|-------------|
| `false` | 关闭推理，直接输出答案 | ✅ 推荐（提速 10 倍） |
| `true` | 开启推理（生成 reasoning_content） | ❌ 不推荐（慢且浪费 tokens） |
| 未设置 | 默认开启推理 | ❌ 不推荐 |

### z.ai `thinking.type`

| 值 | 效果 | 触发测试推荐 |
|----|------|-------------|
| `"disabled"` | 关闭推理 | ✅ 推荐（GLM-5.1 专用） |
| `"enabled"` | 开启推理 | ⚠️ GLM-5.1 可能过度触发 |
| 未设置 | 不同模型默认不同 | ⚠️ 看具体模型 |

**注意：** z.ai 的 `budget_tokens` 参数**无效**（实测被忽略），只有 `type: disabled/enabled` 两档。

## 实测数据（单个 case）

### 阿里云 DashScope

| 模型 | enable_thinking | 耗时 | 触发准确 |
|------|----------------|------|---------|
| `glm-4.7` | `false` | **0.93s** | ✅ |
| `glm-4.7` | `true` | 10.13s | ✅ |
| `glm-5` | `false` | 29.21s | ✅ |
| `glm-5` | `true` | 35.59s | ✅ |

### z.ai

| 模型 | thinking.type | 耗时 | 触发准确 |
|------|--------------|------|---------|
| `GLM-5-Turbo` | 默认 | **3~9s** | ✅ |
| `GLM-5.1` | `disabled` | **~5s** | ✅ |
| `GLM-5.1` | 默认 enabled | 14~28s | ⚠️ 偶尔多触发 |
| `GLM-4.6` | 默认 | 4~48s | ✅（波动大） |

## 全量测试（74 cases）预估

| 配置 | 单 case 耗时 | 74 cases 总耗时 |
|------|-------------|---------------|
| **阿里云 glm-4.7 (thinking=false)** | ~1s | **~1-2 分钟** |
| z.ai GLM-5-Turbo | ~6s | ~7-8 分钟 |
| z.ai GLM-5.1 (disabled) | ~5s | ~6-7 分钟 |

## 快速开始

### 方式 1：使用 .env 文件

复制 `.env.example` 到 `.env`，取消注释对应平台配置：

```bash
cp .env.example .env
# 编辑 .env，取消注释阿里云或 z.ai 配置块
```

### 方式 2：直接设置环境变量

```bash
# 阿里云（最快）
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_MODEL="glm-4.7"
export OPENAI_EXTRA_BODY='{"enable_thinking":false}'

# 运行测试
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api
```

## 故障排查

### 问题：速度很慢

**检查：** 是否忘记设置 `OPENAI_EXTRA_BODY` 关闭推理？

```bash
# 验证当前配置
python3 -c "import os; print('EXTRA_BODY:', os.getenv('OPENAI_EXTRA_BODY'))"
```

### 问题：阿里云报 404 模型不存在

**原因：** 模型名大小写错误。阿里云用小写 `glm-4.7`，z.ai 用大写 `GLM-5-Turbo`。

### 问题：z.ai 报 429 错误

**可能原因：**
1. 余额不足（如 GLM-4.5-AirX、GLM-4-32B）
2. 免费模型被限流（GLM-4.7-Flash、GLM-4.5-Flash）
3. 临时过载

**解决：** 切换到付费稳定模型（GLM-5-Turbo 或 GLM-4.6）

## 相关文档

- [触发测试数据定义](../../maintainer/data/trigger_test_data.py)
- [触发测试脚本](../../maintainer/scripts/evaluation/run_trigger_tests.py)
- [z.ai 触发测试文档](TRIGGER-TESTING-ZAI.md)
