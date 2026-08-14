# Architecture principle calibration

Use only to validate a relevant decision after designing from requirements.

- **Structure:** high cohesion, low coupling, clear responsibility, encapsulated internals.
- **Interfaces:** narrow role-specific contracts, stable dependency direction, predictable semantics.
- **Decisions:** right-size complexity, prefer reversibility, expose ownership/team mismatch, avoid coupling disguised as reuse.
- **Runtime quality:** evaluate failure modes, defense in depth, observability injection points, evolvability, early validation.

Violation signals include unrelated responsibilities in one component, callers using internal data, core domains importing infrastructure details, layers/components added only for hypothetical growth, or external dependencies with no failure-mode analysis.

Not every principle applies. Record any conflict as: prioritized principle, relaxed principle, requirement/constraint that justified it, and consequence. Evaluating timeout/retry/fallback/degradation does not authorize a concrete strategy; keep it blocking until a valid source confirms it.
