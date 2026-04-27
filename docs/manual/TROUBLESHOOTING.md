# 故障排查
<div class="title-en">Troubleshooting</div>

## 目标
<div class="title-en">Goal</div>

把使用者最容易卡住的问题集中收敛在一个地方。

如果你现在还在“选择安装路径”或“判断该用哪个技能”的阶段，而不是已经遇到异常或困惑，先回到[安装说明](INSTALLATION.md)或[技能选择](SKILL-SELECTION.md)会更合适。

## 安装问题
<div class="title-en">Installation Problems</div>

### 安装后找不到技能
<div class="title-en">Cannot Find Skills After Installation</div>

先确认你走的是哪一种最终使用者安装方式：

- 全局安装：先跑 `--global --check`
- 项目安装：先看目标项目里是否已有 `AGENTS.md`，再跑 `--project /path/to/my-repo --check`

常见原因：

- 安装命令没有真正完成
- 装到了你没预期的平台目录
- 把全局安装和项目安装的预期结果混在了一起
- 目标项目路径写错了

### 安装后出现重复技能
<div class="title-en">Duplicate Skills After Installation</div>

这通常不是技能本身重复，而是扫描源重复。

常见原因：

- 同时做了全局安装和项目安装
- 同一个项目里残留了多份安装结果
- 不同平台目录中的产物被同时当成有效来源

### 平台没有被正确识别
<div class="title-en">Platform Was Not Detected Correctly</div>

如果自动检测没有落到你预期的平台，可以改用显式平台参数。

例如项目安装时：

```bash
python3 maintainer/scripts/install/manage-governance.py --project /path/to/my-repo --skills-only --platform codex --force
```

如果你只是要确认是否是平台识别问题，先不要一边改规则一边排查，先把安装路径和目标平台单独确认清楚。

## 治理问题
<div class="title-en">Governance Problems</div>

### 为什么 `AGENTS.md` 看起来不像技能手册
<div class="title-en">Why `AGENTS.md` Does Not Look Like a Skill Manual</div>

这是正常的。

`AGENTS.md` 在这个项目里是路由层，不是技能正文。它的职责是：

- 说明什么时候启用哪个技能
- 说明技能之间怎样交接
- 说明什么时候升级、降级或停用

真正的技能细节在各自的 `SKILL.md` 中。

如果你想看这组分层设计的完整解释，去读[关键机制](KEY-MECHANISMS.md)。

### 为什么注入规则后没有达到预期行为
<div class="title-en">Why Injected Rules Did Not Produce the Expected Behavior</div>

先不要直接判断“规则没生效”，先区分是哪一层出了问题：

- 技能没装好
- 治理文件没进入目标项目
- 任务本身没有触发到你期待的技能
- Agent 只完成了结果，没有表现出你期待的过程

如果你是在验证技能行为，不能只看最后答案，还要看执行过程里有没有出现边界控制、计划、最小改动和针对性验证。

### 什么时候该重新生成或同步
<div class="title-en">When to Reinstall or Refresh</div>

以下情况值得重新安装或重新生成：

- 目标项目中的治理文件还是旧版本
- 你切换了平台或目标环境
- 你已经怀疑当前安装结果和目标平台不一致

## 测试问题
<div class="title-en">Testing Problems</div>

### 为什么只看最终答案不足以评估技能
<div class="title-en">Why Final Answers Alone Are Not Enough</div>

因为这套项目的重点不只是“答对”，而是“以更稳定、更可控的方式答对”。

一个结果即使表面正确，也可能仍然没有体现技能想带来的行为改进，例如：

- 没有先缩小范围
- 没有先计划就开始改
- 改动过大
- 验证过宽或过窄

所以评估技能时，要同时看结果和过程。

### 场景测试应该观察哪些行为信号
<div class="title-en">What Behavior Signals to Watch in Scenarios</div>

最值得观察的是：

- 是否先定义了边界
- 是否在编辑前给出计划
- 是否把改动控制在任务范围内
- 是否做了针对性验证
- 在证据不足时是否保留了不确定性

如果你要快速上手场景化验证，可以继续看[技能测试快速开始](../user/SKILL-TESTING-QUICK-START.md)。

### 哪些失败更像安装问题，哪些更像行为问题
<div class="title-en">Installation Failure vs Behavior Failure</div>

更像安装问题的信号：

- 根本找不到技能
- 读不到技能内容
- 平台目录和预期不一致
- 治理文件没有生成或未更新

更像行为问题的信号：

- 技能能被发现，但 Agent 没按预期方式执行
- 技能触发了，但过程里没有体现核心约束
- 最终答案对了，但执行纪律明显跑偏
