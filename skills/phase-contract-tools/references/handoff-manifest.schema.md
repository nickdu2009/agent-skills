# Handoff Manifest Schema

Use this reference for immutable lane handoff artifacts derived from `plan.yaml`.

Machine validation lives in `handoff-manifest.schema.json`.

## Purpose

A lane handoff artifact should be self-describing and verifiable against the exact plan bytes it was rendered from.

Use it when:

- launching a worker from schema-derived instructions
- reusing an earlier handoff during resume
- verifying that a handoff was not paraphrased or reused after the plan changed

## Required Manifest Keys

Every handoff manifest should include:

- `handoff_schema_version`
- `phase`
- `wave_id`
- `wave_label`
- `lane`
- `owner`
- `ref_kind`
- `ref`
- `plan_path`
- `plan_sha256`
- `body_sha256`
- `generated_at`

## Field Rules

### `handoff_schema_version`

- string
- current value: `1.0`

### `phase`

- phase id derived from the plan

### `wave_id`

- integer wave id

### `wave_label`

- exact `waves[].label` value from the plan

### `lane`

- exact `lane_setup[].lane` value from the selected wave

### `owner`

- exact `lane_setup[].owner` value

### `ref_kind`

- exact `lane_setup[].ref_kind` value
- one of `pr` or `role`

### `ref`

- exact `lane_setup[].ref` value

### `plan_path`

- resolved absolute path to the plan file used for rendering

### `plan_sha256`

- SHA-256 digest of the exact plan bytes used for rendering

### `body_sha256`

- SHA-256 digest of the exact handoff body text

### `generated_at`

- UTC ISO-8601 timestamp

## Handoff Body Rules

The handoff body should be:

- rendered from the schema without paraphrase
- stable enough to re-render and compare under `--strict`
- rejected if the plan digest no longer matches

## Minimal Example

```yaml
handoff_schema_version: "1.0"
phase: "phase13"
wave_id: 1
wave_label: "Wave 1"
lane: "A"
owner: "agent_a"
ref_kind: "pr"
ref: "P13-01"
plan_path: "/repo/docs/phase13-plan.yaml"
plan_sha256: "abc123..."
body_sha256: "def456..."
generated_at: "2026-03-27T08:57:54+00:00"
```

## Anti-Patterns

Do not:

- regenerate the body and keep the old digest
- reuse a handoff after the plan changed
- rewrite the body without updating the digest
- treat the handoff body as advisory prose instead of a contract artifact
