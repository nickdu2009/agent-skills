# 阿里云 DashScope 可用模型列表

## 🔍 如何查看所有可用模型

访问阿里云 DashScope 控制台查看最新模型列表：
https://dashscope.console.aliyun.com/model

---

## 📋 已知可用模型（2024-2025）

### 1️⃣ 通义千问系列（阿里云自研）

| 模型名称 | API调用名 | 缓存类型 | 特点 |
|---------|----------|---------|------|
| 通义千问 Turbo | `qwen-turbo` | 显式 ✅ | 快速、便宜 |
| 通义千问 Plus | `qwen-plus` | 显式 ✅ | 平衡性能 |
| 通义千问 Max | `qwen-max` | 显式 ✅ | 最强推理 |
| 通义千问 Long | `qwen-long` | 显式 ✅ | 超长文本（100万tokens） |
| 通义千问 2.5 Turbo | `qwen2.5-turbo` | 显式 ✅ | 2.5版本快速 |
| 通义千问 2.5 Plus | `qwen2.5-plus` | 显式 ✅ | 2.5版本平衡 |
| 通义千问 2.5 Max | `qwen2.5-max` | 显式 ✅ | 2.5版本最强 |
| 通义千问 3.6 Plus | `qwen3.6-plus` | 显式 ✅ | 3.6版本（当前使用）|

### 2️⃣ 智谱 GLM 系列（阿里云代理）

| 模型名称 | API调用名 | 缓存类型 | 特点 |
|---------|----------|---------|------|
| GLM-4 | `glm-4` | 隐式 ⚠️ | 智谱第4代 |
| GLM-5 | `glm-5` | 隐式 ⚠️ | 智谱第5代 |
| GLM-4 Flash | `glm-4-flash` | 隐式 ⚠️ | 快速版本 |

**注意**: GLM系列仅支持隐式缓存（20%命中成本），且不可控

### 3️⃣ DeepSeek 系列（如果支持）

| 模型名称 | API调用名 | 状态 |
|---------|----------|------|
| DeepSeek Chat | `deepseek-chat` | 需验证 |
| DeepSeek Coder | `deepseek-coder` | 需验证 |

### 4️⃣ 其他可能模型

- Baichuan 系列
- MiniMax 系列（可能需要单独接入）
- 月之暗面 Moonshot 系列（需确认）

---

## ✅ 推荐测试组合

### 方案一：快速对比（4个模型）
```bash
qwen-turbo      # 最便宜
qwen-plus       # 平衡
qwen-max        # 最强
glm-5           # 对比智谱
```

### 方案二：千问系列深度对比（5个模型）
```bash
qwen-turbo      # 快速版
qwen-plus       # 标准版
qwen-max        # 旗舰版
qwen3.6-plus    # 当前基线
qwen-long       # 长文本专用
```

### 方案三：跨厂商对比（6个模型）
```bash
qwen-turbo      # 阿里最便宜
qwen-plus       # 阿里平衡
qwen-max        # 阿里最强
glm-4           # 智谱上代
glm-5           # 智谱最新
deepseek-chat   # DeepSeek（如果支持）
```

---

## 🚀 快速测试方法

### 方法1：编辑脚本选择模型

编辑 `compare_models.sh`，取消注释想要测试的模型：

```bash
# 取消注释以启用
MODELS["glm-5"]="智谱 GLM-5 (隐式缓存)"
MODELS["deepseek-chat"]="DeepSeek Chat"
```

### 方法2：单独测试某个模型

```bash
cd maintainer/scripts/evaluation

# 测试 GLM-5
python run_trigger_tests.py --mode api --compact-mode --enable-cache --model glm-5

# 测试 qwen-max
python run_trigger_tests.py --mode api --compact-mode --enable-cache --model qwen-max
```

### 方法3：批量测试所有模型

```bash
chmod +x compare_models.sh
./compare_models.sh
```

---

## 📊 已知测试结果

| 模型 | 准确率 | Token/case | 缓存类型 | 备注 |
|------|--------|-----------|---------|------|
| qwen3.6-plus | **98.8%** | 1,683 | 显式 | 当前基线 |
| glm-4.7 | 76.8% | 1,403 | 隐式 | Baseline测试 |
| qwen-max | ? | ? | 显式 | 待测试 |
| glm-5 | ? | ? | 隐式 | 待测试 |

---

## 🔗 相关链接

- [阿里云 DashScope 文档](https://help.aliyun.com/zh/dashscope/)
- [模型计费说明](https://help.aliyun.com/zh/dashscope/developer-reference/model-pricing)
- [缓存机制说明](https://help.aliyun.com/zh/dashscope/developer-reference/caching-mechanism)

---

**更新时间**: 2026-04-11  
**维护者**: Claude Code
