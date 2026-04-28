#!/bin/bash
# 检测阿里云 DashScope 可用模型

API_KEY="${DASHSCOPE_API_KEY:-${OPENAI_API_KEY:-}}"
BASE_URL="${DASHSCOPE_BASE_URL:-${OPENAI_BASE_URL:-https://dashscope.aliyuncs.com/compatible-mode/v1}}"

if [[ -z "$API_KEY" ]]; then
    echo "Error: set DASHSCOPE_API_KEY or OPENAI_API_KEY before running this script." >&2
    exit 1
fi

echo "=================================================="
echo "  检测阿里云 DashScope 可用模型"
echo "=================================================="
echo ""

# 测试模型列表
MODELS_TO_TEST=(
    # 通义千问系列
    "qwen-turbo"
    "qwen-plus"
    "qwen-max"
    "qwen3.6-plus"
    "qwen-long"
    "qwen2.5-turbo"
    "qwen2.5-plus"
    "qwen2.5-max"

    # 智谱 GLM 系列
    "glm-4"
    "glm-5"
    "glm-4-flash"
    "glm-4-plus"

    # DeepSeek 系列
    "deepseek-chat"
    "deepseek-coder"
    "deepseek-v3"

    # Baichuan 系列
    "baichuan-4"
    "baichuan2-turbo"

    # MiniMax 系列
    "abab6.5-chat"
    "abab6.5s-chat"

    # Moonshot 系列
    "moonshot-v1-8k"
    "moonshot-v1-32k"

    # 其他
    "yi-lightning"
    "yi-large"
)

echo "测试简单 prompt，检测模型是否可用..."
echo ""

AVAILABLE_MODELS=()
UNAVAILABLE_MODELS=()

for model in "${MODELS_TO_TEST[@]}"; do
    echo -n "测试 $model ... "

    response=$(curl -s -w "\n%{http_code}" \
        -X POST "$BASE_URL/chat/completions" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$model\",
            \"messages\": [{\"role\": \"user\", \"content\": \"hi\"}],
            \"max_tokens\": 10
        }" 2>&1)

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [[ "$http_code" == "200" ]]; then
        echo "✅ 可用"
        AVAILABLE_MODELS+=("$model")
    else
        error_msg=$(echo "$body" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
        if [[ -z "$error_msg" ]]; then
            error_msg=$(echo "$body" | head -c 100)
        fi
        echo "❌ 不可用 (${error_msg:0:50})"
        UNAVAILABLE_MODELS+=("$model")
    fi

    sleep 0.5
done

echo ""
echo "=================================================="
echo "  检测结果"
echo "=================================================="
echo ""

echo "✅ 可用模型 (${#AVAILABLE_MODELS[@]}):"
for model in "${AVAILABLE_MODELS[@]}"; do
    echo "  - $model"
done

echo ""
echo "❌ 不可用模型 (${#UNAVAILABLE_MODELS[@]}):"
for model in "${UNAVAILABLE_MODELS[@]}"; do
    echo "  - $model"
done

echo ""
echo "=================================================="
echo "建议测试的代表性模型组合："
echo "=================================================="
echo ""

# 分类统计
echo "根据可用模型，推荐以下测试组合："
echo ""

# 从可用模型中筛选代表
declare -A CATEGORIES
for model in "${AVAILABLE_MODELS[@]}"; do
    if [[ $model == qwen-* ]]; then
        CATEGORIES["通义千问"]+="$model "
    elif [[ $model == glm-* ]]; then
        CATEGORIES["智谱GLM"]+="$model "
    elif [[ $model == deepseek-* ]]; then
        CATEGORIES["DeepSeek"]+="$model "
    elif [[ $model == baichuan* ]]; then
        CATEGORIES["Baichuan"]+="$model "
    elif [[ $model == abab* ]]; then
        CATEGORIES["MiniMax"]+="$model "
    elif [[ $model == moonshot-* ]]; then
        CATEGORIES["Moonshot"]+="$model "
    elif [[ $model == yi-* ]]; then
        CATEGORIES["零一万物"]+="$model "
    fi
done

for category in "${!CATEGORIES[@]}"; do
    models=(${CATEGORIES[$category]})
    echo "【$category】: ${models[0]}"
done
