---
name: conflict-resolution
version: 0.1.0
description: Compare and arbitrate conflicting findings from parallel investigations or competing hypotheses. Typically loaded by the multi-agent-protocol synthesis step when subagent results disagree, or when the agent holds two plausible explanations with different supporting evidence.
tags: [coding, agents, orchestration, efficiency]
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

# Composition

Combine with:

- `multi-agent-protocol` to normalize incoming outputs
- `bugfix-workflow` when conflicting causes are being weighed
- `targeted-validation` to design an adjudication check
- `context-budget-awareness` to compress multi-branch reasoning into a usable merged state

# Example

Task: "Merge three subagent reports on a cache inconsistency bug."

Possible merge result:

- Consensus: stale reads involve the cache invalidation path.
- Disagreements: Report A claims missing invalidation (code-path evidence in `cache.py:112–118`) vs Report B claims clock skew in expiry logic (timing correlation from logs).
- Evidence assessment: missing invalidation has direct code-path evidence (priority 1); clock skew has log correlation only (priority 3).
- Recommendation: inspect the invalidation branch first.
- Adjudication needed: run one targeted expiry-path check before ruling out clock skew.
