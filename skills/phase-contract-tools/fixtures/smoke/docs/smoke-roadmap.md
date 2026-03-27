# Smoke Phase Roadmap

## Baseline

This smoke fixture exists to prove the shared phase contract helpers can validate and render a minimal strict four-file phase set.

## Goals

- keep the schema-valid fixture small and deterministic
- keep renderer goldens tied to one minimal PR and one minimal wave

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
