# Requirement type calibration

Read only when the request type changes which gaps should be asked first. Types may stack.

| Type | Ask first |
|---|---|
| New feature | Goal, actors, trigger, main flow |
| Existing behavior change | Current vs expected behavior, affected users/data, compatibility |
| Workflow | States, actor per step, transitions, cancellation/rework |
| Permission | Roles, operation granularity, data visibility, denied behavior |
| Data field | Business meaning, requiredness, ownership, historical data |
| Report/query | Metric definition, dimensions, time range, audience, freshness |
| Notification | Trigger, recipients, channel, content, deduplication/frequency |
| Configuration/rule | Subject, condition→action, editor, effective time, conflicts |
| Integration | Responsibilities, data flow, trigger, consistency, failure ownership |
| Exception handling | Exception inventory, expected outcome, manual intervention |

Question examples:

- Prefer “审批对象是报销单、采购单，还是其他对象？” over “请详细描述需求”。
- Convert “金额大的要领导批” into “单笔金额 ≥ X 时由 Y 审批；X/Y remain open” and ask the user to decide X/Y.
- Never infer a retry count, permission fallback, matching threshold, or failure outcome from the type alone.
