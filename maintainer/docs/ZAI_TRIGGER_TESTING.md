# 使用 z.ai 模型进行触发测试

本文档说明如何使用 z.ai 的模型来评估技能触发准确性。

## 快速开始

### 1. 设置 API 密钥

```bash
# 必需：设置 z.ai API 密钥
export ZAI_API_KEY="your-z-ai-api-key"

# 可选：自定义 API 端点（默认: https://api.z.ai/v1）
export ZAI_BASE_URL="https://api.z.ai/v1"

# 可选：自定义模型（默认: deepseek-chat）
export ZAI_MODEL="deepseek-chat"
```

或者在 `.env` 文件中配置：

```bash
# .env
ZAI_API_KEY=your-z-ai-api-key
ZAI_BASE_URL=https://api.z.ai/v1
ZAI_MODEL=deepseek-chat
```

### 2. 运行触发测试

**查看测试矩阵（不调用 API）：**
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode report
```

**生成手动评估提示词：**
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode prompt
```
复制输出的提示词到 z.ai 聊天界面进行手动测试。

**自动调用 z.ai API 评估：**
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api
```

### 3. 高级用法

**测试特定类别：**
```bash
# 仅测试 pre-phase 类别（包括 design-before-plan）
python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api --category pre-phase

# 其他类别: task-type, agents-md-boundary, discovery, context-budget, multi-agent, phase
```

**测试单个用例：**
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api --case design-multiple-approaches
```

**使用不同模型：**
```bash
# 使用命令行参数覆盖
python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api --model gpt-4

# 使用自定义端点
python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api \
  --base-url https://your-custom-endpoint.com/v1 \
  --model your-model-name
```

## z.ai 支持的模型

常见的 z.ai 模型（2026年4月）：

- `deepseek-chat` - DeepSeek 对话模型（推荐，默认）
- `deepseek-reasoner` - DeepSeek 推理模型
- `gpt-4` - GPT-4（如果 z.ai 提供）
- `claude-3.5-sonnet` - Claude 3.5 Sonnet（如果 z.ai 提供）

请查阅 z.ai 官方文档获取最新的模型列表。

## 输出示例

```
  z.ai Base URL: https://api.z.ai/v1
  Model: deepseek-chat

  ✓ [design-multiple-approaches] pass
  ✗ [design-api-contract] fail
      FALSE NEGATIVE: expected design-before-plan but not triggered
  ~ [design-unclear-acceptance] partial
      FALSE POSITIVE: scoped-tasking triggered but should not

Results: 40 pass, 4 partial, 2 fail out of 46 cases
```

## 判定标准

- **Pass** - 完全匹配预期触发列表
- **Partial** - 有误触发但没有漏触发（False Positive only）
- **Fail** - 有漏触发（False Negative）

## 与 OpenAI API 版本的对比

| 特性 | run_trigger_tests.py | run_trigger_tests_zai.py |
|-----|---------------------|-------------------------|
| API 提供商 | OpenAI | z.ai（OpenAI 兼容） |
| 环境变量 | `OPENAI_API_KEY` | `ZAI_API_KEY` |
| 默认模型 | `gpt-5.4` | `deepseek-chat` |
| Base URL | OpenAI 默认端点 | 可配置（默认 z.ai） |
| 功能 | 完全相同 | 完全相同 |

## 常见问题

**Q: z.ai 不支持 `response_format={"type": "json_object"}` 怎么办？**

A: 如果遇到此错误，可以修改脚本第 213 行，移除 `response_format` 参数。大多数现代模型都能正确返回 JSON 格式。

**Q: 如何调试 API 调用失败？**

A: 脚本会捕获并显示 API 错误。检查：
1. `ZAI_API_KEY` 是否正确设置
2. `ZAI_BASE_URL` 是否可访问
3. 模型名称是否正确
4. API 配额是否充足

**Q: 能否同时运行 OpenAI 和 z.ai 测试进行对比？**

A: 可以，分别运行两个脚本：
```bash
# OpenAI 测试
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api --model gpt-4

# z.ai 测试
python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api --model deepseek-chat
```

## 技术细节

脚本使用 OpenAI SDK 的兼容模式：
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("ZAI_API_KEY"),
    base_url="https://api.z.ai/v1"  # OpenAI 兼容端点
)
```

这使得 z.ai 和其他 OpenAI 兼容服务（如 vLLM, Ollama）都可以使用此脚本。

## 相关文档

- [触发测试数据](../../data/trigger_test_data.py) - 测试用例定义
- [原始触发测试脚本](run_trigger_tests.py) - OpenAI 版本
- [技能协议规范](../../data/skill_protocol_v1.py) - 协议验证规则
