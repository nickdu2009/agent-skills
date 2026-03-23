---
name: conflict-resolution
description: Merge overlapping or conflicting findings by comparing evidence quality, preserving uncertainty, and recommending targeted adjudication when needed.
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

1. Normalize findings into comparable claims.
2. Group claims by topic or hypothesis.
3. Mark consensus, partial consensus, and disagreement.
4. Compare evidence quality: directness, reproducibility, code proximity, and consistency with observed symptoms.
5. Resolve only when one interpretation is clearly better supported.
6. If resolution is weak, recommend the smallest targeted adjudication step.
7. Produce a final merged view with uncertainty made explicit.

# Input Contract

Provide:

- the collected findings
- the evidence attached to each finding
- the decision that depends on the merge
- any priority on false positives versus false negatives

Optional but helpful:

- the original symptom or objective
- known trust differences between evidence sources

# Output Contract

Return:

- deduplicated findings
- consensus points
- disagreements
- evidence-quality assessment
- the merged recommendation
- any targeted adjudication step if resolution is incomplete

# Guardrails

- Do not equate stronger wording with stronger evidence.
- Do not erase minority findings that still have meaningful support.
- Do not present an unresolved disagreement as settled.
- If two findings can both be true at different layers, represent that possibility.
- Keep adjudication narrow and evidence-seeking.

# Composition

Combine with:

- `subagent-orchestration` to normalize incoming outputs
- `bugfix-workflow` when conflicting causes are being weighed
- `targeted-validation` to design an adjudication check
- `context-budget-awareness` to compress multi-branch reasoning into a usable merged state

# Example

Task: "Merge three subagent reports on a cache inconsistency bug."

Possible merge result:

- Consensus: stale reads involve the cache invalidation path.
- Disagreement: one report blames missing invalidation, another blames clock skew in expiry logic.
- Evidence assessment: missing invalidation has direct code-path evidence; clock skew has circumstantial timing evidence only.
- Recommendation: inspect the invalidation branch first and run one targeted expiry-path check before ruling out the secondary hypothesis.
