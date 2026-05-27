# 安装说明
<div class="title-en">Installation</div>

## 选择安装模式
<div class="title-en">Choose an Install Mode</div>

这部分的重点不是“把所有命令列出来”，而是先帮助你选对路径。

普通使用者的公开安装入口是 `manage-governance.py`。当前推荐的公开语法是 `install` / `verify` 子命令；旧的 repo-local `mirror` 路径已经移除，这份手册以下面这组命令模型为准。

对普通使用者来说，它面向两种安装方式：

- 用户级安装：把技能和治理规则装到你自己的用户级平台目录
- 项目安装：把技能和治理规则装到某个具体项目里

一个简单判断方法是：

- 想在你自己的机器上跨项目复用这套技能和治理规则，用用户级安装
- 想让某个项目自己携带团队共享规则，用项目安装

## 用户级安装
<div class="title-en">User Install</div>

### 何时选择
<div class="title-en">When to Choose It</div>

适合以下场景：

- 你主要是个人使用
- 你希望多个项目都能直接复用同一套技能和治理规则
- 你不想改某个具体项目里的文档或规则文件

### 标准安装
<div class="title-en">Standard Install</div>

```bash
python3 maintainer/scripts/install/manage-governance.py install user
```

### 常用修饰参数
<div class="title-en">Common Modifiers</div>

公开安装契约始终是“整库一起安装”：技能和治理模板会一起处理，不支持只装其中一部分。  
如果你需要调整安装行为，主要使用下面两个修饰参数。

#### 替换已有治理章节
<div class="title-en">Replace Existing Governance Sections</div>

如果目标治理文件里已经有同名章节，默认会跳过；需要替换已有章节时，请加 `--replace-rules`：

```bash
python3 maintainer/scripts/install/manage-governance.py install user --replace-rules
```

#### 覆盖已有技能安装
<div class="title-en">Overwrite Existing Skill Installations</div>

如果你需要覆盖已有的受管技能安装结果，请加 `--overwrite-skills`：

```bash
python3 maintainer/scripts/install/manage-governance.py install user --overwrite-skills
```

### 你会得到什么
<div class="title-en">What You Get</div>

- 技能会安装到用户级平台目录中
- Codex 会获得用户级 `AGENTS.md`
- Claude Code 会获得用户级 `CLAUDE.md`
- Cursor 会获得用户级 skills；治理规则需要手动复制到 Cursor User Rules

### 首次验证
<div class="title-en">First Validation</div>

建议先做三件事：

- 运行检查命令确认技能和用户级治理规则已经装到目标平台目录
- 如果你使用 Cursor，按下文把治理规则复制到 Cursor User Rules
- 重启对应 Agent，让它重新发现新安装的技能

```bash
python3 maintainer/scripts/install/manage-governance.py verify user
```

如果你已经装过旧版治理规则，并希望把模板更新同步到 Codex 或 Claude Code 的已有用户级规则文件，请使用 `--replace-rules`：

```bash
python3 maintainer/scripts/install/manage-governance.py install user --replace-rules
```

## 项目安装
<div class="title-en">Project Install</div>

### 何时选择
<div class="title-en">When to Choose It</div>

适合以下场景：

- 你希望技能和治理规则一起进入项目
- 你想让 Agent 不只是“能读到技能内容”，还要“知道什么时候该启用什么技能”
- 团队想统一使用方式，而不是每个人各配一套
- 你希望规则随仓库走，而不是只存在于某个用户的机器上

### 标准安装
<div class="title-en">Standard Install</div>

```bash
python3 maintainer/scripts/install/manage-governance.py install project /path/to/my-repo
```

这条命令的目标是一次性完成两件事：

- 安装当前支持的技能库
- 注入项目级治理规则

### 常用修饰参数
<div class="title-en">Common Modifiers</div>

项目安装同样始终处理整库内容，不支持把技能和治理模板拆开安装。  
如果自动检测到的平台不是你想要的目标，可以显式指定；如果你还想覆盖已有技能安装，再加 `--overwrite-skills`：

```bash
python3 maintainer/scripts/install/manage-governance.py install project /path/to/my-repo --platform codex --overwrite-skills
```

如果你需要替换项目里的已有治理章节，请加 `--replace-rules`：

```bash
python3 maintainer/scripts/install/manage-governance.py install project /path/to/my-repo --replace-rules
```

### 你会得到什么
<div class="title-en">What You Get</div>

- 安装到相应平台目录中的技能
- 目标项目内的治理文件注入或更新
- 更完整的“技能内容 + 技能路由规则”组合

### 首次验证
<div class="title-en">First Validation</div>

建议检查三件事：

- 目标项目里是否生成或更新了 `AGENTS.md`
- 平台对应的技能安装目录里是否已有技能
- 可以直接运行项目检查命令确认安装结果
- Agent 在真实任务里是否开始表现出更稳定的边界控制、计划和验证习惯

```bash
python3 maintainer/scripts/install/manage-governance.py verify project /path/to/my-repo
```

## 常见误区
<div class="title-en">Common Pitfalls</div>

### 不要把用户级安装和项目安装混成一件事
<div class="title-en">Do Not Confuse User Install with Project Install</div>

用户级安装解决的是“我这台机器默认可用”，现在会同时安装用户级技能和用户级治理规则。  
项目安装解决的是“这个项目自己携带技能和治理规则”，适合团队共享。

如果你需要把 `AGENTS.md` 或 `CLAUDE.md` 提交进某个仓库，只做用户级安装是不够的。

### 不要把安装对象理解成可拆分部件
<div class="title-en">Do Not Treat the Bundle as Separately Installable Parts</div>

这个库的公开安装对象是“整套技能 + 治理模板”，不是可以自由拆开的两个独立部件。  
如果你需要调整已有结果，应使用 `--overwrite-skills` 或 `--replace-rules`，而不是尝试只安装其中一部分。

### Cursor 没有用户级 AGENTS.md
<div class="title-en">Cursor Has No User-Level AGENTS.md</div>

Cursor 官方文档把 `AGENTS.md` 定位为项目根目录或子目录中的规则文件。用户级规则对应的是 Cursor Settings 里的 User Rules，而不是 `~/.cursor/AGENTS.md`。

因此，用户级安装会自动安装 Cursor skills，但不会写入一个非官方的用户级 `AGENTS.md`。如果你希望 Cursor 也使用同一套治理规则，请打开 Cursor Settings -> Rules，把 `templates/governance/AGENTS-template.md` 的主体内容复制到 User Rules 中。更新旧规则时，尤其要确认 `Behavioral Guidelines` §4 包含 `[parallelism: ...]` 执行计划块。

### 公开安装器不再维护本地镜像
<div class="title-en">The Public Installer No Longer Maintains Local Mirrors</div>

公开安装器现在只面向两类目标：用户级安装和项目安装。  
仓库内的 repo-local mirror 体系已经移除，因此普通使用者只需要 `install user`、`install project`、`verify user` 和 `verify project`。
