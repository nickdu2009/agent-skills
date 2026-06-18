# Architecture Design Principles Reference

This file is the principle checklist for the `architecture-design` skill. SKILL.md references it for principle validation at key decision points. Do not read this entire file upfront; read the relevant section when a specific decision point triggers a principle check.

## How to Use

Principles are organized by the architecture decision they validate. At each decision point in the execution pattern, check the corresponding principle group:

| Decision point | Check this section |
|---|---|
| Component decomposition | §1 Structural Principles |
| Interface definition | §2 Interface Principles |
| Technology selection | §3 Decision Principles |
| Non-functional design | §4 Runtime Quality Principles |
| Final architecture review | All sections (lightweight scan) |

Rules:
- Design from requirements first, then validate against principles.
- When principles conflict, record the trade-off: which principle was prioritized, which was relaxed, and why.
- Not every principle applies to every architecture. Skip principles that are irrelevant to the current scale and context.

## §1 Structural Principles

Use when decomposing components and drawing boundaries.

| Principle | Check | Violation signal |
|---|---|---|
| High Cohesion, Low Coupling | Each component does one category of work; inter-component interaction is through contracts, not shared internals | A component has 3+ unrelated responsibilities; two components share internal data structures |
| Separation of Concerns | Business logic, data access, presentation, and cross-cutting concerns (logging, auth, monitoring) have clear boundaries | Auth logic is scattered across 5 components; data access is mixed into business rules |
| Single Responsibility (component-level) | A component has one reason to change | "If we change the billing rules AND the notification channels, this component changes" → split |
| Encapsulation | Internal complexity is hidden behind a stable interface; internal refactoring does not affect callers | Callers depend on internal data structures or implementation sequence |

## §2 Interface Principles

Use when defining cross-component interfaces.

| Principle | Check | Violation signal |
|---|---|---|
| Dependency Inversion | High-level modules do not depend on low-level implementation details; dependency direction flows from unstable toward stable | A core business component imports a specific database driver directly |
| Interface Segregation | Cross-component interfaces are narrow and role-specific; do not expose capabilities the consumer does not need | A "do-everything" interface with 15 methods where each caller uses 2-3 |
| Least Astonishment | Data flow directions, naming conventions, and patterns are consistent and predictable across the architecture | Component A uses sync-request-response while component B uses fire-and-forget for similar interactions |

## §3 Decision Principles

Use when making technology choices and architectural trade-offs.

| Principle | Check | Violation signal |
|---|---|---|
| YAGNI / Right-sizing | Architecture complexity matches the current problem scale; do not add components or layers for hypothetical future needs | 3 microservices for a feature that could be 1 module; an event bus for 2 producers and 1 consumer |
| Reversibility | Prefer reversible architecture decisions; irreversible decisions (tech stack, storage engine, communication protocol) require stronger justification | Choosing a niche database with vendor lock-in without documenting why alternatives were rejected |
| Conway's Law Awareness | Architecture boundaries align with team boundaries; misalignment is explicitly acknowledged as organizational risk | A single service is owned by 3 teams; a service boundary splits a single team's domain |
| Appropriate Duplication vs. Coupling | In distributed systems, moderate duplication can be better than cross-service coupling; in monoliths, prefer eliminating duplication | A shared library forces 5 services to deploy together for a 1-line change |

## §4 Runtime Quality Principles

Use when designing non-functional architecture.

| Principle | Check | Violation signal |
|---|---|---|
| Design for Failure | Assume any component can fail; every external dependency has timeout, retry, and degradation strategy | No timeout on a downstream HTTP call; no fallback when the cache is unavailable |
| Defense in Depth | Security does not rely on a single barrier; authentication, authorization, input validation, and encryption are applied at multiple layers | "The API gateway handles auth, so internal services skip it entirely" |
| Design for Observability | Architecture includes injection points for logging, metrics, and tracing as first-class concerns; not bolted on after implementation | No structured logging strategy; no correlation ID propagation across components |
| Design for Evolvability | Core abstractions are stable but extensible; new capabilities can be added by adding components rather than modifying existing core | Adding a new notification channel requires modifying the core notification engine |
| Fail Fast | Invalid input and inconsistent state are surfaced as early as possible in the processing chain | Validation happens deep in the data layer instead of at the API boundary |
