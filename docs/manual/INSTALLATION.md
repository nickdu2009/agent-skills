# 接入 Agent Skills
<div class="title-en">Use the Standard Packages</div>

本仓库只发布 [Agent Skills 开放标准](https://agentskills.io/specification) 包，不负责客户端安装与治理配置。

## 选择 Skill

从 `skills/` 选择需要的完整目录。每个目录必须保留原有层级：

```text
<skill-name>/
  SKILL.md
  references/       # 若存在
  scripts/          # 若存在
  assets/           # 若存在
  其他 supporting files
```

不要只复制 `SKILL.md`。正文引用的 supporting files 也是包的一部分。

## 交给运行时

按照目标运行时当前文档，把完整 Skill 目录放到它支持的 Agent Skills 位置，或通过它提供的导入功能接入。

以下内容不由开放标准规定，本仓库也不再提供默认值：

- 用户级与项目级发现路径
- 同名 Skill 的优先级
- 显式调用语法与自动触发开关
- 工具权限、子代理与上下文压缩
- 插件、sidecar 与界面元数据

## 从旧安装迁移

迁移已有安装时先备份，再逐包比较：

1. 新位置写入 canonical `skills/<name>/` 的完整副本。
2. 旧副本与 canonical 完全一致时，可以移出旧发现位置。
3. 旧副本有本地改动时，保留并报告差异，不要自动覆盖或删除。
4. 旧治理文件只在可证明是工具生成且内容完全匹配时清理；人工修改内容必须保留。

这个策略避免把“采用标准”误当成删除用户定制的授权。

## 校验仓库包

```bash
python3 -m pip install PyYAML
python3 maintainer/scripts/analysis/validate_agent_skills.py
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
```

运行时是否真正发现、触发和执行 Skill，仍需在该运行时内单独验证。
