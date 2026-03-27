---
name: safe-refactor
version: 0.1.0
description: Guide small, controlled refactors that improve structure while keeping behavior and interfaces stable unless change is explicitly requested.
tags: [coding, agents, orchestration, efficiency]
---

# Purpose

Make structural improvements with bounded risk. The skill is for small refactors that reduce duplication or improve local clarity without quietly changing behavior or widening the task.

# When to Use

- When the task is structural cleanup with stable behavior.
- When a small local refactor is needed to support a separate change safely.
- When duplicated or tangled logic can be simplified without interface changes.

# When Not to Use

- When the user asked for a bugfix only and no refactor is needed.
- When the refactor would likely change public behavior or external contracts.
- When the required change is large enough to need a dedicated redesign.

# Core Rules

- Keep interface and behavior stable unless change is explicitly requested.
- Refactor in small reversible steps.
- Separate structural cleanup from behavior changes.
- Define invariants before editing.
- Validate only the affected area unless wider validation is justified.
- Prefer extraction, isolation, and simplification over sweeping reorganization.

# Execution Pattern

1. Define the refactor goal.
2. List invariants that must remain true.
3. Choose the smallest structural step.
4. Edit one step at a time.
5. Run narrow validation after each meaningful step.
6. Stop once the structural goal is met; do not convert the task into a redesign.

# Input Contract

Provide:

- the refactor goal
- stable interfaces or behaviors that must not change
- the affected files or modules
- allowed scope for structural movement

Optional but helpful:

- duplicated code locations
- available local tests

# Output Contract

Return:

- stated invariants
- the chosen small-step sequence
- touched interfaces and why they remain stable
- the validation boundary
- residual risk or deferred cleanup

# Guardrails

- Do not bundle behavior changes into a structural cleanup.
- Do not rename externally meaningful symbols unless requested.
- Do not reorganize files just because a smaller extraction would work.
- If a refactor step exposes hidden behavior changes, stop and split the work.
- Keep each step easy to review and easy to revert.

# Composition

Combine with:

- `minimal-change-strategy` to keep the structural patch bounded
- `plan-before-action` to declare invariants and steps before editing
- `targeted-validation` to validate each step cheaply
- `read-and-locate` when the structural boundaries are not obvious yet

# Example

Task: "Extract duplicate request-normalization logic used by three handlers."

Possible invariants:

- handler signatures stay unchanged
- normalized output shape stays unchanged
- error messages stay unchanged

Apply the refactor by extracting one shared helper, switching one handler at a time if needed, and validating the affected handlers rather than running every API test in the repository.
