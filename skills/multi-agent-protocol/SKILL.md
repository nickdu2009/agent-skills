---
name: multi-agent-protocol
description: Launch and coordinate parallel subagents. Use when (1) user explicitly says "in parallel", (2) task describes 3+ independent investigation areas owned by different teams/modules, or (3) AGENTS.md rules indicate Tier 2 parallelism. Implicit parallel opportunity example "understand X system, Y service, and Z pipeline" equals 3 independent areas.
metadata:
  version: "0.2.0"
  tags: "coding, agents, orchestration"
---

# multi-agent-protocol

Use this skill to decide whether parallel agent work is justified and how to merge results.

## Use When

- There are 3 or more independent investigation areas.
- Different modules, artifacts, or hypotheses can be explored without shared writes.
- Parallel read-only exploration can reduce latency without creating merge confusion.
- Write-capable delegation is explicitly useful and scopes can be isolated.

## Do Not Use When

- A single direct search or file read is enough.
- Work areas overlap heavily.
- The parent agent cannot clearly synthesize the outputs.

## Tiers

- Tier 1, read-only: launch without declaration when each subagent has a clear question and must return evidence.
- Tier 2, write-capable: before launch, emit `[delegate: <count 2-4> | split:<dimension> | risk:<low|medium|high>]`.

## Subagent Contract

Each subagent prompt must include:

- objective
- exact scope
- allowed operations
- expected evidence format
- what not to change or inspect

## Parent Duties

- Keep at most 4 subagents active unless a phase plan is warranted.
- Integrate findings; do not paste reports together.
- Preserve uncertainty when evidence is incomplete.
- Own the final decision and validation plan.

## Conflict Step

When subagent conclusions disagree:

1. Normalize each claim with evidence, source, and confidence.
2. Group claims by topic or hypothesis.
3. Compare evidence quality: direct code path, reproducible behavior, logs, then analogy.
4. Adopt only conclusions clearly supported by stronger evidence.
5. If unresolved, choose the smallest follow-up check and mark the remaining uncertainty.

## Output

`[output: multi-agent-protocol | completed <confidence> | lanes:"..." synthesis:"..." uncertainty:"..." | next:<action>]`
