# Interview calibration

Read only when a worked conversation helps calibrate question depth.

User: “加一个审批功能。”

Round 1 classifies new feature + workflow + permission, records all three ledgers, and asks: what is approved, whose problem is solved, who submits/approves, and what triggers approval. Maturity: `Insufficient`.

User: “员工提交报销单给主管；金额大的财务再看。”

Round 2 confirms object, roles, and main flow; keeps “主管=直属上级” tentative; asks the amount threshold, rejection behavior, finance handoff, and notification expectation. Maturity: `Mostly clear`.

User: “5000；驳回后可修改重提；财务驳回退员工；通过发站内通知。”

The final result records the four scope buckets and observable acceptance, retains any still-open manager identity question, reaches `Ready for design`, and recommends `design-before-plan`. It does not invent APIs, tables, retries, or fallback behavior.
