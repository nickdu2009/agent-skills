---
name: read-and-locate
description: Find the relevant files, code paths, and edit points in an unfamiliar area of the codebase when the agent must trace a runtime, data, ownership, or configuration path. Use when module is known but exact file is unknown, or must locate where a feature is implemented. Triggers on "Find where", "locate implementation", or "somewhere in X module" patterns. Do not use for reference searches or pure information queries without edit intent.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Teach the agent to understand only the amount of code needed to move the task forward. The skill emphasizes narrow discovery, explicit evidence, and early stopping once the likely edit surface is known.

# When to Use

- When the codebase is unfamiliar.
- When the relevant file or module is not known yet.
- When the agent needs to trace a call path, data path, or ownership boundary.
- Before a bugfix or small feature change in an unfamiliar area.

# When Not to Use

- When the exact edit file is already known.
- When an exact symbol, class, function, or file search is enough to find the edit surface.
- When the user asks for a broad architectural survey.
- When the task is analysis of one already-open file with no discovery needed.

# Core Rules

- Start from the most relevant entry points.
- Prefer narrow discovery over broad repository exploration.
- Identify likely files, modules, call paths, and boundaries first.
- Stop exploring once enough evidence is gathered for the next step.
- Distinguish confirmed locations from tentative leads.
- Do not treat every interesting file as part of the required working set.

# Execution Pattern

1. Start from the strongest clue: endpoint, command, stack trace, test, symbol, or file path.
2. Identify the first likely entry point.
   - Runtime path: follow function calls and control flow.
   - Data path: follow data transformations and storage boundaries.
   - Ownership path: follow module boundaries and responsibility seams.
   - Configuration path: follow config loading, overrides, and environment resolution.
3. Trace only the adjacent call path or ownership path.
4. Mark each discovered file as confirmed location or tentative lead.
5. Stop once the likely edit points and validation surface are clear.
6. Hand off to planning or editing without continuing to browse for curiosity.

# Input Contract

Provide:

- the objective
- the strongest available clue
- the kind of path to trace: runtime, data, ownership, or configuration

Optional but helpful:

- suspected modules
- recent failing commands

# Output Contract

Return:

- confirmed locations
- tentative leads
- likely edit points
- relevant boundaries or ownership seams
- what remains unknown but does not block the next step

# Guardrails

- Do not start with repo-wide reading.
- Do not read entire directories when one or two files can establish the path.
- Do not trigger when grep, find-references, or one exact symbol lookup is sufficient.
- Do not keep exploring after the next action is already clear.
- Do not present tentative leads as confirmed facts.
- If the first clue is weak, say so and choose the narrowest next-best clue.

# Common Anti-Patterns

- **Reading every file in the directory.** The agent opens all files in `src/billing/` sequentially instead of starting from the invoice generation entry point and tracing one call path. Most files turn out to be irrelevant.
- **Continuing to explore after the edit point is clear.** The agent already identified the serializer boundary but keeps browsing neighboring modules "just in case," wasting context on files that will not be touched.

See skill-anti-pattern-template.md for format guidelines.

# Composition

Part of the `bugfix-standard` chain (see CLAUDE.md § Skill Chain Triggers).

Standard forward flow: receives boundary from `scoped-tasking`, produces edit points, hands to `plan-before-action` or `bugfix-workflow`.

Additional compositions:

- `context-budget-awareness` to avoid carrying every discovered branch forward when discovery produces too many tentative leads

# Example

Task: "Add an audit field to generated invoices."

A good discovery sequence is:

- start from the invoice generation command or endpoint
- locate the service that builds invoice payloads
- identify the serializer or template boundary
- confirm where persistence happens

Stop once the generation path and serialization boundary are clear. Do not survey every billing file just because they look related.

## Contract

### Preconditions

- The relevant edit point is not yet known.
- The task has at least one strong clue that can anchor a narrow discovery path.
- Simple exact lookup is not sufficient to finish discovery.

### Postconditions

- `status: completed` includes `entry_points`, `candidate_files`, and `edit_points`.
- Confirmed locations are separated from tentative leads.
- The validation surface is clear enough to hand off to planning or diagnosis.

### Invariants

- Discovery remains local to the traced runtime, data, ownership, or configuration path.
- Curiosity-driven browsing stops once the next action is clear.
- Tentative leads are never presented as confirmed edit locations.

### Downstream Signals

- `entry_points` tell downstream skills where the traced path starts.
- `candidate_files` narrows the remaining search surface.
- `edit_points` identify the likely mutation or review surface for the next skill.

## Failure Handling

### Common Failure Causes

- The strongest clue is too weak to establish a reliable path.
- Adjacent paths branch too widely to keep discovery local.
- A direct symbol/path lookup would have been sufficient but was not available at first.

### Retry Policy

- Allow one shift to the next-best clue when the first clue dead-ends.
- If the second clue still fails to produce likely edit points, stop and request stronger input.

### Fallback

- Hand off to `scoped-tasking` if the discovery surface itself is too broad.
- Hand off to `bugfix-workflow` when the real goal is to isolate a fault domain rather than locate an edit point.
- Escalate to the user for a stronger clue when discovery would otherwise become repo-wide.

### Low Confidence Handling

- Mark files as tentative and require downstream confirmation before editing.
- Prefer a short list of uncertain candidates over an inflated list of weak leads.

## Output Example

```yaml
[skill-output: read-and-locate]
status: completed
confidence: medium
outputs:
  entry_points:
    - "invoice generation endpoint"
  candidate_files:
    - "billing/invoice_service.py"
    - "billing/invoice_serializer.py"
  edit_points:
    - "InvoiceSerializer.build_payload"
signals:
  validation_surface:
    - "invoice generation test fixture"
recommendations:
  downstream_skill: "plan-before-action"
[/skill-output]
```

## Deactivation Trigger

- Deactivate once a downstream skill has consumed the likely edit points.
- Deactivate when discovery concludes that the exact symbol lookup or user clarification is now sufficient.
- Deactivate when the task shifts from discovery to planning, diagnosis, or editing.
