# Claude Interactive Fixture Workspace

This synthetic repository is the stable substrate for Claude Code interactive
acceptance runs.

It deliberately exposes a few small but realistic surfaces:

- reporting, billing, and notification code for scoping and planning behavior
- auth middleware, session storage, and role checks for parallelism decisions
- a small Go file with an obvious single-file bug for the negative serial case
- phase contract tooling for validator-focused maintenance work
- lightweight cache and expiry modules for evidence-based conflict resolution

The goal is not application correctness. The goal is to give Claude enough code
shape that multi-turn skill behavior can be observed without falling back to
"please show me the real repository."
