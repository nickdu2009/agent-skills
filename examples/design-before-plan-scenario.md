# Design-Before-Plan Scenario

## Scenario Type
Design decision with multiple approaches and cross-module impact.

## Task Description
"Add support for batch operations to our API. Users need to submit multiple items at once instead of making individual requests."

## Initial State
- Existing REST API with single-item endpoints: `POST /items`, `PUT /items/{id}`, `DELETE /items/{id}`
- Authentication middleware validates each request
- Rate limiting tracks requests per user per minute
- Database uses row-level locking for updates

## Recommended Skill Composition
1. `scoped-tasking` — narrow the initial boundary (which endpoints? what batch size?)
2. **`design-before-plan`** — compare batch API designs, define contracts, establish acceptance criteria
3. `implementation-planning` — convert the chosen design into a durable implementation plan with per-step verify checks
4. `targeted-validation` — validate batch semantics (atomicity, partial failures)

## Expected Agent Behavior

### Phase 1: Scoping (scoped-tasking)
- Clarify batch scope: which operations? (create, update, delete, or all?)
- Establish batch size limit (10? 100? 1000?)
- Define validation boundary: existing tests + new batch tests

### Phase 2: Design (design-before-plan) — **this skill triggers here**

**Requirements clarification:**
- Functional:
  - Users can submit up to 100 items in a single request
  - Support batch create and batch update (delete excluded for safety)
  - Return per-item results indicating success or failure
- Non-functional:
  - Maintain p95 latency < 2s for batches of 10 items
  - Preserve existing rate limit semantics
- Implicit NFR candidates (check ≠ adopt; each has source/status/blocking):
  - Security:
    - Validate batch size limit (max 100) to prevent DoS — source: scoped functional limit; status: confirmed
    - Reuse existing authentication (single token validates entire batch) — source: existing contract; status: confirmed
    - Validate each item against same authorization rules as single-item endpoint — source: existing contract; status: confirmed
  - Performance:
    - Process items in transaction batches (candidate size TBD) to avoid long-running transactions — status: open; blocking: false for design choice of endpoint shape
    - Database connection pooling must handle batch workload without exhaustion — status: open; blocking: false
  - Observability:
    - Log batch start/complete with item count and duration — status: open; blocking: false
    - Emit metrics: batch_size, batch_duration_seconds, items_succeeded, items_failed — status: open; blocking: false
    - Include batch_id in logs for request correlation — status: open; blocking: false
  - Resilience (must ask before adopting):
    - Batch processing timeout value — status: open; blocking: true (do not invent "30 seconds")
    - Partial-failure mode (all-or-nothing vs best-effort) — status: open; blocking: true (do not invent a default)
- Edge cases:
  - Partial failures (item 3 fails validation, others succeed) — ask whether this is required
  - Transaction semantics (all-or-nothing vs. best-effort) — confirm with user before chosen_design

**Design alternatives:**
1. **Single endpoint with batch payload:**
   - Endpoint: `POST /items/batch` with `{ items: [...] }`
   - Pros: clear separation from single-item endpoint, explicit batch semantics
   - Cons: new endpoint, client must use different code path
   - Blast radius: 2 files (new controller + routes)

2. **Extend existing endpoint to accept arrays:**
   - Endpoint: `POST /items` accepts `{ items: [...] }` or single `{ item: {...} }`
   - Pros: client can use same endpoint for single and batch
   - Cons: payload polymorphism complicates validation, confusing semantics
   - Blast radius: 1 file (existing controller)

3. **GraphQL-style mutation:**
   - Endpoint: `POST /graphql` with `mutation { createItems(items: [...]) }`
   - Pros: consistent with modern API patterns, introspection support
   - Cons: requires GraphQL dependency, large migration scope
   - Blast radius: 8+ files (new GraphQL layer)

**Clarification before chosen_design (behavioral NFRs):**
- User confirms: default mode is best-effort (`options.atomic=false`); atomic mode available on request.
- User confirms: batch processing timeout is 30 seconds; exceeded batches fail closed with a structured timeout error (no silent partial success beyond completed items already returned).

**Chosen design:**
- Approach: Single batch endpoint (`POST /items/batch`)
- Rationale:
  - Clear contract separation (no payload polymorphism)
  - Smallest blast radius among non-trivial options
  - Existing REST clients can adopt incrementally
- Authorized behavioral decisions (only after confirmation above):
  - Default best-effort mode with optional atomic flag
  - 30s batch timeout with fail-closed structured error
- Deferred:
  - GraphQL layer (future: when 3+ batch operations exist, revisit)
  - WebSocket streaming for large batches (optimization for future)

**ADR threshold and artifact:**
- This API contract crosses routing, controller, validation, rate-limiting, and client adoption boundaries and is costly to reverse.
- Emit `ADR-0042: Use a dedicated REST batch endpoint` as a vendor-neutral Proposed ADR artifact.
- Record the three alternatives, positive/negative consequences, and revisit conditions in the artifact.
- Add `adr_candidates: [ADR-0042]`; keep `linked_adrs` empty.

**Interface contracts:**
- Request:
  ```json
  {
    "items": [
      { "name": "item1", "value": 10 },
      { "name": "item2", "value": 20 }
    ],
    "options": {
      "atomic": false  // default best-effort — confirmed by user before chosen_design
    }
  }
  ```
- Response:
  ```json
  {
    "results": [
      { "index": 0, "status": "success", "id": "123" },
      { "index": 1, "status": "error", "error": "duplicate name" }
    ],
    "summary": {
      "total": 2,
      "succeeded": 1,
      "failed": 1
    }
  }
  ```
- Error handling:
  - 400 if batch size exceeds 100
  - 207 Multi-Status for partial failures
  - Preserve original error codes in per-item results
- Backward compatibility:
  - Existing `POST /items` unchanged
  - Authentication and rate limiting apply to batch endpoint

**Acceptance criteria:**
- Must-have:
  - Batch of 10 items completes in < 2s (p95)
  - Partial failures return per-item error details
  - Atomic mode (if requested) rolls back all items on any failure
- Nice-to-have:
  - Batch progress callback (streaming response)
- Validation boundary:
  - Integration test with 100-item batch
  - Test partial failure scenarios (mix of valid/invalid items)
  - Test atomic vs. best-effort modes
  - Verify rate limiter counts 1 request (not 100) for batch

**Architectural constraints:**
- Database: row-level locking may cause contention for large batches
- Rate limiter: must count batch as 1 request (not N requests)
- Authentication: single token validates entire batch (no per-item auth)

### Phase 3: Planning (`implementation-planning`)
Consumes the design brief and produces a durable per-step plan with verify checks:
- Goal: implement `POST /items/batch` endpoint with confirmed best-effort default and 30s timeout
- Scope: 2 files (batch controller, routes)
- Mechanical assumption: existing item validation logic is reusable (behavior-preserving)
- Behavioral assumptions: none remaining — timeout and failure mode were confirmed in design
- Intended files: `routes/items.js`, `controllers/batch_items_controller.js`, `tests/batch_items.test.js`
- Plan:
  1. Add route + controller skeleton → verify: route table updated, 200 OK on empty array
  2. Wire per-item validation reuse → verify: invalid item returns structured error
  3. Add batch size guard + rate-limit-1 marker → verify: oversized batch returns 400
  4. Write integration tests for partial failure → verify: tests pass

Execute the plan, validate with batch integration tests.

## Anti-Patterns to Avoid

### ❌ Skipping design enumeration
Agent immediately proposes extending existing `POST /items` to accept arrays without comparing alternatives. User later realizes payload polymorphism creates confusing semantics. Refactor required.

### ❌ Deriving acceptance criteria from implementation
Agent states "batch endpoint returns 200 OK" as acceptance criteria. This is an implementation detail, not a requirement-based success condition. Correct criterion: "Partial failures return per-item error details."

### ❌ Missing interface contract definition
Agent starts implementing batch endpoint without defining the request/response schema first. During implementation, agent realizes atomic vs. best-effort modes need different response formats. Contract changes mid-implementation, requiring test rewrites.

### ❌ Ignoring implicit requirements
Agent designs batch endpoint focusing only on explicit functional requirements (accept array, return results). Production deploy reveals:
- **Security gap**: No batch size validation, attacker submits 100K-item batch causing DoS
- **Performance issue**: All items processed in single transaction, causing 30s lock contention and timeout
- **Observability gap**: No logging/metrics, cannot diagnose why 20% of batches are failing
- **Resilience gap**: No timeout, hung batch blocks worker thread indefinitely

Correct approach: During design phase, explicitly check implicit requirements triggered by "batch API with external input" → security (size limits, auth), performance (transaction batching), observability (logs/metrics), resilience (timeouts).

## Success Indicators

- ✅ Agent enumerates 2-4 design alternatives before choosing one
- ✅ Agent documents design rationale (why chosen, why others rejected)
- ✅ Agent identifies implicit requirements (security: batch size limit; performance: transaction batching; observability: logs/metrics; resilience: timeout)
- ✅ Agent defines complete interface contract (request, response, errors) before planning
- ✅ Agent derives acceptance criteria from requirements (not from implementation details)
- ✅ Agent flags architectural constraints (rate limiter, database locking)
- ✅ Agent outputs a structured design brief consumed by `implementation-planning`
- ✅ Agent emits a portable ADR candidate for the long-lived cross-module API decision without assuming a persistence system

## Skill Protocol v2 Trace

```
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[triggers: scoped-tasking:trigger design-before-plan:trigger]
[precheck: design-before-plan | result:PASS | checks:alternatives_exist acceptance_criteria_unfrozen]
[output: design-before-plan | status:completed | confidence:high | requirements:"Support batch create and update up to 100 items" | alternatives:"Single batch endpoint, Extend existing endpoint, GraphQL mutation" | chosen_design:"POST /items/batch" | rationale:"Clear contract separation with smallest acceptable blast radius" | acceptance_criteria:"Per-item partial failure details are returned; Batches of 10 finish within 2 seconds p95" linked_adrs:"none" adr_candidates:"ADR-0042:Use a dedicated REST batch endpoint:Proposed" | planning_ready:true | next:artifact-review-loop:design]
[validate: design-before-plan | result:PASS | checks:alternatives acceptance_criteria]
[drop: design-before-plan | reason:"design brief complete, ready for implementation-planning" | active:none]
```
