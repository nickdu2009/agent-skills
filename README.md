# Agent Execution Skills

本仓库提供一组遵循 [Agent Skills 开放标准](https://agentskills.io/specification) 的编码代理技能，重点覆盖需求澄清、范围收敛、设计、实施规划、缺陷修复、安全重构、影响分析、评审与验证。

## 边界

- 唯一可分发源是 `skills/<name>/`。
- 每个 Skill 由 `SKILL.md` 和同目录下按需读取的 supporting files 组成。
- 仓库不提供客户端安装器、发现路径映射、治理文件生成器、运行时 sidecar 或客户端专属测试。
- 根目录 `AGENTS.md` 仅约束本仓库的维护工作，不属于 Skill 分发内容。

具体客户端如何发现或安装 Agent Skills，请以该客户端当前文档为准；本仓库不假定任何客户端路径或调用语法。

## Skills

仓库包含 12 个标准 Skill 包。推荐默认复制核心 10 个；只有在需要并行委派或维护项目级 `AGENTS.md` 时，再加入两个可选包。该分组只是仓库建议，不改变 Agent Skills 标准包格式。

### 需求、设计与规划

- `requirement-interview`
- `design-before-plan`
- `architecture-design`
- `implementation-planning`

### 执行与验证

- `scoped-tasking`
- `bugfix-workflow`
- `safe-refactor`
- `impact-analysis`
- `artifact-review-loop`
- `targeted-validation`

### 可选：协作与项目治理

- `multi-agent-protocol`
- `manage-agents-md`

## 使用

将所需的完整 Skill 目录交给支持 Agent Skills 标准的运行时。不要只复制 `SKILL.md`；`references/`、模板和其他 supporting files 也可能是技能契约的一部分。

安装位置、冲突优先级、显式调用、自动触发、权限与子代理行为都不属于 Agent Skills 包格式，应由实际运行时决定。

## 本地校验

```bash
python3 -m pip install PyYAML
python3 maintainer/scripts/analysis/validate_agent_skills.py
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report
```

第一项仓库校验器检查开放标准的 frontmatter 约束，并额外要求目录名与 `name` 一致；引用和触发测试属于本仓库自己的内容质量检查。

## 目录

```text
skills/                 # 唯一可分发的 Agent Skills packages
docs/manual/            # 使用说明
docs/user/              # Skill 协议与测试说明
docs/maintainer/        # 客户端无关的维护文档
examples/               # 客户端无关的示例
templates/evaluation/   # 通用评测模板
maintainer/             # 校验、评测数据和报告
AGENTS.md               # 仅供本仓库维护使用
```

维护 Skill 时保持渐进加载：`name` 与 `description` 用于发现，`SKILL.md` 是激活后的主指令，长示例或变体材料只在确有需要时从 supporting files 读取。
