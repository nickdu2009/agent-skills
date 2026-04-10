# 使用 z.ai 模型进行触发测试

本文档说明如何使用 z.ai 或其他 OpenAI 兼容 API 来评估技能触发准确性。

## 快速开始

### 1. 配置环境变量

脚本使用 OpenAI SDK 的标准环境变量，兼容所有 OpenAI-compatible 服务（z.ai、vLLM、Ollama 等）。

```bash
# 使用 z.ai
export OPENAI_API_KEY="your-z-ai-api-key"
export OPENAI_BASE_URL="https://api.z.ai/v1"
export OPENAI_MODEL="deepseek-chat"  # 可选，设置默认模型
```

或在项目根目录的 `.env` 文件中配置：

```bash
# .env
OPENAI_API_KEY=your-z-ai-api-key
OPENAI_BASE_URL=https://api.z.ai/v1
OPENAI_MODEL=deepseek-chat  # 可选，设置后无需在命令行指定 --model
```

### 2. 运行触发测试

**查看测试矩阵（无需 API）：**
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report
```

**使用 z.ai 评估：**
```bash
# 如果已设置 OPENAI_MODEL 环境变量，无需指定 --model
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api

# 或者在命令行指定模型（会覆盖环境变量）
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api --model deepseek-chat
```

**测试特定类别：**
```bash
# 仅测试 design-before-plan 相关用例
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --category pre-phase
```

**测试单个用例：**
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --case design-multiple-approaches
```

## 环境变量说明

脚本使用 **OpenAI SDK 兼容的环境变量**：

| 环境变量 | 说明 | 是否必需 | 默认值 |
|---------|------|---------|--------|
| `OPENAI_API_KEY` | API 密钥（OpenAI、z.ai 或其他服务） | ✅ 是 | 无 |
| `OPENAI_BASE_URL` | API 端点（用于非 OpenAI 服务） | 否 | OpenAI 默认端点 |
| `OPENAI_MODEL` | 默认模型名称 | 否 | `gpt-5.4` |

### 为什么使用 OPENAI_* 变量？

OpenAI SDK 原生支持这些环境变量，无需修改代码即可切换到任何 OpenAI 兼容服务：

```python
# OpenAI SDK 自动读取环境变量
from openai import OpenAI
client = OpenAI()  # 自动使用 OPENAI_API_KEY 和 OPENAI_BASE_URL
```

这意味着：
- ✅ 无需维护自定义环境变量（如 `ZAI_API_KEY`）
- ✅ 兼容所有 OpenAI-compatible 服务
- ✅ 与官方 SDK 文档保持一致

## 配置示例

### z.ai 配置

```bash
# .env
OPENAI_API_KEY=your-z-ai-api-key
OPENAI_BASE_URL=https://api.z.ai/v1
OPENAI_MODEL=deepseek-chat
```

配置后，只需运行：
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api
```

### OpenAI 配置

```bash
# .env
OPENAI_API_KEY=sk-...
# OPENAI_BASE_URL 留空，使用 OpenAI 默认端点
```

### 其他 OpenAI 兼容服务

```bash
# vLLM
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=http://localhost:8000/v1

# Ollama (OpenAI 兼容模式)
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1

# Azure OpenAI
OPENAI_API_KEY=your-azure-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
```

## z.ai 推荐模型

| 模型名称 | 说明 | 适用场景 |
|---------|------|---------|
| `deepseek-chat` | DeepSeek 对话模型 | 通用触发测试（推荐） |
| `deepseek-reasoner` | DeepSeek 推理模型 | 需要深度推理的复杂场景 |

请查阅 z.ai 官方文档获取最新模型列表。

## 完整使用示例

### 场景 1：测试所有 design-before-plan 用例

```bash
export OPENAI_API_KEY="your-z-ai-key"
export OPENAI_BASE_URL="https://api.z.ai/v1"

python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --model deepseek-chat \
  --category pre-phase
```

**预期输出：**
```
  Base URL: https://api.z.ai/v1
  Model: deepseek-chat

  ✓ [design-multiple-approaches] pass
  ✓ [design-api-contract] pass
  ✓ [design-unclear-acceptance] pass
  ✓ [design-cross-module-contract] pass
  ✓ [design-not-needed-clear-path] pass
  ✓ [design-not-needed-documented] pass
  ✓ [design-not-needed-bugfix] pass
  ...

Results: 14 pass, 1 partial, 1 fail out of 16 cases
```

### 场景 2：对比 OpenAI 和 z.ai 的触发准确性

```bash
# OpenAI 评估
export OPENAI_API_KEY="sk-..."
unset OPENAI_BASE_URL  # 使用 OpenAI 默认端点
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --model gpt-4 > openai_results.txt

# z.ai 评估
export OPENAI_API_KEY="your-z-ai-key"
export OPENAI_BASE_URL="https://api.z.ai/v1"
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --model deepseek-chat > zai_results.txt

# 对比结果
diff openai_results.txt zai_results.txt
```

### 场景 3：使用自定义端点

通过环境变量或命令行参数设置自定义端点：

```bash
# 方式 1: 环境变量
export OPENAI_BASE_URL="https://your-custom-endpoint.com/v1"
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api --model your-model

# 方式 2: 命令行参数（优先级更高）
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --base-url https://your-custom-endpoint.com/v1 \
  --model your-model-name
```

## 输出解读

### 判定标准

- **✓ Pass** - 完全匹配预期触发列表，无漏报、无误报
- **~ Partial** - 有误触发（False Positive）但没有漏触发
- **✗ Fail** - 有漏触发（False Negative）

### 输出示例

```
  ✓ [design-multiple-approaches] pass
  ✗ [design-api-contract] fail
      FALSE NEGATIVE: expected design-before-plan but not triggered
  ~ [design-unclear-acceptance] partial
      FALSE POSITIVE: scoped-tasking triggered but should not
```

**解释：**
- `design-multiple-approaches` - ✅ 完全正确
- `design-api-contract` - ❌ 应该触发 `design-before-plan` 但没触发（漏报）
- `design-unclear-acceptance` - ⚠️ 错误地触发了 `scoped-tasking`（误报）

## OpenAI vs z.ai 配置对比

| 服务 | OPENAI_API_KEY | OPENAI_BASE_URL | 模型示例 |
|-----|---------------|----------------|---------|
| OpenAI | `sk-...` | 留空（使用默认） | `gpt-4`, `gpt-5.4` |
| z.ai | z.ai 密钥 | `https://api.z.ai/v1` | `deepseek-chat`, `deepseek-reasoner` |
| vLLM | 自定义 | `http://localhost:8000/v1` | 部署的模型名 |
| Ollama | `ollama` | `http://localhost:11434/v1` | `llama2`, `mistral` |

## 故障排查

### 问题：`OPENAI_API_KEY not set`

**解决方案：**
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.z.ai/v1"  # 使用 z.ai 时必需
```

### 问题：API 调用失败

检查以下内容：
1. `OPENAI_API_KEY` 是否正确设置
2. `OPENAI_BASE_URL` 是否可访问（使用 `curl` 测试）
3. 模型名称是否正确（查阅服务提供商文档）
4. API 配额是否充足

**调试建议：**
```bash
# 测试 API 连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     "$OPENAI_BASE_URL/models"

# 先测试单个用例
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --case design-multiple-approaches
```

### 问题：`response_format` 不支持

某些模型可能不支持 `response_format={"type": "json_object"}`。如果遇到此错误，可以：

1. 使用支持 JSON 模式的模型
2. 或修改脚本第 226 行，移除 `response_format` 参数（大多数模型会自动返回 JSON）

## 相关文档

- [触发测试数据定义](../../maintainer/data/trigger_test_data.py)
- [技能协议规范](../../maintainer/data/skill_protocol_v1.py)
- [触发测试脚本](../../maintainer/scripts/evaluation/run_trigger_tests.py)
