# 故障排查
<div class="title-en">Troubleshooting</div>

## 先区分三类问题

1. **包问题**：frontmatter、目录名或引用无效。
2. **运行时发现问题**：包正确，但运行时没有列出或加载。
3. **行为问题**：已经触发，但路由、执行或输出不符合契约。

## 包问题

```bash
python3 maintainer/scripts/analysis/validate_agent_skills.py
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
```

常见原因包括：目录名与 `name` 不一致、YAML 类型错误、只复制了 `SKILL.md`、相对引用在移动后失效。

## 运行时没有发现 Skill

检查：

- 是否复制了完整 Skill 目录。
- 是否使用了运行时当前文档支持的发现位置或导入方式。
- 是否需要重启、刷新或重新打开工作区。
- 是否存在同名副本和未公开的优先级冲突。

这些行为不在开放标准内，应以运行时证据为准，不要把某一客户端的结论写进共享 Skill。

## 触发错误

```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report
```

若误触发，优先修正 `description` 的正向触发条件、排除边界与相邻 Skill 区分；不要依赖客户端专属 metadata 掩盖共享描述问题。

## supporting file 未读取

确认 `SKILL.md` 明确写出读取条件和相对路径。避免二跳引用；主文件应直接指向任务需要的 supporting file。

## 旧副本冲突

先备份并递归比较完整目录。完全一致的工具管理副本可以移出旧位置；任何有本地改动的副本都应保留，直到用户决定合并或删除。
