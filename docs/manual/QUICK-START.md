# 快速开始
<div class="title-en">Quick Start</div>

## 1. 选择最小 Skill 集

- 需求不清：`requirement-interview`
- 范围过大：`scoped-tasking`
- 多方案或契约未定：`design-before-plan`
- 系统级设计：`architecture-design`
- 多文件实施编排：`implementation-planning`
- 缺陷定位与修复：`bugfix-workflow`
- 保持行为的结构调整：`safe-refactor`
- 完成修改后的检查：`artifact-review-loop`（仅在已验证的 `self-delivery` 上下文继承当前任务写权限）+ `targeted-validation`

完整索引见[技能索引](SKILL-INDEX.md)。

## 2. 保留完整包

将选中的 `skills/<name>/` 整个目录交给支持 Agent Skills 标准的运行时。不要拆散 `SKILL.md` 与 supporting files。

运行时路径和调用方式请查该运行时文档；本仓库不提供客户端适配。

## 3. 验证包内容

```bash
python3 -m pip install PyYAML
python3 maintainer/scripts/analysis/validate_agent_skills.py
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
```

## 4. 用真实任务验证

在目标运行时中分别验证：

1. 能发现 Skill。
2. 相关任务会触发正确 Skill。
3. 不相关任务不会误触发。
4. 引用的 supporting files 能按需读取。
5. 输出契约与停止条件仍成立。

仓库内可先运行客户端无关的触发评测：

```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report
```
