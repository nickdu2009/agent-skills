# Smoke Phase Roadmap

## Baseline

This smoke fixture exists to prove the shared phase contract helpers can validate and render a minimal strict four-file phase set.

## Goals

- keep the schema-valid fixture small and deterministic
- keep renderer goldens tied to one minimal PR and one minimal wave
- keep the owned smoke API subset aligned with `specs/smoke-api.yaml`

## External Contract Authority

- authority: `specs/smoke-api.yaml`
- owned subset: `paths./smoke`, `components.schemas.SmokeResponse`
- excluded subset: upstream-owned fixture paths

## Non-Goals

- no repository implementation work
- no extra phase-local planning files

## Validation Posture

- run the shared schema validator
- run the shared doc-set validator
- run the smoke runner to compare deterministic renderer output against committed goldens

## Phase Done-When

- the strict four-file fixture remains valid
- shared renderer outputs still match the smoke goldens
- the owned smoke API subset remains aligned or only accepted non-blocking gaps remain
