# Skill 系统评价

**Status**: Current authority

**Date**: 2026-08-13

## 当前结论

- 12 个标准 Skill 包都位于唯一 canonical `skills/` 树；推荐默认集合是 core 10，`multi-agent-protocol` 与 `manage-agents-md` 为可选包。
- 六个旧评审包已按共同循环合同合并为 `artifact-review-loop`；对象类型通过五个条件 reference 分流，自交付修订只在受信 provenance 与既有写授权同时成立时启用。
- 大主文件已去重并把真正条件化的 catalog、专项检查与 worked examples 下沉，同时保留一个高显著性的硬约束块。
- supporting files 只有在条件读取时才产生实际节省。
- 根 `AGENTS.md` 是仓库内部治理，不进入 Skill 分发。
- 当前 `o200k_base` 基线：完整 discovery 990、全部主文件 18,084、全包上限 24,123；典型激活最大 2,974，重路径最大 3,028 tokens。

## 评价维度

1. metadata 是否能清楚区分相邻 Skill。
2. 主文件是否包含目标、硬约束、执行步骤、输出合同与停止条件。
3. supporting material 是否一层可达且按场景读取。
4. 评审对象、模式、授权来源与写范围是否能稳定路由并保持 fail-closed。
5. 标准格式、catalog、引用、协议、触发、激活预算与 deterministic index 是否都通过。

运行时兼容性不属于本评价；需要时另建基于真实版本的适配评测。
