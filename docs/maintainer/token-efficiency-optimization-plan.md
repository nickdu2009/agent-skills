# Token Efficiency Optimization Plan

**Version**: 2.0  
**Date**: 2026-04-11  
**Status**: Draft  
**Scope**: Repository-only

## Executive Summary

This plan narrows token-efficiency work to what can be implemented inside the
`agent-skills` repository itself. It treats the repository as a prompt-surface
producer for `Cursor`, `Claude Code`, and `Codex`, not as the runtime that
controls model loading, caching, request routing, or telemetry.

The practical goal is to reduce prompt surface area and duplicated text in:

- `SKILL.md` files
- `AGENTS.md` / `CLAUDE.md` governance templates
- generated governance output
- evaluation prompts and static prompt assets

This revision intentionally removes or demotes ideas that require external
platform/runtime control, such as prompt caching, runtime lazy loading,
checkpoint stores, A/B rollout, request-level token telemetry, and response-time
monitoring.

## Repo-Scoped Assumptions

This plan keeps only assumptions that are valid inside this repository:

1. The repository's main lever is text.
   - We can directly change skill documents, governance templates, generated
     governance content, installation scripts, and evaluation scripts.
   - We cannot directly change how `Cursor`, `Claude Code`, or `Codex` schedule
     prompts internally.

2. Governance output is platform-shaped but repo-controlled.
   - `manage-governance.py` already selects `AGENTS.md` for `Cursor`/`Codex`
     and `CLAUDE.md` for `Claude Code`.
   - Template size and structure therefore matter.

3. Some tasks can stay at the governance layer.
   - The repository already models cases where no full skill should load and
     `AGENTS.md` rules are sufficient.
   - This makes governance-boundary optimization realistic.

4. Proxy measurements are acceptable.
   - We can measure text length, approximate token count, generated prompt size,
     and evaluation prompt size.
   - We cannot assume request logs, real token billing data, cache-hit data, or
     runtime latency metrics exist.

5. Backward compatibility matters more than theoretical maximum savings.
   - Prompt compression must not break installer output, trigger evaluation, or
     the readability of governance assets.

6. The shared skill source tree should preserve the portable core.
   - Shared `SKILL.md` files should continue to rely on the cross-platform
     minimum contract: `name`, `description`, matching directory name, and a
     concise body.
   - Additional summary or analysis metadata should be generated into external
     artifacts by default, not added directly to the shared `SKILL.md`
     frontmatter unless compatibility has been reviewed explicitly.

7. Officially documented authoring guardrails are fair repo-level targets.
   - Shared `description` fields should stay specific, use third-person phrasing,
     and include both what the skill does and when it should trigger.
   - Shared `SKILL.md` bodies should generally stay under 500 lines, with larger
     material split into sidecar files where practical.
   - Reference structures should stay shallow enough for progressive disclosure
     to remain reliable, with one-level-deep links from `SKILL.md` as the
     preferred pattern.

## Explicit Non-Goals

The following items are out of scope for this repository-only plan:

- prompt caching integration
- runtime lazy loading of skill stubs
- model-side checkpointing or delta-state stores
- adaptive protocol depth enforced by the platform
- request-level token telemetry
- staging environments and runtime A/B rollout
- response-time dashboards
- platform-internal batch activation primitives

These can remain as future architecture notes, but they are not implementation
work for this repository.

## Current Cost Drivers Inside the Repo

The largest repo-controlled token costs are:

1. Verbose governance templates
   - `templates/governance/AGENTS-template.md`
   - `templates/governance/CLAUDE-template.md`

2. Repetition across skill docs
   - repeated protocol framing
   - repeated composition language
   - large examples and explanatory prose
   - oversized `SKILL.md` bodies or nested references that weaken progressive
    disclosure

3. Generated governance output
   - full injected `AGENTS.md` / `CLAUDE.md` documents may carry more repeated
     explanation than needed for day-to-day use

4. Evaluation prompt size
   - trigger test prompts currently build a flat block of available skill
     descriptions

## Optimization Strategy

## Tier 1: High-Confidence Repo Wins

### 1. Governance Surface Compression

**Goal**: Reduce repeated prose in governance templates while preserving meaning.

#### Approach

- Tighten wording in:
  - `templates/governance/AGENTS-template.md`
  - `templates/governance/CLAUDE-template.md`
- Prefer short rule bullets over explanatory prose when the meaning is already
  well covered by nearby structure.
- Move optional explanatory material out of the generated governance surface and
  into maintainer docs when possible.
- Keep generated governance docs optimized for execution, not for onboarding.

#### Constraints

- Do not remove required governance sections.
- Do not weaken the trigger/lifecycle/validation contract.
- Do not break platform-specific wording differences.

#### Expected Benefit

- Smaller generated `AGENTS.md` / `CLAUDE.md`
- Lower repeated prompt surface for users who install the full governance suite

### 2. Governance Protocol V2 (Text-Only Compression)

**Goal**: Introduce a more compact protocol representation at the text/template
level without assuming runtime protocol engines.

#### Approach

- Define a repository-supported compact style for protocol blocks.
- Keep current verbose form as `v1`.
- Add a `v2` compact representation for examples, templates, or future
  generated variants.
- Treat this as a documentation and rendering choice, not a runtime feature.

#### Example Direction

Current verbose style:

```yaml
[task-input-validation]
task: "<user request verbatim>"
checks:
  clarity:
    status: PASS
    reason: "<why>"
result: PASS
action: proceed
[/task-input-validation]
```

Compact v2 style:

```yaml
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | action:proceed]
```

#### Constraints

- Keep `v1` as a supported reference form.
- Use `v2` only where readability and maintainability remain acceptable.
- Do not change evaluator expectations without synchronized test updates.

#### Expected Benefit

- Lower prompt footprint for governance examples and generated guidance
- More stable prompt structures for repeated execution

### 3. AGENTS/CLAUDE Boundary Tightening

**Goal**: Make "no full skill needed" behavior more explicit and more testable.

#### Approach

- Expand the boundary rules for tiny tasks that should remain at the governance
  layer.
- Add or refine trigger cases for:
  - direct answers
  - simple commands
  - single-file low-risk edits
  - routine validation requests
- Keep fast-path as a repository rule and evaluation concept, not a platform
  bypass engine.

#### Existing Foundation

- `maintainer/data/trigger_test_data.py` already includes
  `agents-md-boundary` scenarios.

#### Expected Benefit

- Fewer unnecessary skill activations in prompt guidance
- Clearer separation between governance-only behavior and skill escalation

## Tier 2: Medium-Confidence Repo Improvements

### 4. Skill Metadata / Stub Layer

**Goal**: Create a shorter, repo-controlled summary layer for each skill without
assuming runtime lazy loading.

#### Approach

- Generate a compact skill index or sidecar summary artifact for evaluation and
  analysis tooling.
- Derive compact fields from the existing shared source tree where possible, for
  example:
  - `name`
  - `description`
  - directory path
  - derived family or category labels computed by tooling
- Only add new fields to shared `SKILL.md` frontmatter if they are validated as
  portable across the supported platform baseline.
- Use the compact index in maintainer scripts where full `SKILL.md` bodies are
  unnecessary.

#### Important Boundary

This is **not** runtime lazy loading. It is a repository-maintained summary
artifact that lets evaluation and analysis use shorter inputs.

It is also **not** a default expansion of the shared `SKILL.md` contract. The
first implementation choice should be a generated external index rather than new
frontmatter fields in the shared skill source tree.

#### Candidate Uses

- trigger test prompt construction
- maintainer reports
- release/readiness summaries

#### Expected Benefit

- Smaller eval prompts
- Reduced duplicated description text in analysis scripts

### 5. Evaluation Prompt Slimming

**Goal**: Reduce prompt size in repository evaluation tools.

#### Approach

- Update evaluation scripts to prefer compact skill summaries over full
  descriptive lists when the full text is not necessary.
- Keep a verbose mode for debugging and rubric inspection.
- Add a measurable "prompt size before/after" comparison for evaluation scripts.

#### Candidate Targets

- `maintainer/scripts/evaluation/run_trigger_tests.py`
- related report-generation scripts

#### Expected Benefit

- Lower prompt size in maintainer-driven evaluations
- Better evidence for whether text-only compression is actually helping

### 6. Common Chain Aliases

**Goal**: Reduce repeated chain narration in examples and governance docs.

#### Approach

- Define a small set of repository-level chain aliases, for example:
  - `bugfix-standard`
  - `refactor-safe`
  - `multi-file-planned`
- Use aliases in examples and maintainer docs where full chain spelling adds
  little value.
- Keep the detailed chain definitions in one canonical reference section.

#### Boundary

This is a documentation alias mechanism, not a runtime batch activation system.

#### Expected Benefit

- Less repeated chain prose across docs and examples
- Easier maintenance when a canonical chain changes

## Tier 3: Optional Structural Cleanup

### 7. Selective Skill Deduplication

**Goal**: Reduce duplicated explanatory text across skills without forcing early
skill mergers.

#### Approach

- Start with shared wording cleanup before any skill consolidation.
- Extract repeated explanatory prose patterns into:
  - maintainer docs
  - shared examples
  - concise canonical wording reused manually
- Only consider true skill mergers after evidence shows text duplication is the
  dominant problem and semantic boundaries remain intact.

#### Why This Is Not Full Consolidation

Full skill consolidation would ripple across:

- governance rules
- tests and trigger datasets
- examples
- baselines
- installer assumptions
- maintainer documentation

That makes it a separate design effort, not a token-efficiency quick win.

#### Expected Benefit

- Moderate reduction in duplicated prose
- Lower migration risk than renaming or merging skills

## Implementation Roadmap

## Phase 1: Measurement and Safe Compression

### Goals

- establish repo-only baseline metrics
- compress governance surfaces safely
- tighten boundary rules

### Tasks

- [ ] Add a proxy token/size measurement script or report mode
- [ ] Measure:
  - template length
  - generated governance length
  - evaluation prompt length
- [ ] Add a repo-level check/report for:
  - `SKILL.md` body length against the 500-line target
  - description quality markers (`what` + `when`, third-person phrasing)
- [ ] Draft compact protocol `v2`
- [ ] Tighten governance wording in templates
- [ ] Add boundary-focused trigger cases where gaps exist

### Exit Criteria

- baseline report exists
- compact governance wording passes existing smoke and trigger checks
- no regression in generated governance structure

## Phase 2: Summary Layers and Evaluation Slimming

### Goals

- reduce evaluation prompt size
- introduce shorter summary artifacts for skill analysis

### Tasks

- [ ] Define compact skill metadata/stub format as a generated external artifact
- [ ] Generate a compact skill index from the shared `SKILL.md` source plus
      derived summary fields
- [ ] Update evaluation scripts to support compact vs verbose prompt modes
- [ ] Measure prompt-size delta on trigger evaluation flows

### Exit Criteria

- evaluation scripts can run in compact mode
- prompt-size reduction is measurable
- trigger expectations remain stable

## Phase 3: Documentation Normalization

### Goals

- reduce repeated chain narration
- clean shared wording across examples and skill docs

### Tasks

- [ ] Add common chain aliases/reference table
- [ ] Normalize repeated phrasing across examples
- [ ] Identify high-duplication prose across skill docs
- [ ] Apply selective deduplication without changing skill identities

### Exit Criteria

- canonical chain reference exists
- examples and maintainer docs use shared naming consistently
- duplication reduction is visible in a before/after size report

## Success Metrics

Only include metrics the repository can actually produce.

### Primary Metrics

| Metric | Baseline Source | Target |
|--------|-----------------|--------|
| Governance template size | template file length / proxy tokens | 15-25% reduction |
| Generated governance size | temp-project generation via installer | 15-25% reduction |
| Evaluation prompt size | trigger test prompt builder | 20-35% reduction |
| SKILL body budget compliance | shared `SKILL.md` line counts | no unjustified regressions over 500 lines |
| Boundary-case precision | trigger test results | no regression |
| Install/smoke stability | existing smoke scripts | 100% pass |

### Secondary Metrics

| Metric | Meaning |
|--------|---------|
| Skill summary index size | how small a compact analysis surface can be |
| Chain alias adoption | how much repeated chain prose was removed |
| Duplication reduction | repeated phrase or block reduction across skill docs |

## Validation Plan

Use only repository-controlled validation.

### Required Checks

1. Trigger evaluation
   - `python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report`
   - extend with targeted cases as needed

2. Governance installation smoke
   - `python3 maintainer/scripts/install/run_manage_governance_smoke.py`

3. Temporary-project generation checks
   - use `manage-governance.py --project <temp-dir>` to verify generated
     `AGENTS.md` / `CLAUDE.md`

4. Portable-core guardrail review
   - confirm shared `SKILL.md` files still rely on the cross-platform portable
     minimum contract unless an explicit compatibility exception was approved
   - prefer generated sidecar/index outputs over new shared frontmatter fields
   - review `description` quality for specific trigger terms, third-person
     phrasing, and both what/when coverage
   - review `SKILL.md` body length and shallow reference layout as progressive
     disclosure guardrails

5. Size comparison
   - compare before/after file length and proxy token estimates for:
     - governance templates
     - generated governance docs
     - evaluation prompts

### Nice-to-Have Checks

- maintain a markdown baseline report for repo-controlled prompt surfaces
- compare compact vs verbose evaluation prompt sizes side by side

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Compression harms clarity | Medium | Keep `v1` reference form; review compact wording manually |
| Governance text loses required nuance | High | Validate against trigger tests and installer smoke tests |
| Metadata/stub layer drifts from skill source | Medium | Generate summaries from source instead of hand-maintaining them |
| Shared core expands into platform-specific frontmatter | High | Keep new summary data in generated artifacts by default; require explicit compatibility review before changing shared `SKILL.md` fields |
| Skill deduplication accidentally changes semantics | High | Start with wording cleanup; defer true mergers |
| Repo metrics overstate real-world savings | Medium | Label all measurements as proxy metrics, not billing metrics |

## Rollback Strategy

Rollback must stay lightweight and repo-local.

### Phase 1 Rollback

- revert compact wording changes
- keep only baseline measurements

### Phase 2 Rollback

- disable compact eval mode
- continue using verbose prompt construction

### Phase 3 Rollback

- remove chain aliases from docs
- restore explicit chain wording where needed

## Deliverables

The plan should produce repository artifacts, not runtime infrastructure.

### Expected Outputs

- compact governance wording updates
- optional protocol `v2` documentation/rendering path
- compact skill summary/stub artifact generated outside the shared portable
  `SKILL.md` core by default
- slimmer evaluation prompt construction
- baseline size report for repo-controlled prompt surfaces
- updated maintainer docs describing scope and limits

## Appendix

## What This Plan No Longer Assumes

The repository-only version explicitly does **not** assume:

- access to platform request logs
- access to cache controls in production usage
- access to runtime prompt schedulers
- access to internal model orchestration
- access to staged rollout or A/B traffic splitting

## Future Architecture Notes

If an external runtime or proxy layer becomes available later, the following
ideas can be revisited outside this plan:

- prompt caching
- true lazy loading
- runtime adaptive depth
- checkpoint/delta state passing
- response-time and token telemetry
- rollout controls
