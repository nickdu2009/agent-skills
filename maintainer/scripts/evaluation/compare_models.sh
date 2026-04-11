#!/bin/bash
# 多模型对比测试脚本
# 用法: ./compare_models.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/../../../docs/maintainer/model-comparison"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# 创建结果目录
mkdir -p "$RESULTS_DIR"

echo "=================================================="
echo "  多模型对比测试"
echo "=================================================="
echo "开始时间: $(date)"
echo "结果目录: $RESULTS_DIR"
echo ""

# 定义要测试的模型列表
# 每行格式: "模型名称|描述"
MODELS=(
    "qwen3.6-plus|阿里千问3.6-Plus (当前基线, 显式缓存10%)"
    "glm-5|智谱GLM-5 (隐式缓存20%)"
    "deepseek-v3|DeepSeek-V3"
)

# 测试每个模型
for model_entry in "${MODELS[@]}"; do
    # 分割模型名和描述
    IFS='|' read -r model description <<< "$model_entry"

    echo "--------------------------------------------------"
    echo "测试模型: $model - $description"
    echo "--------------------------------------------------"

    # 设置输出文件
    OUTPUT_FILE="$RESULTS_DIR/${TIMESTAMP}_${model}.txt"

    # 运行测试
    echo "执行中..."
    python "$SCRIPT_DIR/run_trigger_tests.py" \
        --mode api \
        --compact-mode \
        --enable-cache \
        --model "$model" \
        --concurrency 5 \
        2>&1 | tee "$OUTPUT_FILE"

    echo "✓ 完成，结果保存至: $OUTPUT_FILE"
    echo ""

    # 短暂延迟，避免API限流
    sleep 2
done

echo "=================================================="
echo "  所有测试完成"
echo "=================================================="
echo "结束时间: $(date)"
echo ""

# 生成汇总报告
echo "正在生成汇总报告..."
python "$SCRIPT_DIR/generate_model_comparison_report.py" "$RESULTS_DIR" "$TIMESTAMP"

echo ""
echo "✅ 所有测试完成！"
echo "查看结果: $RESULTS_DIR/${TIMESTAMP}_summary.md"
