#!/usr/bin/env python3
"""生成多模型对比测试报告"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


def parse_test_result(file_path: Path) -> Dict:
    """解析单个测试结果文件"""
    content = file_path.read_text(encoding='utf-8')

    # 提取模型信息
    model_match = re.search(r'Model:\s+(\S+)', content)
    model = model_match.group(1) if model_match else 'Unknown'

    # 提取 token 信息
    prompt_size_match = re.search(r'Prompt size \(per case\):\s+~(\d+)\s+tokens', content)
    prompt_size = int(prompt_size_match.group(1)) if prompt_size_match else 0

    # 提取缓存类型
    cache_match = re.search(r'Caching:\s+(.*)', content)
    cache_type = cache_match.group(1) if cache_match else 'Unknown'

    # 提取测试结果
    results_match = re.search(r'Results:\s+(\d+)\s+pass,\s+(\d+)\s+partial,\s+(\d+)\s+fail\s+out\s+of\s+(\d+)', content)
    if results_match:
        passed = int(results_match.group(1))
        partial = int(results_match.group(2))
        failed = int(results_match.group(3))
        total = int(results_match.group(4))
        accuracy = (passed / total * 100) if total > 0 else 0
    else:
        passed = partial = failed = total = 0
        accuracy = 0

    # 提取失败用例
    failed_cases = []
    for match in re.finditer(r'[✗~]\s+\[([^\]]+)\]\s+(fail|partial)', content):
        case_id = match.group(1)
        status = match.group(2)
        failed_cases.append(f"{case_id} ({status})")

    return {
        'model': model,
        'prompt_size': prompt_size,
        'cache_type': cache_type,
        'total': total,
        'passed': passed,
        'partial': partial,
        'failed': failed,
        'accuracy': accuracy,
        'failed_cases': failed_cases,
    }


def generate_comparison_report(results_dir: Path, timestamp: str) -> None:
    """生成对比报告"""
    # 查找所有测试结果文件
    result_files = sorted(results_dir.glob(f'{timestamp}_*.txt'))

    if not result_files:
        print(f"未找到测试结果文件: {results_dir}/{timestamp}_*.txt")
        return

    # 解析所有结果
    all_results = []
    for file_path in result_files:
        if file_path.name.endswith('_summary.md'):
            continue
        try:
            result = parse_test_result(file_path)
            all_results.append(result)
            print(f"✓ 解析: {file_path.name} - {result['model']} ({result['accuracy']:.1f}%)")
        except Exception as e:
            print(f"✗ 解析失败: {file_path.name} - {e}")

    if not all_results:
        print("没有成功解析的结果")
        return

    # 按准确率排序
    all_results.sort(key=lambda x: x['accuracy'], reverse=True)

    # 生成 Markdown 报告
    report_path = results_dir / f'{timestamp}_summary.md'

    with report_path.open('w', encoding='utf-8') as f:
        f.write(f"# 多模型对比测试报告\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**测试ID**: {timestamp}\n")
        f.write(f"**测试配置**: compact mode + explicit cache + concurrency 5\n")
        f.write(f"**测试用例数**: {all_results[0]['total'] if all_results else 0}\n\n")

        f.write("---\n\n")
        f.write("## 📊 总体对比\n\n")

        # 生成对比表格
        f.write("| 排名 | 模型 | 准确率 | 通过 | 部分 | 失败 | Token/case | 缓存类型 |\n")
        f.write("|------|------|--------|------|------|------|------------|----------|\n")

        for idx, result in enumerate(all_results, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}"
            f.write(f"| {medal} | {result['model']} | **{result['accuracy']:.1f}%** | "
                   f"{result['passed']}/{result['total']} | {result['partial']} | {result['failed']} | "
                   f"{result['prompt_size']} | {result['cache_type']} |\n")

        f.write("\n")

        # 准确率对比图
        f.write("## 📈 准确率对比\n\n")
        f.write("```\n")
        max_accuracy = max(r['accuracy'] for r in all_results)
        for result in all_results:
            bar_length = int(result['accuracy'] / max_accuracy * 50)
            bar = "█" * bar_length
            f.write(f"{result['model']:20} {bar} {result['accuracy']:.1f}%\n")
        f.write("```\n\n")

        # 详细分析
        f.write("## 📋 详细分析\n\n")

        for result in all_results:
            f.write(f"### {result['model']}\n\n")
            f.write(f"- **准确率**: {result['accuracy']:.1f}%\n")
            f.write(f"- **通过**: {result['passed']}/{result['total']}\n")
            f.write(f"- **部分通过**: {result['partial']}\n")
            f.write(f"- **失败**: {result['failed']}\n")
            f.write(f"- **Prompt大小**: {result['prompt_size']} tokens\n")
            f.write(f"- **缓存类型**: {result['cache_type']}\n")

            if result['failed_cases']:
                f.write(f"\n**未通过用例** ({len(result['failed_cases'])}):\n")
                for case in result['failed_cases']:
                    f.write(f"- {case}\n")
            else:
                f.write("\n✅ **所有用例通过！**\n")

            f.write("\n---\n\n")

        # 推荐建议
        f.write("## 💡 推荐建议\n\n")

        best = all_results[0]
        f.write(f"### 🏆 最佳准确率: {best['model']}\n")
        f.write(f"- 准确率: **{best['accuracy']:.1f}%**\n")
        f.write(f"- 失败用例: {best['failed']} 个\n")

        if best['accuracy'] >= 99.0:
            f.write(f"- ✅ **推荐使用**: 准确率优异\n")
        elif best['accuracy'] >= 95.0:
            f.write(f"- ⚠️ **可接受**: 准确率良好，但有提升空间\n")
        else:
            f.write(f"- ⚠️ **需优化**: 准确率偏低\n")

        f.write("\n### 💰 性价比分析\n\n")
        f.write("根据准确率和成本综合考虑：\n\n")

        # 简单的性价比评分（这里需要实际价格数据）
        price_map = {
            'qwen-turbo': 1,
            'qwen-plus': 3,
            'qwen3.6-plus': 3,
            'qwen-max': 25,
            'qwen-long': 5,
        }

        for result in all_results:
            model = result['model']
            price_factor = price_map.get(model, 1)
            value_score = result['accuracy'] / price_factor

            if value_score > 30:
                rating = "🌟🌟🌟 极佳"
            elif value_score > 20:
                rating = "🌟🌟 良好"
            else:
                rating = "🌟 一般"

            f.write(f"- **{model}**: {rating} (准确率 {result['accuracy']:.1f}% / 相对成本 {price_factor}x)\n")

        f.write("\n---\n\n")
        f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"\n✅ 报告已生成: {report_path}")


def main():
    if len(sys.argv) < 3:
        print("用法: python generate_model_comparison_report.py <results_dir> <timestamp>")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    timestamp = sys.argv[2]

    if not results_dir.exists():
        print(f"结果目录不存在: {results_dir}")
        sys.exit(1)

    generate_comparison_report(results_dir, timestamp)


if __name__ == '__main__':
    main()
