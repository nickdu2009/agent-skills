# 常见工作流
<div class="title-en">Common Workflows</div>

## 为什么有这一章
<div class="title-en">Why This Chapter Exists</div>

使用者最需要的不是技能列表，而是“面对一个具体任务时该怎么走”。

这一章给的是执行主线，不负责替代[技能选择](SKILL-SELECTION.md)的选型说明，也不负责替代[故障排查](TROUBLESHOOTING.md)的排错说明。

## 工作流 1：小范围本地改动
<div class="title-en">Workflow 1: Small Local Change</div>

### 何时使用
<div class="title-en">When to Use</div>

适合局部功能调整、小修小补、单点行为修改。

### 推荐技能
<div class="title-en">Recommended Skills</div>

- `scoped-tasking`
- `plan-before-action`
- `minimal-change-strategy`
- `targeted-validation`

### 如何运行
<div class="title-en">How It Runs</div>

1. 先把任务缩到最小边界，只保留这次真正要完成的那一小块。
2. 在编辑前先形成一个短计划，明确准备改哪些文件、为什么改、准备怎样验证。
3. 按最小可行改动执行，不顺手清理无关代码。
4. 先跑最小充分验证，只确认直接受影响的面。

### 何时停止
<div class="title-en">Stop When</div>

- 边界已经稳定
- 改动只覆盖目标区域
- 局部验证已经能说明这次修改站得住

## 工作流 2：找到正确的编辑点
<div class="title-en">Workflow 2: Find the Right Edit Point</div>

### 何时使用
<div class="title-en">When to Use</div>

适合知道问题大致在哪个模块，但还不知道真正该改哪个文件或哪个符号。

### 推荐技能
<div class="title-en">Recommended Skills</div>

- `scoped-tasking`
- `read-and-locate`
- `plan-before-action`

### 如何运行
<div class="title-en">How It Runs</div>

1. 从当前最强线索开始，例如入口命令、报错位置、已知符号、调用点。
2. 只沿着相邻路径往下追，不做目录级扫读。
3. 把确认位置和待确认线索分开记录。
4. 一旦可能的编辑点已经清楚，就停止继续浏览，切到计划和修改阶段。

### 何时停止
<div class="title-en">Stop When</div>

- 已确认位置已经足够支持下一步
- 待确认线索不再阻碍行动
- 可能的编辑点已经明确

## 工作流 3：缺陷修复
<div class="title-en">Workflow 3: Bugfix</div>

### 何时使用
<div class="title-en">When to Use</div>

适合已经存在错误、异常、失败测试或用户投诉，但根因还不明确的场景。

### 推荐技能
<div class="title-en">Recommended Skills</div>

- `scoped-tasking`
- `read-and-locate`
- `bugfix-workflow`
- `minimal-change-strategy`
- `targeted-validation`

### 如何运行
<div class="title-en">How It Runs</div>

1. 先收集症状和证据，而不是立即猜原因。
2. 缩小故障域，确认问题最可能落在哪个边界。
3. 根因假设有证据支撑后，再做最小修复。
4. 用最小但足够说明问题的验证确认修复成立。

### 何时停止
<div class="title-en">Stop When</div>

- 根因已经被确认，而不只是“看起来像”
- 修复补丁是局部且可解释的
- 验证结果能说明症状已被消除，没有明显引入新问题

## 工作流 4：安全重构
<div class="title-en">Workflow 4: Safe Refactor</div>

### 何时使用
<div class="title-en">When to Use</div>

适合整理结构、提取重复逻辑、降低局部复杂度，但不打算改变对外行为。

### 推荐技能
<div class="title-en">Recommended Skills</div>

- `scoped-tasking`
- `safe-refactor`
- `minimal-change-strategy`
- `self-review`
- `targeted-validation`

### 如何运行
<div class="title-en">How It Runs</div>

1. 先确认目标是结构优化，不是顺便改行为。
2. 明确哪些接口、输入输出、边界条件必须保持不变。
3. 只在局部做可控整理，不扩大成全局清理。
4. 在测试前先做一次自查，再做针对性回归验证。

### 何时停止
<div class="title-en">Stop When</div>

- 结构问题已经得到缓解
- 不变条件仍然成立
- 验证没有显示行为回归

## 工作流 5：并行分析
<div class="title-en">Workflow 5: Parallel Analysis</div>

### 何时使用
<div class="title-en">When to Use</div>

适合多个分析子问题之间边界清楚、彼此低耦合、汇总成本较低的任务。

### 推荐技能
<div class="title-en">Recommended Skills</div>

- `plan-before-action`
- `multi-agent-protocol`
- `conflict-resolution`（必要时）
- `targeted-validation`

### 如何运行
<div class="title-en">How It Runs</div>

1. 先判断任务是否真的适合并行，而不是默认多开代理。
2. 按模块、层次、责任或假设把任务拆成低耦合子问题。
3. 每条子线独立推进，主代理只负责收集结论和证据。
4. 如果子线结论冲突，显式做冲突裁决，而不是直接选一个顺眼的答案。
5. 集成后在交汇点做一次针对性验证。

### 何时停止
<div class="title-en">Stop When</div>

- 每条子线都已给出可汇总结果
- 冲突已被保留或裁决
- 集成验证已完成

## 一个实践提醒
<div class="title-en">A Practical Reminder</div>

这五类流程不是要你每次都完整走一遍，而是帮助你根据任务形态挑出一条最合适的主线。  
对大多数普通任务来说，从“小范围普通改动”或“定位编辑点”开始，通常已经足够。
