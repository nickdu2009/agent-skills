# Skill 测试快速开始

测试分成三层，避免把包合规误当成运行时可用。

## 1. 标准包与引用

```bash
python3 -m pip install PyYAML
python3 maintainer/scripts/analysis/validate_agent_skills.py
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
```

## 2. 客户端无关的内容评测

```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report
python3 maintainer/scripts/evaluation/test_review_loop_output_contract.py
python3 maintainer/scripts/evaluation/test_adr_contract.py
```

这层验证 metadata 路由、Skill 协议和跨 Skill 合同，不证明任何具体运行时已发现 Skill。

## 3. 真实运行时验收

在目标运行时自己的隔离测试项目中验证：

- Skill 可发现。
- 一条明确相关任务能触发。
- 一条相邻但不相关任务不会触发。
- supporting files 能按主文件指令读取。
- 权限、子代理和压缩行为没有破坏输出或停止条件。

记录运行时名称、版本、安装方式、任务原文和可观察结果。运行时差异只保留在测试记录或未来专门适配层中，不写入 portable `SKILL.md`。
