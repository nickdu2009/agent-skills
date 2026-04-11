---
name: conflict-resolution
description: Compare and arbitrate conflicting findings from parallel investigations or competing hypotheses. Typically loaded by multi-agent-protocol synthesis step when subagent results disagree, or when the agent holds two plausible explanations with different supporting evidence. Use for merge conflicts, disagreements between investigation paths, or overlapping findings from parallel work. Triggers on "conflicting", "disagree", "contradictory", or synthesis with 2+ divergent conclusions.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Help the primary agent compare and arbitrate conflicting findings without collapsing uncertainty too early. The skill keeps synthesis evidence-based and prevents the loudest conclusion from becoming the final answer by tone alone.

# When to Use

- When multiple subagents report overlapping findings.
- When different hypotheses are supported by different evidence.
- When findings appear contradictory or partially contradictory.
- When the next action depends on choosing between competing explanations.

# When Not to Use

- When outputs are already consistent and non-overlapping.
- When only one source of evidence exists.
- When the task is simple enough that serial analysis is clearer than merge logic.

# Core Rules

- Deduplicate overlapping findings.
- Identify consensus first.
- Clearly label disagreements.
- Weigh evidence quality, not confidence tone.
- Do not force premature resolution.
- Preserve uncertainty when evidence is weak.
- If needed, recommend a targeted adjudication pass.

# Execution Pattern

1. Normalize each finding into the standard format (Claim / Evidence / Source / Confidence).
   - Rewrite each claim as: subject + predicate + scope.
   - Drop findings that have no evidence attached.
   - When receiving `multi-agent-protocol` subagent output, map fields: `Findings` → `Claim`, infer `Source` from the subagent identity, carry `Evidence` and `Confidence` directly. For Tier 2 output, `Uncertainty` becomes a confidence qualifier.
   - Example normalization:
     Raw: "Findings: stale cache on retry. Evidence: `cache.py:112`. Confidence: high"
     Normalized: "Claim: cache invalidation is missing on the retry path. Evidence: `cache.py:112–118`. Source: subagent-1. Confidence: high"
2. Group claims by topic or hypothesis.
3. Mark consensus, partial consensus, and disagreement.
4. Compare evidence quality using these dimensions in priority order:
   1. Direct code-path evidence (strongest)
   2. Reproducible behavioral evidence
   3. Log or timing correlation
   4. Structural similarity or analogy (weakest)
   When two findings conflict and their evidence types differ, prefer the finding with higher-priority evidence.
5. Resolve only when one interpretation is clearly better supported.
6. If resolution is weak, recommend the smallest targeted adjudication step.
7. Produce a final merged view with uncertainty made explicit.

# Input Contract

Each finding must use this format:

- Claim: <one-sentence assertion>
- Evidence: <file paths, line ranges, observed behavior, or log entries>
- Source: <which agent, pass, or analysis produced this>
- Confidence: <high | medium | low>

Also provide:

- the decision that depends on the merge
- any priority on false positives versus false negatives

Optional but helpful:

- the original symptom or objective
- known trust differences between evidence sources

# Output Contract

Return using this template:

- Consensus: <list of agreed claims>
- Disagreements: <claim A vs claim B, with evidence for each>
- Evidence assessment: <which evidence is stronger and why>
- Recommendation: <action to take>
- Adjudication needed: <targeted check if resolution is incomplete, or "none">

# Guardrails

- Do not equate stronger wording with stronger evidence.
- Do not erase minority findings that still have meaningful support.
- Do not present an unresolved disagreement as settled.
- If two findings can both be true at different layers, represent that possibility.
- Keep adjudication narrow and evidence-seeking.

# Common Anti-Patterns

- **Loudest voice wins.** One subagent reports with "high confidence" while another says "medium confidence." The agent picks the high-confidence claim without comparing evidence quality — the medium-confidence claim had direct code-path evidence while the high-confidence claim relied on log correlation only.
- **Collapsing disagreement into false consensus.** Two subagents contradict each other, and the agent silently drops the minority finding instead of presenting both with their evidence and labeling the disagreement.

See skill-anti-pattern-template.md for format guidelines.

# Composition

Part of the `parallel` chain (see the project governance file § Skill Chain Triggers).

Additional compositions:

- `bugfix-workflow` when conflicting causes are being weighed
- `context-budget-awareness` to compress multi-branch reasoning into a usable merged state

# Example

Task: "Merge three subagent reports on a cache inconsistency bug."

Possible merge result:

- Consensus: stale reads involve the cache invalidation path.
- Disagreements: Report A claims missing invalidation (code-path evidence in `cache.py:112–118`) vs Report B claims clock skew in expiry logic (timing correlation from logs).
- Evidence assessment: missing invalidation has direct code-path evidence (priority 1); clock skew has log correlation only (priority 3).
- Recommendation: inspect the invalidation branch first.
- Adjudication needed: run one targeted expiry-path check before ruling out clock skew.

## Contract

### Preconditions

- There are at least two non-identical findings or hypotheses to compare.
- Each claim carries evidence, source, and confidence metadata, or can be normalized into that shape.
- A downstream decision depends on resolving or preserving the disagreement.

### Postconditions

- `status: completed` includes `claims`, `evidence`, `resolution`, and `residual_uncertainty`.
- Consensus and disagreement are separated explicitly.
- The final recommendation is tied to evidence quality rather than tone.

### Invariants

- Unsupported claims are dropped rather than treated as valid evidence.
- Minority findings with real support are preserved until disproven.
- Unresolved disagreement is reported as unresolved.

### Downstream Signals

- `claims` captures the normalized positions under review.
- `evidence` records the basis for comparison.
- `resolution` states the current best-supported conclusion or adjudication direction.
- `residual_uncertainty` tells downstream work what remains unproven.

## Failure Handling

### Common Failure Causes

- Claims arrive without enough evidence to compare meaningfully.
- Two interpretations can both be true at different layers and are incorrectly treated as mutually exclusive.
- The evidence gap is too large for a confident arbitration.

### Retry Policy

- Allow one normalization/adjudication pass when the first comparison lacks sufficient structure.
- If evidence still cannot support a decision, stop and recommend the smallest targeted adjudication step.

### Fallback

- Hand unresolved disagreements back to `multi-agent-protocol` synthesis with explicit residual uncertainty.
- Use `targeted-validation` to design the adjudication check.
- Escalate to the user when the decision depends on non-technical trade-offs.

### Low Confidence Handling

- Prefer `resolution: unresolved` with a targeted next step over a weak forced verdict.
- State exactly which claim remains uncertain and why.

## Deactivation Trigger

- Deactivate once a merged resolution or explicit unresolved state has been delivered.
- Deactivate when the disagreement is absorbed by a downstream targeted check.
- Deactivate after the primary agent or user consumes the arbitration result.
