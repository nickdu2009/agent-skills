---
name: context-budget-awareness
description: Compress working state when investigation is stuck. Use when (1) 8+ files read without convergence (not 7), (2) same file read 3+ times without new leads, (3) 4+ hypotheses listed with "could be X, Y, Z, or W" pattern without evidence ranking, or (4) last 3+ actions didn't advance the goal. Pattern "could be...or...or...or" with 4+ options triggers this.
metadata:
  version: "0.2.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Teach the agent to control context growth through an observable, structured accounting mechanism — the Context Ledger. Instead of relying on implicit self-discipline to track file counts and hypothesis budgets, the agent must externalize its working state at defined checkpoints so that both the agent and the user can verify whether budget rules are being followed.

# When to Use

- In long debugging or refactoring sessions.
- When the working set exceeds 8 files without a recent scope-narrowing step.
- When the same file has been read more than twice without a new question driving the re-read.
- When more than 3 hypotheses are active without evidence to rank them.
- When the agent's last 3 actions did not advance the stated objective.
- When a fresh focused pass may be cheaper than carrying the current context forward.

These thresholds (8 files, 2 re-reads, 3 hypotheses, 3 stalled actions) are starting defaults. Adjust downward for small focused tasks or upward for large multi-module investigations where broader context is expected.

# When Not to Use

- In a short task with a stable, compact working set.
- When a small amount of extra context is essential to avoid repeated discovery.
- When the user explicitly wants a broad historical recap.

# Core Rules

- Avoid long, bloated sessions when a fresh focused session is better.
- Avoid repeatedly re-reading large files without need.
- Avoid injecting excessive policy, logs, or irrelevant history.
- Keep active context aligned to the current objective.
- Distinguish between live context, deferred context, and discarded context.
- Externalize working state through the Context Ledger at every checkpoint — never rely on implicit internal tracking.

# Context Ledger

The Context Ledger is a structured status block that the agent must output at defined checkpoints. It replaces implicit self-monitoring with observable, auditable state.

## Ledger Format

```
[context-ledger]
objective: <one-sentence current objective>
files_touched: [file_a.py, file_b.py, file_c.py]  (N/8)
re-reads: file_b.py ×2 (reason: verifying fix)
hypotheses:
  - ✓ confirmed hypothesis (evidence: ...)
  - ✗ ruled-out hypothesis (evidence: ...)
  - ? pending hypothesis (strength: high|medium|low)
staleness: N/3
action: continue | compress | restart
[/context-ledger]
```

Field definitions:

- **objective**: the current goal in one sentence. If it has drifted from the original task, note the drift.
- **files_touched**: every distinct file read or edited in this session, with count against the threshold `(N/8)`.
- **re-reads**: any file read more than once, with the count and the new question that justified the re-read. A re-read without a stated new question is a violation.
- **hypotheses**: each hypothesis tagged with one of three states:
  - `✓` confirmed — has supporting evidence (cited).
  - `✗` ruled out — has disconfirming evidence (cited).
  - `?` pending — not yet tested, annotated with estimated strength (high/medium/low).
- **staleness**: count of consecutive recent actions that did not advance the stated objective `(N/3)`.
- **action**: the agent's decision based on ledger state — one of `continue`, `compress`, or `restart`.

## Checkpoints (When to Output the Ledger)

Output the Context Ledger at these milestones — not after every tool call:

| Checkpoint | Trigger |
|------------|---------|
| New file enters working set | a file not previously in `files_touched` is read or edited |
| Hypothesis state change | a hypothesis is added, confirmed (`✓`), or ruled out (`✗`) |
| Edit completed | a file was successfully modified |
| Stall detected | the agent self-assesses that its last 3 actions did not advance the objective |
| Subagent results received | parallel investigation results need to be merged into the working state |

## Threshold-Triggered Actions

When a threshold is reached, the ledger `action` field must reflect the required response. The agent must not choose `continue` when a threshold is breached.

| Condition | Required action |
|-----------|----------------|
| `files_touched` count ≥ 8 | `action: compress` — classify working set into Live / Deferred / Discarded and drop Discarded files from active context |
| Same file re-read ≥ 3 times | Must state the new question in `re-reads`. If no new question exists, stop re-reading and work from the existing summary |
| Pending hypotheses `?` ≥ 4 | Must rank by evidence strength and discard the weakest before adding any new hypothesis |
| `staleness` ≥ 3 | `action: compress` or `action: restart` — `continue` is not permitted |

# Execution Pattern

1. At session start, state the objective and initialize an empty ledger.
2. Read only the slices of information needed for the next step.
3. At each checkpoint (see table above), output the Context Ledger.
4. If the ledger shows a threshold breach, execute the required action before proceeding.
5. When `action: compress`, produce a compressed state block (see Output Contract).
6. When `action: restart`, produce a compressed state block and explicitly discard all context outside that block. Continue from the compressed state only.
7. Rehydrate only the evidence needed for the next decision — do not reload discarded context.

# Input Contract

Provide:

- the current objective
- the active file or module set
- the current evidence
- any history that is truly required

Optional but helpful:

- the last known good summary
- known dead ends to avoid

# Output Contract

Return at every checkpoint:

- the Context Ledger (structured status block, see format above)

Return when `action` is `compress` or `restart`:

- the compressed state using this template:
  ```
  [context-compressed]
  objective: <...>
  confirmed_scope: [file_a.py:fn_x, file_b.py:class_Y]
  ruled_out: [file_c.py — reason, file_d.py — reason]
  live: [files directly needed for the next step]
  deferred: [files that may matter later but do not block the current step]
  discarded: [files investigated and found irrelevant]
  next_step: <specific next action>
  [/context-compressed]
  ```
- the active working set, classified as:
  - **Live**: directly needed for the next step.
  - **Deferred**: may matter in a later phase but does not block the current step.
  - **Discarded**: investigated and found irrelevant, or superseded by newer evidence.
- the next focused step

# Guardrails

- The Context Ledger must be output at every checkpoint. Skipping a checkpoint is a skill violation.
- A re-read without a stated new question in the `re-reads` field is a violation.
- Choosing `action: continue` when any threshold is breached is a violation.
- Do not keep huge logs or long file excerpts in active memory when a short summary is enough.
- Drop any hypothesis that has no supporting evidence after the most recent investigation pass.
- If starting fresh would improve clarity, say so explicitly via `action: restart`.
- The compressed state must include: the current objective, the confirmed scope, what has been ruled out, and the next intended step.

# Common Anti-Patterns

- **Carrying the entire session history.** The agent re-reads rejected hypotheses, old terminal output, and abandoned file paths into every subsequent step instead of compressing state after each milestone.
- **Re-reading the same 500-line file for the fourth time.** The agent keeps loading the same large file without a new question driving the re-read, consuming context budget on information that should have been summarized after the first pass.
- **Silent threshold breach.** The agent internally "knows" it has touched 10 files but never externalizes this count, so neither the agent's own reasoning nor the user can catch the violation. The Context Ledger prevents this by requiring explicit accounting.
- **Phantom progress.** The agent keeps reading files and running commands but the objective has not advanced. Without the `staleness` counter in the ledger, this can go unnoticed for many steps.

See skill-anti-pattern-template.md for format guidelines.

# Composition

Cross-chain fallback skill. Activates when context budget thresholds are breached during any execution chain (see CLAUDE.md § Skill Escalation).

Role: Compress and refocus working state when investigation is stuck or spinning. Produces compressed state that downstream skills can consume.

Typical activations:

- During `bugfix-workflow` when diagnosis spreads across too many hypotheses
- During `read-and-locate` when discovery exceeds 8 files without convergence
- During `multi-agent-protocol` synthesis when parallel findings need compact merge
- After compression, typically hands back to `plan-before-action` to resume with focused state

# Example

Task: "Debug an intermittent worker failure after a long session."

Context Ledger at a mid-session checkpoint:

```
[context-ledger]
objective: find root cause of worker failure on retry path
files_touched: [retry_scheduler.py, payload_serializer.py, retry_test.py, queue_client.py, credentials.py]  (5/8)
re-reads: retry_scheduler.py ×2 (reason: checking retry count vs. max_retries after finding serializer issue)
hypotheses:
  - ✗ queue connection timeout (evidence: connection logs show successful reconnect)
  - ✗ credential expiry (evidence: token refresh confirmed in auth middleware)
  - ? payload serializer drops fields on retry (strength: high)
  - ? retry count off-by-one (strength: medium)
staleness: 0/3
action: continue
[/context-ledger]
```

Compressed state when threshold is hit:

```
[context-compressed]
objective: find root cause of worker failure on retry path
confirmed_scope: [retry_scheduler.py:enqueue_retry, payload_serializer.py:serialize]
ruled_out: [queue_client.py — connection stable, credentials.py — token refresh works]
live: [retry_scheduler.py, payload_serializer.py]
deferred: [retry_test.py — update after fix is found]
discarded: [queue_client.py, credentials.py]
next_step: compare serializer output between initial enqueue and retry enqueue for field differences
[/context-compressed]
```

Do not carry the full terminal history, every rejected hypothesis, and every unrelated worker module into the next pass.

## Contract

### Preconditions

- The session is long, noisy, or clearly at risk of context sprawl.
- The agent can name the current objective, working set, and active hypotheses.
- At least one compression or restart decision can be justified from observable session state.

### Postconditions

- `status: completed` includes `current_state`, `dropped_hypotheses`, and `open_questions`.
- A ledger or compressed-state output makes the active context observable.
- The next step is narrower than the pre-compression state.

### Invariants

- Working-state accounting stays explicit rather than implicit.
- Threshold breaches do not continue with `action: continue`.
- Stale hypotheses are either ranked, deferred, or dropped.

### Downstream Signals

- `current_state` gives downstream skills the compressed summary they should continue from.
- `dropped_hypotheses` prevents old dead ends from silently re-entering scope.
- `open_questions` defines the next focused investigation target.

## Failure Handling

### Common Failure Causes

- The agent cannot summarize the live scope because the session never externalized its state.
- Too many hypotheses remain active with no evidence to rank them.
- The user wants a broad historical recap rather than a compact working summary.

### Retry Policy

- Allow one compression pass to rebuild the ledger from current evidence.
- If the state still cannot be compressed usefully, recommend a restart from the compressed summary instead of continuing the bloated session.

### Fallback

- Hand off to `scoped-tasking` when the compressed state shows the objective itself is too broad.
- Resume `plan-before-action` once the working set is compact again.
- Ask the user whether a broad recap is wanted when concise compression conflicts with their goal.

### Low Confidence Handling

- Mark weak hypotheses as open questions rather than carrying them as likely causes.
- Prefer restart over continued accumulation when the compressed state is still noisy.

## Output Example

```yaml
[skill-output: context-budget-awareness]
status: completed
confidence: medium
outputs:
  current_state:
    objective: "find root cause of worker failure on retry path"
    live: ["retry_scheduler.py", "payload_serializer.py"]
  dropped_hypotheses: ["queue connection timeout", "credential expiry"]
  open_questions: ["does serializer output differ between initial enqueue and retry enqueue?"]
signals:
  action: "compress"
recommendations:
  next_step: "compare serializer output across the two enqueue paths"
[/skill-output]
```

## Deactivation Trigger

- Deactivate once the working set is back under control and a downstream skill has consumed the compressed state.
- Deactivate when the user explicitly chooses a broad recap instead of focused continuation.
- Deactivate after a restart handoff has been produced and the old session state is no longer active.
