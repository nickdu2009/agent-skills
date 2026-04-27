# 安装说明
<div class="title-en">Installation</div>

## 选择安装模式
<div class="title-en">Choose an Install Mode</div>

这部分的重点不是“把所有命令列出来”，而是先帮助你选对路径。

普通使用者的公开安装入口是 `manage-governance.py`，它面向两种使用方式：

- 全局安装：把技能装到你自己的用户级平台目录
- 项目安装：把技能装到某个具体项目里，并按需要注入治理规则

一个简单判断方法是：

- 想在你自己的机器上跨项目复用这套技能，用全局安装
- 想让某个项目自己携带技能和治理规则，用项目安装

## 全局安装
<div class="title-en">Global Install</div>

### 何时选择
<div class="title-en">When to Choose It</div>

适合以下场景：

- 你主要是个人使用
- 你希望多个项目都能直接复用同一套技能
- 你不想改某个具体项目里的文档或规则文件

### 标准安装
<div class="title-en">Standard Install</div>

```bash
python3 maintainer/scripts/install/manage-governance.py --global
```

### 你会得到什么
<div class="title-en">What You Get</div>

- 技能会安装到用户级平台目录中
- 适合做个人默认技能环境
- 不会往某个具体项目里注入 `AGENTS.md` 或 `CLAUDE.md`

### 首次验证
<div class="title-en">First Validation</div>

建议先做两件事：

- 运行检查命令确认技能已经装到目标平台目录
- 重启对应 Agent，让它重新发现新安装的技能

```bash
python3 maintainer/scripts/install/manage-governance.py --global --check
```

## 项目安装
<div class="title-en">Project Install</div>

### 何时选择
<div class="title-en">When to Choose It</div>

适合以下场景：

- 你希望技能和治理规则一起进入项目
- 你想让 Agent 不只是“能读到技能内容”，还要“知道什么时候该启用什么技能”
- 团队想统一使用方式，而不是每个人各配一套

### 标准安装
<div class="title-en">Standard Install</div>

```bash
python3 maintainer/scripts/install/manage-governance.py --project /path/to/my-repo
```

这条命令的目标是一次性完成两件事：

- 安装完整技能库
- 注入匹配的治理规则

### 项目安装变体
<div class="title-en">Project Variants</div>

以下变体仍然属于项目安装，不是第三条独立安装路径。

#### 仅安装技能
<div class="title-en">Skills Only</div>

如果你只想先装技能，不改项目规则：

```bash
python3 maintainer/scripts/install/manage-governance.py --project /path/to/my-repo --skills-only
```

#### 仅注入规则
<div class="title-en">Rules Only</div>

如果技能已经存在，只想补治理规则：

```bash
python3 maintainer/scripts/install/manage-governance.py --project /path/to/my-repo --rules-only
```

#### 强制指定平台
<div class="title-en">Force a Specific Platform</div>

如果自动检测到的平台不是你想要的目标，可以显式指定：

```bash
python3 maintainer/scripts/install/manage-governance.py --project /path/to/my-repo --skills-only --platform codex --force
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
python3 maintainer/scripts/install/manage-governance.py --project /path/to/my-repo --check
```

## 常见误区
<div class="title-en">Common Pitfalls</div>

### 不要把全局安装和项目安装混成一件事
<div class="title-en">Do Not Confuse Global Install with Project Install</div>

全局安装解决的是“我这台机器默认可用”。  
项目安装解决的是“这个项目自己携带技能和治理规则”。

如果你需要项目内的 `AGENTS.md` 或 `CLAUDE.md`，只做全局安装是不够的。

### 不要把“只装技能”误解成另一条安装路径
<div class="title-en">Do Not Treat Skills Only as a Separate Install Path</div>

`--skills-only` 适合想减少目标项目改动的人，但它不是另一套独立安装体系。  
它仍然属于项目安装的一个变体。
