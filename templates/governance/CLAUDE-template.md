# CLAUDE.md

## Multi-Agent Rules

Multi-agent execution has two tiers. Full operational protocol is in the `multi-agent-protocol` skill.

**Tier 1 — Explore (read-only):** The agent may launch read-only subagents at any time without pre-declaration. Each subagent must return structured results; the primary agent must synthesize them.

**Tier 2 — Delegate (write-capable):** Before launching any subagent that may edit files or run mutating commands, the agent must output: `[delegate: <count 2–4> | split: <dimension> | risk: <low|medium|high>]`. If the task cannot be cleanly split, output `[delegate: 0 | reason: <why>]` and stay serial.

**Exemptions:** No declaration needed for single-file edits, direct answers, single commands, or git housekeeping.

## Skill Escalation

These rules define when base-level CLAUDE.md rules are insufficient and the agent should load the full skill.

- Escalate to `minimal-change-strategy` when: the diff is growing beyond what the task requires, multiple edit strategies compete, or surrounding code tempts drive-by cleanup.
- Escalate to `context-budget-awareness` when: the working set exceeds 8 files, the same file has been read more than twice without a new question, more than 3 hypotheses are active without ranking evidence, or the last 3 actions did not advance the stated objective.
- Escalate to `targeted-validation` when: multiple validation options exist and the cheapest meaningful check needs deliberate selection, validation is expensive and the change is local enough for a narrower check, or a validation failure needs diagnosis before broadening coverage.

## Skill Lifecycle

- Load the smallest set of skills that fits the current task.
- Drop `scoped-tasking` and `read-and-locate` once the working set and edit points are confirmed.
- Drop `plan-before-action` once execution is underway and no re-planning is needed.
- Drop `context-budget-awareness` after a successful compression if the session is now compact.
- Keep `minimal-change-strategy` and `targeted-validation` active until the task is complete.
- If the task phase changes (e.g., from diagnosis to implementation), re-evaluate which skills are still providing signal.
- Never carry more than 4 active skills simultaneously without explicit justification.
