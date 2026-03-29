#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Validate a phase execution schema for structure and cross-reference integrity."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode


TOP_LEVEL_REQUIRED = {
    "schema_version",
    "last_updated",
    "status",
    "scope",
    "hard_rules",
    "schema_conventions",
    "placeholder_conventions",
    "validation_profiles",
    "team",
    "hotspots",
    "prs",
    "waves",
}

PR_REQUIRED = {
    "id",
    "title",
    "milestone",
    "type",
    "owner",
    "wave",
    "depends_on",
    "goal",
    "read_first",
    "start_condition",
    "scope",
    "files",
    "expected_changes",
    "guardrails",
    "non_goals",
    "validation",
    "done_when",
}

WAVE_REQUIRED = {
    "id",
    "label",
    "goal",
    "control_pr",
    "prs",
    "merge_order",
    "lane_setup",
    "constraints",
    "integrator_checklist",
}

PLACEHOLDER_RE = re.compile(r"<[^>]+>")
START_GATE_VALUES = {"immediate", "after_prs", "after_waves"}
VALIDATION_KINDS = {"profile", "command"}
OWNED_SCOPE_MODES = {"full", "subset"}
VAGUE_PHRASE_PATTERNS = (
    "as needed",
    "if needed",
    "where appropriate",
    "related",
    "relevant",
    "etc",
    "and so on",
    "be careful",
    "make sure",
    "improve things",
    "clean up",
    "looks good",
    "when ready",
)
CONTRACT_SENSITIVE_PATTERNS = (
    "openapi",
    "webhook",
    "public api",
    "public contract",
    "contract authority",
    "legacy dto",
    "route shape",
    "owned subset",
)
INVALID_CONTRACT_COMPLETION_PATTERNS = (
    "adapter unavailable",
    "legacy dto reuse",
    "temporary route alias",
    "fail-closed",
)


class Issue:
    def __init__(
        self,
        path: str,
        message: str,
        expected: str | None,
        location: str,
        repair: str | None = None,
    ) -> None:
        self.path = path
        self.message = message
        self.expected = expected
        self.location = location
        self.repair = repair

    def render(self, level: str) -> str:
        lines = [f"{level} {self.path}: {self.message}"]
        if self.expected:
            lines.append(f"expected: {self.expected}")
        if self.repair:
            lines.append(f"repair: {self.repair}")
        lines.append(f"location: {self.location}")
        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a phase execution schema.")
    parser.add_argument("--plan", required=True, help="Path to docs/phaseN-plan.yaml")
    return parser.parse_args()


def load_yaml(path: Path) -> tuple[dict[str, Any], dict[tuple[Any, ...], int]]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("Top-level YAML value must be a mapping.")
    root = yaml.compose(text)
    line_map: dict[tuple[Any, ...], int] = {}
    if root is not None:
        walk_node(root, (), line_map)
    return data, line_map


def walk_node(node: Node, path: tuple[Any, ...], line_map: dict[tuple[Any, ...], int]) -> None:
    line_map.setdefault(path, node.start_mark.line + 1)
    if isinstance(node, MappingNode):
        for key_node, value_node in node.value:
            if not isinstance(key_node, ScalarNode):
                continue
            key = key_node.value
            key_path = path + (key,)
            line_map.setdefault(key_path, key_node.start_mark.line + 1)
            walk_node(value_node, key_path, line_map)
    elif isinstance(node, SequenceNode):
        for idx, item_node in enumerate(node.value):
            item_path = path + (idx,)
            line_map.setdefault(item_path, item_node.start_mark.line + 1)
            walk_node(item_node, item_path, line_map)


def path_str(path: tuple[Any, ...]) -> str:
    if not path:
        return "<root>"
    parts: list[str] = []
    for part in path:
        if isinstance(part, int):
            if not parts:
                parts.append(f"[{part}]")
            else:
                parts[-1] = f"{parts[-1]}[{part}]"
        else:
            parts.append(str(part))
    return ".".join(parts)


def location_for(file_path: Path, line_map: dict[tuple[Any, ...], int], path: tuple[Any, ...]) -> str:
    probe = path
    while probe:
        if probe in line_map:
            return f"{file_path}:{line_map[probe]}"
        probe = probe[:-1]
    if () in line_map:
        return f"{file_path}:{line_map[()]}"
    return str(file_path)


def add_issue(
    bucket: list[Issue],
    file_path: Path,
    line_map: dict[tuple[Any, ...], int],
    path: tuple[Any, ...],
    message: str,
    expected: str | None = None,
    repair: str | None = None,
) -> None:
    bucket.append(Issue(path_str(path), message, expected, location_for(file_path, line_map, path), repair))


def walk_strings(value: Any, path: tuple[Any, ...]):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, path + (key,))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            yield from walk_strings(item, path + (idx,))
    elif isinstance(value, str):
        yield path, value


def looks_contract_sensitive(value: Any) -> bool:
    for _, text in walk_strings(value, ()):
        lowered = text.lower()
        if any(pattern in lowered for pattern in CONTRACT_SENSITIVE_PATTERNS):
            return True
    return False


def validate_read_first_entries(
    errors: list[Issue],
    plan_path: Path,
    line_map: dict[tuple[Any, ...], int],
    base_path: tuple[Any, ...],
    entries: Any,
    phase_name: str,
    allowed_phase_docs: set[str],
) -> None:
    if not isinstance(entries, list):
        add_issue(errors, plan_path, line_map, base_path, "read_first must be a list.", expected="a list", repair="rewrite read_first as an ordered list of document reference mappings")
        return
    for idx, entry in enumerate(entries):
        entry_path = base_path + (idx,)
        if not isinstance(entry, dict):
            add_issue(errors, plan_path, line_map, entry_path, "read_first entry must be a mapping.", repair="rewrite the entry as a mapping with path and optional section")
            continue
        path_value = entry.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            add_issue(errors, plan_path, line_map, entry_path + ("path",), "read_first.path must be a non-empty string.", repair="set read_first.path to a document path")
            continue
        if f"docs/{phase_name}-" in path_value and path_value not in allowed_phase_docs:
            add_issue(
                errors,
                plan_path,
                line_map,
                entry_path + ("path",),
                "phase-local read_first reference points outside the strict four-file set.",
                expected=f"one of {sorted(allowed_phase_docs)}",
                repair="replace the read_first path with roadmap, plan.yaml, wave-guide, or execution-index",
            )
        section_value = entry.get("section")
        if section_value is not None and (not isinstance(section_value, str) or not section_value.strip()):
            add_issue(errors, plan_path, line_map, entry_path + ("section",), "read_first.section must be a non-empty string when present.", repair="remove section or replace it with a short section hint")


def validate_validation_entries(
    errors: list[Issue],
    plan_path: Path,
    line_map: dict[tuple[Any, ...], int],
    base_path: tuple[Any, ...],
    entries: Any,
    profile_ids: set[str],
    declared_tokens: set[str],
) -> None:
    if not isinstance(entries, list):
        add_issue(errors, plan_path, line_map, base_path, "validation must be a list.", expected="a list", repair="rewrite validation as an ordered list of validation mappings")
        return
    for idx, entry in enumerate(entries):
        entry_path = base_path + (idx,)
        if not isinstance(entry, dict):
            add_issue(errors, plan_path, line_map, entry_path, "validation entry must be a mapping.", repair="rewrite the validation entry as a mapping with kind plus ref or command")
            continue
        kind = entry.get("kind")
        if kind not in VALIDATION_KINDS:
            add_issue(
                errors,
                plan_path,
                line_map,
                entry_path + ("kind",),
                f"invalid validation kind `{kind}`.",
                expected=f"one of {sorted(VALIDATION_KINDS)}",
                repair="set validation.kind to profile or command",
            )
            continue
        if kind == "profile":
            ref = entry.get("ref")
            if not isinstance(ref, str) or not ref.strip():
                add_issue(errors, plan_path, line_map, entry_path + ("ref",), "validation.ref must be a non-empty string for profile entries.", repair="set validation.ref to an existing validation profile id")
            elif ref not in profile_ids:
                add_issue(
                    errors,
                    plan_path,
                    line_map,
                    entry_path + ("ref",),
                    f"unknown validation profile `{ref}`.",
                    expected=f"one of {sorted(profile_ids)}",
                    repair="change validation.ref to an existing profile id or add the missing profile under validation_profiles",
                )
        elif kind == "command":
            command = entry.get("command")
            if not isinstance(command, str) or not command.strip():
                add_issue(errors, plan_path, line_map, entry_path + ("command",), "validation.command must be a non-empty string for command entries.", repair="set validation.command to a runnable shell command")
            else:
                for token in PLACEHOLDER_RE.findall(command):
                    if token not in declared_tokens:
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            entry_path + ("command",),
                            f"undeclared placeholder token `{token}`.",
                            expected=f"one of {sorted(declared_tokens)}" if declared_tokens else "declare the token under placeholder_conventions",
                            repair="declare the placeholder token under placeholder_conventions or remove it from the command",
                        )


def expect_type(
    issues: list[Issue],
    file_path: Path,
    line_map: dict[tuple[Any, ...], int],
    path: tuple[Any, ...],
    value: Any,
    expected_type: type,
    expected_label: str,
) -> bool:
    if not isinstance(value, expected_type):
        add_issue(
            issues,
            file_path,
            line_map,
            path,
            f"got {type(value).__name__}, not {expected_label}.",
            expected=expected_label,
        )
        return False
    return True


def validate_schema(plan_path: Path) -> tuple[list[Issue], list[Issue]]:
    errors: list[Issue] = []
    warnings: list[Issue] = []

    try:
        data, line_map = load_yaml(plan_path)
    except FileNotFoundError:
        return [Issue("--plan", "file not found.", None, str(plan_path))], []
    except Exception as exc:  # noqa: BLE001
        return [Issue("--plan", f"unable to parse YAML: {exc}", None, str(plan_path))], []

    for key in sorted(TOP_LEVEL_REQUIRED):
        if key not in data:
            add_issue(
                errors,
                plan_path,
                line_map,
                (),
                f"missing top-level field `{key}`.",
                expected=key,
                repair=f"add `{key}` at the top level of the plan schema",
            )

    phase_name = plan_path.stem[:-5] if plan_path.stem.endswith("-plan") else plan_path.stem
    allowed_phase_docs = {
        f"docs/{phase_name}-roadmap.md",
        f"docs/{phase_name}-plan.yaml",
        f"docs/{phase_name}-wave-guide.md",
        f"docs/{phase_name}-execution-index.md",
    }
    deprecated_doc_names = {
        f"docs/{phase_name}-first-wave-pr-breakdown.md",
        f"docs/{phase_name}-parallel-matrix.md",
        f"docs/{phase_name}-pr-delivery-plan.md",
        f"docs/{phase_name}-pr-parallelization-plan.md",
        f"docs/{phase_name}-pr-plan.md",
    }
    for string_path, text in walk_strings(data, ()):
        for deprecated in deprecated_doc_names:
            if deprecated in text:
                add_issue(
                    errors,
                    plan_path,
                    line_map,
                    string_path,
                    f"deprecated phase doc reference `{deprecated}` is not allowed in the strict four-file model.",
                    expected="use roadmap, wave-guide, execution-index, or plan.yaml references only",
                    repair="replace the deprecated doc reference with one of the four allowed phase files",
                )
        lowered = text.lower()
        if any(part in string_path for part in ("goal", "guardrails", "non_goals", "done_when", "expected_changes", "note", "allow", "deny")):
            for phrase in VAGUE_PHRASE_PATTERNS:
                if phrase in lowered:
                    add_issue(
                        errors,
                        plan_path,
                        line_map,
                        string_path,
                        f"vague execution phrase `{phrase}` is not allowed in execution-critical fields.",
                        expected="a concrete file, package, PR gate, invariant, or validation outcome",
                        repair="replace the vague phrase with an explicit scope, dependency, invariant, or stop condition",
                    )

    team = data.get("team")
    team_ids: set[str] = set()
    if expect_type(errors, plan_path, line_map, ("team",), team, list, "a list"):
        for idx, member in enumerate(team):
            member_path = ("team", idx)
            if not isinstance(member, dict):
                add_issue(errors, plan_path, line_map, member_path, "team entry must be a mapping.", repair="rewrite the team entry as a mapping with id, label, focus, owns, and avoid fields")
                continue
            member_id = member.get("id")
            if not isinstance(member_id, str) or not member_id:
                add_issue(errors, plan_path, line_map, member_path + ("id",), "team id must be a non-empty string.", repair="set team[].id to a stable non-empty string and reuse it everywhere owner is referenced")
                continue
            if member_id in team_ids:
                add_issue(errors, plan_path, line_map, member_path + ("id",), f"duplicate team id `{member_id}`.", repair="rename one of the duplicate team ids so every owner id is unique")
            team_ids.add(member_id)

    placeholder_conventions = data.get("placeholder_conventions")
    declared_tokens: set[str] = set()
    if expect_type(
        errors,
        plan_path,
        line_map,
        ("placeholder_conventions",),
        placeholder_conventions,
        dict,
        "a mapping",
    ):
        for name, spec in placeholder_conventions.items():
            token_path = ("placeholder_conventions", name, "token")
            if not isinstance(spec, dict):
                add_issue(errors, plan_path, line_map, ("placeholder_conventions", name), "placeholder spec must be a mapping.", repair="rewrite the placeholder entry as a mapping with token, meaning, and example")
                continue
            token = spec.get("token")
            if not isinstance(token, str) or not token:
                add_issue(errors, plan_path, line_map, token_path, "placeholder token must be a non-empty string.", repair="set placeholder_conventions.*.token to the literal token used in commands")
                continue
            if token in declared_tokens:
                add_issue(errors, plan_path, line_map, token_path, f"duplicate placeholder token `{token}`.", repair="keep one declaration per placeholder token")
            declared_tokens.add(token)

    validation_profiles = data.get("validation_profiles")
    profile_ids: set[str] = set()
    if expect_type(
        errors,
        plan_path,
        line_map,
        ("validation_profiles",),
        validation_profiles,
        dict,
        "a mapping",
    ):
        for profile_id, spec in validation_profiles.items():
            profile_ids.add(profile_id)
            profile_path = ("validation_profiles", profile_id)
            if not isinstance(spec, dict):
                add_issue(errors, plan_path, line_map, profile_path, "validation profile must be a mapping.", repair="rewrite the profile as a mapping with description and command")
                continue
            command = spec.get("command")
            if not isinstance(command, str) or not command.strip():
                add_issue(errors, plan_path, line_map, profile_path + ("command",), "validation profile command must be a non-empty string.", repair="set validation_profiles.*.command to a runnable shell command")

    external_contracts = data.get("external_contracts", [])
    contract_ids: set[str] = set()
    if expect_type(
        errors,
        plan_path,
        line_map,
        ("external_contracts",),
        external_contracts,
        list,
        "a list",
    ):
        for idx, contract in enumerate(external_contracts):
            contract_path = ("external_contracts", idx)
            if not isinstance(contract, dict):
                add_issue(errors, plan_path, line_map, contract_path, "external contract entry must be a mapping.", repair="rewrite the contract entry as a mapping with id, path, kind, authority, and owned_scope")
                continue
            contract_id = contract.get("id")
            if not isinstance(contract_id, str) or not contract_id.strip():
                add_issue(errors, plan_path, line_map, contract_path + ("id",), "external contract id must be a non-empty string.", repair="set external_contracts[].id to a stable contract id")
            elif contract_id in contract_ids:
                add_issue(errors, plan_path, line_map, contract_path + ("id",), f"duplicate external contract id `{contract_id}`.", repair="rename one of the duplicate external contract ids")
            else:
                contract_ids.add(contract_id)
            contract_source = contract.get("path")
            if not isinstance(contract_source, str) or not contract_source.strip():
                add_issue(errors, plan_path, line_map, contract_path + ("path",), "external contract path must be a non-empty string.", repair="set external_contracts[].path to the contract source path")
            kind = contract.get("kind")
            if not isinstance(kind, str) or not kind.strip():
                add_issue(errors, plan_path, line_map, contract_path + ("kind",), "external contract kind must be a non-empty string.", repair="set external_contracts[].kind to a short source type such as openapi or yaml")
            authority = contract.get("authority")
            if authority != "external_contract":
                add_issue(errors, plan_path, line_map, contract_path + ("authority",), f"external contract authority must stay `external_contract`, not `{authority}`.", expected="external_contract", repair="set external_contracts[].authority to `external_contract`")
            owned_scope = contract.get("owned_scope")
            if expect_type(errors, plan_path, line_map, contract_path + ("owned_scope",), owned_scope, dict, "a mapping"):
                mode = owned_scope.get("mode")
                if mode not in OWNED_SCOPE_MODES:
                    add_issue(errors, plan_path, line_map, contract_path + ("owned_scope", "mode"), f"invalid owned_scope mode `{mode}`.", expected=f"one of {sorted(OWNED_SCOPE_MODES)}", repair="set owned_scope.mode to full or subset")
                for field in ("include", "exclude"):
                    value = owned_scope.get(field)
                    if not isinstance(value, list):
                        add_issue(errors, plan_path, line_map, contract_path + ("owned_scope", field), f"owned_scope.{field} must be a list.", expected="a list", repair=f"rewrite owned_scope.{field} as a list of scope strings")

    accepted_contract_gaps = data.get("accepted_contract_gaps", [])
    if expect_type(
        errors,
        plan_path,
        line_map,
        ("accepted_contract_gaps",),
        accepted_contract_gaps,
        list,
        "a list",
    ):
        for idx, gap in enumerate(accepted_contract_gaps):
            gap_path = ("accepted_contract_gaps", idx)
            if not isinstance(gap, dict):
                add_issue(errors, plan_path, line_map, gap_path, "accepted contract gap entry must be a mapping.", repair="rewrite the gap entry as a mapping with id, contract, scope, reason, blocking, and accepted_by")
                continue
            for field in ("id", "contract", "scope", "reason", "accepted_by"):
                value = gap.get(field)
                if not isinstance(value, str) or not value.strip():
                    add_issue(errors, plan_path, line_map, gap_path + (field,), f"`{field}` must be a non-empty string.", repair=f"set accepted_contract_gaps[].{field} to a non-empty string")
            if gap.get("contract") not in contract_ids:
                add_issue(errors, plan_path, line_map, gap_path + ("contract",), f"unknown external contract `{gap.get('contract')}`.", expected=f"one of {sorted(contract_ids)}", repair="set accepted_contract_gaps[].contract to a declared external contract id")
            if not isinstance(gap.get("blocking"), bool):
                add_issue(errors, plan_path, line_map, gap_path + ("blocking",), "`blocking` must be a boolean.", expected="true or false", repair="set accepted_contract_gaps[].blocking to true or false")

    prs = data.get("prs")
    pr_ids: set[str] = set()
    pr_to_wave: dict[str, int] = {}
    if expect_type(errors, plan_path, line_map, ("prs",), prs, list, "a list"):
        for idx, pr in enumerate(prs):
            pr_path = ("prs", idx)
            if not isinstance(pr, dict):
                add_issue(errors, plan_path, line_map, pr_path, "PR entry must be a mapping.", repair="rewrite the PR entry as a mapping with the required PR fields")
                continue
            missing = sorted(PR_REQUIRED - set(pr))
            for key in missing:
                add_issue(errors, plan_path, line_map, pr_path, f"missing required PR field `{key}`.", expected=key, repair=f"add `{key}` to this PR entry")
            pr_id = pr.get("id")
            if not isinstance(pr_id, str) or not pr_id:
                add_issue(errors, plan_path, line_map, pr_path + ("id",), "PR id must be a non-empty string.", repair="set prs[].id to a stable non-empty PR id")
                continue
            if pr_id in pr_ids:
                add_issue(errors, plan_path, line_map, pr_path + ("id",), f"duplicate PR id `{pr_id}`.", repair="rename one of the duplicate PR ids and update all references to it")
            pr_ids.add(pr_id)

            owner = pr.get("owner")
            if owner not in team_ids:
                add_issue(
                    errors,
                    plan_path,
                    line_map,
                    pr_path + ("owner",),
                    f"unknown owner `{owner}`.",
                    expected=f"one of {sorted(team_ids)}",
                    repair="change the owner to a declared team[].id or add the missing team entry",
                )
            wave = pr.get("wave")
            if not isinstance(wave, int):
                add_issue(errors, plan_path, line_map, pr_path + ("wave",), "wave must be an integer.", repair="set prs[].wave to the numeric wave id that owns this PR")
            else:
                pr_to_wave[pr_id] = wave

            depends_on = pr.get("depends_on")
            if expect_type(errors, plan_path, line_map, pr_path + ("depends_on",), depends_on, list, "a list"):
                for dep_idx, dep in enumerate(depends_on):
                    if not isinstance(dep, str):
                        add_issue(errors, plan_path, line_map, pr_path + ("depends_on", dep_idx), "dependency must be a PR id string.", repair="replace the dependency entry with a referenced PR id string")

            scope = pr.get("scope")
            if expect_type(errors, plan_path, line_map, pr_path + ("scope",), scope, dict, "a mapping"):
                for field in ("allow", "deny"):
                    if field not in scope:
                        add_issue(errors, plan_path, line_map, pr_path + ("scope",), f"scope is missing `{field}`.", expected=field, repair=f"add scope.{field} as a list")
                    elif not isinstance(scope[field], list):
                        add_issue(errors, plan_path, line_map, pr_path + ("scope", field), f"scope.{field} must be a list.", repair=f"rewrite scope.{field} as a list of strings")

            start_condition = pr.get("start_condition")
            if expect_type(errors, plan_path, line_map, pr_path + ("start_condition",), start_condition, dict, "a mapping"):
                gate = start_condition.get("gate")
                refs = start_condition.get("refs")
                if gate not in START_GATE_VALUES:
                    add_issue(
                        errors,
                        plan_path,
                        line_map,
                        pr_path + ("start_condition", "gate"),
                        f"invalid start gate `{gate}`.",
                        expected=f"one of {sorted(START_GATE_VALUES)}",
                        repair="set start_condition.gate to immediate, after_prs, or after_waves",
                    )
                if not isinstance(refs, list):
                    add_issue(
                        errors,
                        plan_path,
                        line_map,
                        pr_path + ("start_condition", "refs"),
                        "start_condition.refs must be a list.",
                        expected="a list",
                        repair="rewrite start_condition.refs as an ordered list of PR ids or wave ids",
                    )
                elif gate == "immediate" and refs:
                    add_issue(
                        errors,
                        plan_path,
                        line_map,
                        pr_path + ("start_condition", "refs"),
                        "immediate start_condition must use an empty refs list.",
                        expected="[]",
                        repair="clear start_condition.refs when gate is immediate",
                    )
                elif gate == "after_prs":
                    for ref_idx, ref in enumerate(refs):
                        if ref not in pr_ids:
                            add_issue(
                                errors,
                                plan_path,
                                line_map,
                                pr_path + ("start_condition", "refs", ref_idx),
                                f"unknown PR gate `{ref}`.",
                                expected=f"one of {sorted(pr_ids)}",
                                repair="replace the gate ref with an existing PR id",
                            )
                elif gate == "after_waves":
                    for ref_idx, ref in enumerate(refs):
                        if not isinstance(ref, int):
                            add_issue(
                                errors,
                                plan_path,
                                line_map,
                                pr_path + ("start_condition", "refs", ref_idx),
                                "wave gate ref must be an integer wave id.",
                                expected="an integer wave id",
                                repair="replace the gate ref with a numeric wave id",
                            )

            validate_read_first_entries(errors, plan_path, line_map, pr_path + ("read_first",), pr.get("read_first"), phase_name, allowed_phase_docs)
            validate_validation_entries(errors, plan_path, line_map, pr_path + ("validation",), pr.get("validation"), profile_ids, declared_tokens)

            required_contracts = pr.get("required_contracts", [])
            if required_contracts is not None and not isinstance(required_contracts, list):
                add_issue(errors, plan_path, line_map, pr_path + ("required_contracts",), "required_contracts must be a list when present.", expected="a list", repair="rewrite required_contracts as an ordered list of external contract ids")
                required_contracts = []
            if isinstance(required_contracts, list):
                for contract_idx, contract_id in enumerate(required_contracts):
                    if not isinstance(contract_id, str) or not contract_id.strip():
                        add_issue(errors, plan_path, line_map, pr_path + ("required_contracts", contract_idx), "required_contracts entry must be a non-empty contract id string.", repair="replace the entry with a declared external contract id")
                    elif contract_id not in contract_ids:
                        add_issue(errors, plan_path, line_map, pr_path + ("required_contracts", contract_idx), f"unknown required contract `{contract_id}`.", expected=f"one of {sorted(contract_ids)}", repair="replace the contract id with one declared under external_contracts")

            has_required_contracts = isinstance(required_contracts, list) and any(isinstance(item, str) and item.strip() for item in required_contracts)
            for field in ("contract_guardrails", "contract_done_when"):
                value = pr.get(field, [])
                if value is not None and not isinstance(value, list):
                    add_issue(errors, plan_path, line_map, pr_path + (field,), f"`{field}` must be a list when present.", expected="a list", repair=f"rewrite `{field}` as a list of concrete contract checks")
                    continue
                if has_required_contracts and not value:
                    add_issue(errors, plan_path, line_map, pr_path + (field,), f"`{field}` is required when required_contracts is non-empty.", expected=f"a non-empty `{field}` list", repair=f"add at least one concrete entry under `{field}`")
                for item_idx, item in enumerate(value or []):
                    if not isinstance(item, str) or not item.strip():
                        add_issue(errors, plan_path, line_map, pr_path + (field, item_idx), f"`{field}` entry must be a non-empty string.", repair=f"replace the `{field}` entry with a concrete contract rule")
                    elif field == "contract_done_when":
                        lowered = item.lower()
                        for invalid_phrase in INVALID_CONTRACT_COMPLETION_PATTERNS:
                            if invalid_phrase in lowered:
                                add_issue(errors, plan_path, line_map, pr_path + (field, item_idx), f"invalid contract completion phrase `{invalid_phrase}` is not allowed.", expected="a contract alignment outcome, not a fallback or legacy condition", repair="replace the entry with a concrete owned-subset alignment check")

            if contract_ids and not has_required_contracts and looks_contract_sensitive(pr):
                add_issue(
                    warnings,
                    plan_path,
                    line_map,
                    pr_path,
                    "PR appears contract-sensitive but does not declare required_contracts.",
                    expected="declare required_contracts plus contract_guardrails and contract_done_when",
                    repair="add required_contracts and the matching contract guardrails/done checks for this PR",
                )

            for field in ("files", "expected_changes", "guardrails", "non_goals"):
                value = pr.get(field)
                if not isinstance(value, list):
                    add_issue(errors, plan_path, line_map, pr_path + (field,), f"`{field}` must be a list.", expected="a list", repair=f"rewrite `{field}` as a list of strings")
                    continue

    if not contract_ids and isinstance(prs, list):
        for idx, pr in enumerate(prs):
            if isinstance(pr, dict) and looks_contract_sensitive(pr):
                add_issue(
                    warnings,
                    plan_path,
                    line_map,
                    ("prs", idx),
                    "PR appears contract-sensitive but the plan declares no external_contracts.",
                    expected="declare external_contracts when the phase depends on a public contract source",
                    repair="add external_contracts and wire the PR through required_contracts if this phase consumes an external contract",
                )

    waves = data.get("waves")
    wave_ids: set[int] = set()
    wave_membership: dict[str, int] = {}
    if expect_type(errors, plan_path, line_map, ("waves",), waves, list, "a list"):
        for idx, wave in enumerate(waves):
            wave_path = ("waves", idx)
            if not isinstance(wave, dict):
                add_issue(errors, plan_path, line_map, wave_path, "wave entry must be a mapping.", repair="rewrite the wave entry as a mapping with the required wave fields")
                continue
            missing = sorted(WAVE_REQUIRED - set(wave))
            for key in missing:
                add_issue(errors, plan_path, line_map, wave_path, f"missing required wave field `{key}`.", expected=key, repair=f"add `{key}` to this wave entry")
            wave_id = wave.get("id")
            if not isinstance(wave_id, int):
                add_issue(errors, plan_path, line_map, wave_path + ("id",), "wave id must be an integer.", repair="set waves[].id to a numeric wave id")
                continue
            if wave_id in wave_ids:
                add_issue(errors, plan_path, line_map, wave_path + ("id",), f"duplicate wave id `{wave_id}`.", repair="rename one of the duplicate wave ids so each wave id is unique")
            wave_ids.add(wave_id)

            wave_prs = wave.get("prs")
            wave_pr_set: set[str] = set()
            if expect_type(errors, plan_path, line_map, wave_path + ("prs",), wave_prs, list, "a list"):
                for pr_idx, pr_id in enumerate(wave_prs):
                    if not isinstance(pr_id, str):
                        add_issue(errors, plan_path, line_map, wave_path + ("prs", pr_idx), "wave PR entry must be a PR id string.", repair="replace the wave PR entry with a referenced PR id")
                        continue
                    if pr_id not in pr_ids:
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            wave_path + ("prs", pr_idx),
                            f"unknown PR id `{pr_id}`.",
                            expected=f"one of {sorted(pr_ids)}",
                            repair="change the wave PR entry to an existing PR id or add the missing PR under prs",
                        )
                    if pr_id in wave_membership and wave_membership[pr_id] != wave_id:
                        add_issue(errors, plan_path, line_map, wave_path + ("prs", pr_idx), f"PR `{pr_id}` is already assigned to wave {wave_membership[pr_id]}.", repair="keep each PR in exactly one wave")
                    wave_membership[pr_id] = wave_id
                    wave_pr_set.add(pr_id)

            control_pr = wave.get("control_pr")
            if control_pr not in pr_ids:
                add_issue(
                    errors,
                    plan_path,
                    line_map,
                    wave_path + ("control_pr",),
                    f"unknown control PR `{control_pr}`.",
                    expected=f"one of {sorted(pr_ids)}",
                    repair="set control_pr to an existing PR id in this phase",
                )
            elif control_pr not in wave_pr_set:
                add_issue(errors, plan_path, line_map, wave_path + ("control_pr",), f"control PR `{control_pr}` is not listed in this wave's `prs`.", repair="either add the control PR to waves[].prs or change control_pr to a member of this wave")

            merge_order = wave.get("merge_order")
            merged_prs: list[str] = []
            if expect_type(errors, plan_path, line_map, wave_path + ("merge_order",), merge_order, list, "a list"):
                for batch_idx, batch in enumerate(merge_order):
                    if not isinstance(batch, list):
                        add_issue(errors, plan_path, line_map, wave_path + ("merge_order", batch_idx), "merge_order batch must be a list.", repair="rewrite each merge_order batch as a list of PR ids")
                        continue
                    for pr_idx, pr_id in enumerate(batch):
                        if not isinstance(pr_id, str):
                            add_issue(errors, plan_path, line_map, wave_path + ("merge_order", batch_idx, pr_idx), "merge_order entry must be a PR id string.", repair="replace the merge_order entry with a referenced PR id")
                            continue
                        merged_prs.append(pr_id)
                        if pr_id not in wave_pr_set:
                            add_issue(
                                errors,
                                plan_path,
                                line_map,
                                wave_path + ("merge_order", batch_idx, pr_idx),
                                f"merge_order references PR `{pr_id}` not present in this wave.",
                                expected=f"one of {sorted(wave_pr_set)}",
                                repair="keep merge_order aligned with waves[].prs for the same wave",
                            )
                if wave_pr_set and set(merged_prs) != wave_pr_set:
                    missing = sorted(wave_pr_set - set(merged_prs))
                    extra = sorted(set(merged_prs) - wave_pr_set)
                    detail = []
                    if missing:
                        detail.append(f"missing {missing}")
                    if extra:
                        detail.append(f"extra {extra}")
                    add_issue(errors, plan_path, line_map, wave_path + ("merge_order",), f"merge_order does not cover the same PR set as waves[].prs ({'; '.join(detail)}).", repair="make merge_order contain exactly the same PR ids as waves[].prs")

            roles = wave.get("roles", [])
            role_ids: set[str] = set()
            if roles is not None and not isinstance(roles, list):
                add_issue(errors, plan_path, line_map, wave_path + ("roles",), "roles must be a list when present.", repair="rewrite roles as a list of role mappings")
                roles = []
            for role_idx, role in enumerate(roles):
                role_path = wave_path + ("roles", role_idx)
                if not isinstance(role, dict):
                    add_issue(errors, plan_path, line_map, role_path, "role entry must be a mapping.", repair="rewrite the role entry as a mapping with id, owner, kind, scope, validation, and done_when")
                    continue
                role_id = role.get("id")
                if not isinstance(role_id, str) or not role_id:
                    add_issue(errors, plan_path, line_map, role_path + ("id",), "role id must be a non-empty string.", repair="set roles[].id to a stable non-empty string")
                elif role_id in role_ids:
                    add_issue(errors, plan_path, line_map, role_path + ("id",), f"duplicate role id `{role_id}` within the wave.", repair="rename one of the duplicate role ids within this wave")
                else:
                    role_ids.add(role_id)
                owner = role.get("owner")
                if owner not in team_ids:
                    add_issue(
                        errors,
                        plan_path,
                        line_map,
                        role_path + ("owner",),
                        f"unknown role owner `{owner}`.",
                        expected=f"one of {sorted(team_ids)}",
                        repair="change the role owner to a declared team[].id or add the missing team entry",
                    )
                for field in ("goal", "start_condition", "guardrails", "validation", "done_when"):
                    if field not in role:
                        add_issue(errors, plan_path, line_map, role_path, f"missing role field `{field}`.", expected=field, repair=f"add `{field}` to this role entry")
                start_condition = role.get("start_condition")
                if expect_type(errors, plan_path, line_map, role_path + ("start_condition",), start_condition, dict, "a mapping"):
                    gate = start_condition.get("gate")
                    refs = start_condition.get("refs")
                    if gate not in START_GATE_VALUES:
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            role_path + ("start_condition", "gate"),
                            f"invalid start gate `{gate}`.",
                            expected=f"one of {sorted(START_GATE_VALUES)}",
                            repair="set start_condition.gate to immediate, after_prs, or after_waves",
                        )
                    if not isinstance(refs, list):
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            role_path + ("start_condition", "refs"),
                            "start_condition.refs must be a list.",
                            expected="a list",
                            repair="rewrite start_condition.refs as an ordered list of PR ids or wave ids",
                        )
                    elif gate == "immediate" and refs:
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            role_path + ("start_condition", "refs"),
                            "immediate start_condition must use an empty refs list.",
                            expected="[]",
                            repair="clear start_condition.refs when gate is immediate",
                        )
                    elif gate == "after_prs":
                        for ref_idx, ref in enumerate(refs):
                            if ref not in pr_ids:
                                add_issue(
                                    errors,
                                    plan_path,
                                    line_map,
                                    role_path + ("start_condition", "refs", ref_idx),
                                    f"unknown PR gate `{ref}`.",
                                    expected=f"one of {sorted(pr_ids)}",
                                    repair="replace the gate ref with an existing PR id",
                                )
                    elif gate == "after_waves":
                        for ref_idx, ref in enumerate(refs):
                            if not isinstance(ref, int):
                                add_issue(
                                    errors,
                                    plan_path,
                                    line_map,
                                    role_path + ("start_condition", "refs", ref_idx),
                                    "wave gate ref must be an integer wave id.",
                                    expected="an integer wave id",
                                    repair="replace the gate ref with a numeric wave id",
                                )
                if "read_first" in role:
                    validate_read_first_entries(errors, plan_path, line_map, role_path + ("read_first",), role.get("read_first"), phase_name, allowed_phase_docs)
                validate_validation_entries(errors, plan_path, line_map, role_path + ("validation",), role.get("validation"), profile_ids, declared_tokens)
                scope = role.get("scope")
                if scope is not None:
                    if expect_type(errors, plan_path, line_map, role_path + ("scope",), scope, dict, "a mapping"):
                        for field in ("allow", "deny"):
                            if field not in scope:
                                add_issue(errors, plan_path, line_map, role_path + ("scope",), f"scope is missing `{field}`.", expected=field, repair=f"add scope.{field} as a list")
                            elif not isinstance(scope[field], list):
                                add_issue(errors, plan_path, line_map, role_path + ("scope", field), f"scope.{field} must be a list.", repair=f"rewrite scope.{field} as a list of strings")
                done_when = role.get("done_when")
                if not isinstance(done_when, list):
                    add_issue(errors, plan_path, line_map, role_path + ("done_when",), "done_when must be a list.", expected="a list", repair="rewrite done_when as a list of concrete completion checks")
                elif not done_when:
                    add_issue(errors, plan_path, line_map, role_path + ("done_when",), "done_when must not be empty.", repair="add at least one concrete completion check")
                else:
                    for done_idx, entry in enumerate(done_when):
                        if not isinstance(entry, str) or not entry.strip():
                            add_issue(errors, plan_path, line_map, role_path + ("done_when", done_idx), "done_when entry must be a non-empty string.", repair="replace the done_when entry with a concrete completion check")

            lane_setup = wave.get("lane_setup")
            if expect_type(errors, plan_path, line_map, wave_path + ("lane_setup",), lane_setup, list, "a list"):
                for lane_idx, lane in enumerate(lane_setup):
                    lane_path = wave_path + ("lane_setup", lane_idx)
                    if not isinstance(lane, dict):
                        add_issue(errors, plan_path, line_map, lane_path, "lane entry must be a mapping.", repair="rewrite the lane entry as a mapping with lane, owner, ref_kind, and ref")
                        continue
                    owner = lane.get("owner")
                    if owner not in team_ids:
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            lane_path + ("owner",),
                            f"unknown lane owner `{owner}`.",
                            expected=f"one of {sorted(team_ids)}",
                            repair="change the lane owner to a declared team[].id or add the missing team entry",
                        )
                    ref_kind = lane.get("ref_kind")
                    ref = lane.get("ref")
                    if ref_kind not in {"pr", "role"}:
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            lane_path + ("ref_kind",),
                            f"invalid ref_kind `{ref_kind}`.",
                            expected="one of ['pr', 'role']",
                            repair="set ref_kind to `pr` or `role` and align ref accordingly",
                        )
                    elif ref_kind == "pr" and ref not in wave_pr_set:
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            lane_path + ("ref",),
                            f"lane ref `{ref}` is not a PR in this wave.",
                            expected=f"one of {sorted(wave_pr_set)}",
                            repair="change the lane ref to a PR id listed in this wave",
                        )
                    elif ref_kind == "role" and ref not in role_ids:
                        add_issue(
                            errors,
                            plan_path,
                            line_map,
                            lane_path + ("ref",),
                            f"lane ref `{ref}` is not a role in this wave.",
                            expected=f"one of {sorted(role_ids)}",
                            repair="change the lane ref to a role id declared in this wave",
                        )

    for idx, pr in enumerate(prs or []):
        if not isinstance(pr, dict):
            continue
        pr_id = pr.get("id")
        if not isinstance(pr_id, str) or pr_id not in pr_ids:
            continue
        pr_path = ("prs", idx)
        done_when = pr.get("done_when")
        if not isinstance(done_when, list):
            add_issue(errors, plan_path, line_map, pr_path + ("done_when",), "done_when must be a list.", expected="a list", repair="rewrite done_when as a list of concrete completion checks")
        elif not done_when:
            add_issue(errors, plan_path, line_map, pr_path + ("done_when",), "done_when must not be empty.", repair="add at least one concrete completion check")
        else:
            for done_idx, entry in enumerate(done_when):
                if not isinstance(entry, str) or not entry.strip():
                    add_issue(errors, plan_path, line_map, pr_path + ("done_when", done_idx), "done_when entry must be a non-empty string.", repair="replace the done_when entry with a concrete completion check")
                else:
                    lowered = entry.lower()
                    for invalid_phrase in INVALID_CONTRACT_COMPLETION_PATTERNS:
                        if invalid_phrase in lowered:
                            add_issue(errors, plan_path, line_map, pr_path + ("done_when", done_idx), f"invalid completion phrase `{invalid_phrase}` is not allowed.", expected="a concrete completion check, not a fallback or legacy condition", repair="replace the entry with a concrete repo-local or contract alignment outcome")
        for dep_idx, dep in enumerate(pr.get("depends_on", [])):
            if isinstance(dep, str) and dep not in pr_ids:
                add_issue(
                    errors,
                    plan_path,
                    line_map,
                    pr_path + ("depends_on", dep_idx),
                    f"unknown dependency `{dep}`.",
                    expected=f"one of {sorted(pr_ids)}",
                    repair="change the dependency to an existing PR id or add the missing PR",
                )
        declared_wave = pr.get("wave")
        listed_wave = wave_membership.get(pr_id)
        if listed_wave is None:
            add_issue(errors, plan_path, line_map, pr_path + ("wave",), f"PR `{pr_id}` is not listed in any wave.", repair="add the PR id to exactly one wave under waves[].prs and merge_order")
        elif declared_wave != listed_wave:
            add_issue(
                errors,
                plan_path,
                line_map,
                pr_path + ("wave",),
                f"PR declares wave {declared_wave} but is listed under wave {listed_wave}.",
                expected=f"wave {listed_wave}",
                repair="make prs[].wave match the wave that lists this PR",
            )

    if not errors and not warnings:
        return [], []
    return errors, warnings


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    errors, warnings = validate_schema(plan_path)

    if errors:
        print("Schema validation failed:")
        for issue in errors:
            print(issue.render("ERROR"))
        for issue in warnings:
            print(issue.render("WARN"))
        return 1

    print("Schema validation passed.")
    for issue in warnings:
        print(issue.render("WARN"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
