# 决策原因
<div class="title-en">Decision Rationale</div>

## 目标
<div class="title-en">Goal</div>

这一章不只是告诉使用者“应该怎么选”，而是解释这些常见选择背后的原因。

这一章回答的是“为什么此时更适合选 A，而不是 B”。  
默认你已经知道这套手册的基本方法论和关键机制；如果还没有，建议先读[设计理念](DESIGN-PHILOSOPHY.md)和[关键机制](KEY-MECHANISMS.md)。

## 为什么小任务不该直接上阶段技能
<div class="title-en">Why Small Tasks Should Not Start With Phase Skills</div>

`phase-plan`、`phase-plan-review`、`phase-execute` 这类阶段技能适合的是多波次、多 PR、跨模块、需要正式交接物的大任务。

如果把它们直接用在小任务上，通常会出现反效果：

- 任务本身很小，但协调流程变得很重
- 为了执行一个局部补丁，额外引入波次、工件、审查门
- 使用成本高于实际收益

所以对小任务来说，更合理的默认路径通常是：

- `scoped-tasking`
- `plan-before-action`
- `minimal-change-strategy`
- `targeted-validation`

只有当任务真的跨越多个阶段、多个 PR、多个依赖关系时，这类阶段技能才值得上场。

## 为什么编辑点不明确时要先用 `read-and-locate`
<div class="title-en">Why Use `read-and-locate` When the Edit Point Is Unclear</div>

当编辑点不明确时，最危险的动作就是开始无边界地阅读仓库。

`read-and-locate` 的作用不是“多看一点”，而是“只看足够找到编辑点的那一小段路径”。

之所以优先它，是因为它要求：

- 从最强线索开始
- 只追相邻路径
- 把已确认位置和待确认线索区分开
- 一旦编辑点清楚就停止继续浏览

这能避免任务还没开始真正编辑，工作集就已经膨胀失控。

## 为什么缺陷修复要先证据后修改
<div class="title-en">Why Bugfix Starts With Evidence</div>

缺陷修复先证据后修改，是因为“症状”不等于“根因”。

如果没有先确认故障域，就直接动手修，很容易出现这几种情况：

- 修掉了表面症状，但根因还在
- 修复建立在错误假设上，导致新的回归
- 后续验证只能说明“行为变了”，却不能说明“原因对了”

所以缺陷修复的正确顺序更像是：

1. 收集症状和上下文
2. 缩小故障域
3. 确认根因假设
4. 再做最小修改
5. 再做针对性验证

这会比直接改看起来慢一点，但误修率更低。

## 为什么多代理只适合低耦合任务
<div class="title-en">Why Multi-Agent Fits Only Low-Coupling Tasks</div>

多代理只有在低耦合任务里才真正高效，因为并行节省的是“彼此独立的分析时间”，不是“所有任务都能天然拆分”。

适合并行的典型特征是：

- 子问题边界清楚
- 结果之间依赖少
- 主代理容易做最终汇总

不适合并行的典型特征是：

- 多个子任务共享同一编辑面
- 每个结论都依赖另一条未完成的调查
- 最后需要大量人工裁决才能拼出统一结论

换句话说，多代理不是为了制造更多代理，而是为了只在“低耦合可并行”的地方安全提速。

## 一条简单经验法则
<div class="title-en">A Simple Rule of Thumb</div>

如果你不确定该怎么选，可以先用下面这条顺序判断：

1. 任务边界清楚吗
2. 编辑点清楚吗
3. 根因清楚吗
4. 改动范围真的需要升级吗
5. 子任务之间真的低耦合吗

只要前面的问题还没有回答清楚，就不应该过早跳到更重的机制。
