#!/usr/bin/env python3
"""Measure the portable Agent Skills prompt surface and theoretical upper bound."""

from __future__ import annotations

import argparse
import json
import re
import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

import yaml

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
REPOSITORY_GOVERNANCE = REPO_ROOT / "AGENTS.md"
TOKEN_ENCODING = "o200k_base"
TOKEN_COUNTER = "tiktoken"
COUNTER_VERSION = "0.13.0"
MEASUREMENT_CONTRACT_VERSION = "1.0"
ACTIVATION_CONTRACT_PATH = REPO_ROOT / "maintainer" / "data" / "token_activation_contract.json"
CATALOG_PATH = REPO_ROOT / "maintainer" / "data" / "skill_catalog.json"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
MARKDOWN_CODE_PATH = re.compile(r"`((?:references/)?[^`\s]+\.md)`")
LOAD_MODES = frozenset({"always", "conditional", "optional-runtime", "authoring-only"})


class ContractError(RuntimeError):
    """The measurement contract is missing, invalid, or cannot be evaluated."""


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def measurement_identity() -> dict[str, str]:
    return {
        "measurement_contract_version": MEASUREMENT_CONTRACT_VERSION,
        "token_counter": TOKEN_COUNTER,
        "counter_version": COUNTER_VERSION,
        "tokenizer": TOKEN_ENCODING,
    }


def verify_counter_runtime() -> None:
    try:
        installed = package_version(TOKEN_COUNTER)
    except PackageNotFoundError as exc:
        raise ContractError(f"{TOKEN_COUNTER} is not installed") from exc
    if installed != COUNTER_VERSION:
        raise ContractError(
            f"{TOKEN_COUNTER} version mismatch: expected {COUNTER_VERSION}, got {installed}"
        )


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read {_display_path(path)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{_display_path(path)} must contain a JSON object")
    return value


def load_activation_contract(path: Path = ACTIVATION_CONTRACT_PATH) -> dict[str, Any]:
    contract = load_json_object(path)
    identity = measurement_identity()
    mismatches = [
        f"{key}: expected {expected!r}, got {contract.get(key)!r}"
        for key, expected in identity.items()
        if contract.get(key) != expected
    ]
    if mismatches:
        raise ContractError("token activation identity mismatch: " + "; ".join(mismatches))
    return contract


def count_tokens(text: str) -> int:
    """Count exact tokens with o200k_base."""

    if not TIKTOKEN_AVAILABLE:
        raise RuntimeError("tiktoken is required for --actual-tokens")
    try:
        return len(tiktoken.get_encoding(TOKEN_ENCODING).encode(text))
    except Exception as exc:
        raise RuntimeError(f"failed to count tokens with {TOKEN_ENCODING}: {exc}") from exc


def count_file_tokens(path: Path) -> int:
    try:
        return count_tokens(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot measure UTF-8 file {_display_path(path)}: {exc}") from exc


def text_metrics(text: str, *, actual_tokens: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "lines": len(text.splitlines()),
        "chars": len(text),
        "bytes": len(text.encode("utf-8")),
    }
    if actual_tokens:
        result["tokens"] = count_tokens(text)
        result["tokens_estimate"] = len(text) // 4
    return result


def file_metrics(path: Path, *, actual_tokens: bool) -> dict[str, Any]:
    if not path.is_file():
        result: dict[str, Any] = {
            "path": str(path),
            "exists": False,
            "lines": 0,
            "chars": 0,
            "bytes": 0,
        }
        if actual_tokens:
            result.update(tokens=0, tokens_estimate=0)
        return result

    result = {
        "path": _display_path(path),
        "exists": True,
        **text_metrics(path.read_text(encoding="utf-8"), actual_tokens=actual_tokens),
    }
    return result


def split_skill(content: str) -> tuple[dict[str, Any], str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, content
    frontmatter = yaml.safe_load("\n".join(lines[1:end])) or {}
    return frontmatter if isinstance(frontmatter, dict) else {}, "\n".join(lines[end + 1 :])


def read_supporting_text_files(skill_dir: Path) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.name == "SKILL.md" or any(part.startswith(".") for part in path.relative_to(skill_dir).parts):
            continue
        try:
            files.append((path, path.read_text(encoding="utf-8")))
        except (UnicodeDecodeError, OSError):
            continue
    return files


def _catalog_skill_sets() -> tuple[list[str], list[str]]:
    catalog = load_json_object(CATALOG_PATH)
    core = catalog.get("core_skill_names")
    optional = catalog.get("optional_skill_names")
    if (
        not isinstance(core, list)
        or not isinstance(optional, list)
        or any(not isinstance(item, str) for item in [*core, *optional])
    ):
        raise ContractError("skill_catalog.json has invalid core/optional Skill arrays")
    return core, optional


def _normalize_package_path(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError("reference path must be a non-empty string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != value:
        raise ContractError(f"reference path must be normalized and package-relative: {value!r}")
    return value


def _load_reference_manifest(skill_dir: Path, contract: dict[str, Any]) -> list[dict[str, str]]:
    manifest_contract = contract.get("reference_manifest")
    if not isinstance(manifest_contract, dict):
        raise ContractError("reference_manifest contract must be an object")
    manifest_relative = _normalize_package_path(manifest_contract.get("path"))
    manifest_path = skill_dir / manifest_relative
    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"missing reference manifest: {_display_path(manifest_path)}") from exc
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError(f"invalid reference manifest {_display_path(manifest_path)}: {exc}") from exc
    if not isinstance(raw, dict) or set(raw) != {"schema_version", "references"}:
        raise ContractError(f"{_display_path(manifest_path)} must contain only schema_version and references")
    if raw.get("schema_version") != manifest_contract.get("schema_version"):
        raise ContractError(f"{_display_path(manifest_path)} schema_version mismatch")
    items = raw.get("references")
    if not isinstance(items, list):
        raise ContractError(f"{_display_path(manifest_path)} items must be an array")
    normalized: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    seen_conditions: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != {"path", "load_mode", "condition_id"}:
            raise ContractError(
                f"{_display_path(manifest_path)} items[{index}] must contain only path, load_mode, condition_id"
            )
        path = _normalize_package_path(item.get("path"))
        load_mode = item.get("load_mode")
        condition_id = item.get("condition_id")
        if load_mode not in LOAD_MODES:
            raise ContractError(f"unsupported load_mode {load_mode!r} in {_display_path(manifest_path)}")
        if not isinstance(condition_id, str) or not condition_id:
            raise ContractError(f"condition_id must be a non-empty string in {_display_path(manifest_path)}")
        if path in seen_paths:
            raise ContractError(f"duplicate manifest path {path!r} in {_display_path(manifest_path)}")
        if condition_id in seen_conditions:
            raise ContractError(f"duplicate condition_id {condition_id!r} in {_display_path(manifest_path)}")
        target = skill_dir / path
        if not target.is_file():
            raise ContractError(f"manifest target does not exist: {_display_path(target)}")
        try:
            target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ContractError(f"manifest target is not readable UTF-8: {_display_path(target)}: {exc}") from exc
        normalized.append({"path": path, "load_mode": load_mode, "condition_id": condition_id})
        seen_paths.add(path)
        seen_conditions.add(condition_id)
    return normalized


def _local_markdown_targets(skill_dir: Path, source: Path) -> set[str]:
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot read Markdown link source {_display_path(source)}: {exc}") from exc
    targets: set[str] = set()
    for match in MARKDOWN_LINK.finditer(text):
        raw = match.group(1).split("#", 1)[0]
        if not raw or "://" in raw or raw.startswith(("#", "/")):
            continue
        candidate = (source.parent / raw).resolve()
        try:
            relative = candidate.relative_to(skill_dir.resolve())
        except ValueError as exc:
            raise ContractError(
                f"Markdown link escapes Skill package: {_display_path(source)} -> {raw}"
            ) from exc
        if candidate.suffix.lower() == ".md" and candidate.is_file():
            targets.add(relative.as_posix())
    for match in MARKDOWN_CODE_PATH.finditer(text):
        raw = match.group(1)
        candidate = (
            skill_dir / raw
            if raw.startswith("references/")
            else source.parent / raw
        ).resolve()
        try:
            relative = candidate.relative_to(skill_dir.resolve())
        except ValueError as exc:
            raise ContractError(
                f"Markdown path escapes Skill package: {_display_path(source)} -> {raw}"
            ) from exc
        if candidate.is_file():
            targets.add(relative.as_posix())
    return targets


def _reachable_markdown(skill_dir: Path) -> set[str]:
    pending = ["SKILL.md"]
    visited: set[str] = set()
    reachable: set[str] = set()
    while pending:
        relative = pending.pop()
        if relative in visited:
            continue
        visited.add(relative)
        for target in _local_markdown_targets(skill_dir, skill_dir / relative):
            reachable.add(target)
            if target not in visited:
                pending.append(target)
    return reachable


def _validate_reference_contract(
    skill_name: str,
    skill_dir: Path,
    actual: list[dict[str, str]],
    expected: object,
) -> list[str]:
    issues: list[str] = []
    if not isinstance(expected, list) or any(not isinstance(item, dict) for item in expected):
        return [f"reference_contracts.{skill_name} must be an array of objects"]
    if actual != expected:
        issues.append(f"{skill_name}: reference manifest differs from token_activation_contract.json")
    by_path = {item["path"]: item for item in actual}
    manifest_relative = "references/manifest.yaml"
    supporting_paths = {
        path.relative_to(skill_dir).as_posix()
        for path, _text in read_supporting_text_files(skill_dir)
        if path.relative_to(skill_dir).as_posix() != manifest_relative
    }
    if supporting_paths != set(by_path):
        issues.append(
            f"{skill_name}: manifest paths differ from package supporting text: "
            f"missing={sorted(supporting_paths - set(by_path))}, "
            f"extra={sorted(set(by_path) - supporting_paths)}"
        )
    reachable = _reachable_markdown(skill_dir)
    runtime_paths = {
        path for path, item in by_path.items() if item["load_mode"] != "authoring-only"
    }
    authoring_paths = {
        path for path, item in by_path.items() if item["load_mode"] == "authoring-only"
    }
    for path in sorted(reachable - runtime_paths):
        if path in authoring_paths:
            issues.append(f"{skill_name}: authoring-only reference is runtime-reachable: {path}")
        else:
            issues.append(f"{skill_name}: runtime Markdown link is absent from manifest: {path}")
    for path in sorted(runtime_paths - reachable):
        issues.append(f"{skill_name}: runtime manifest reference is not reachable from SKILL.md: {path}")
    return issues


def measure_activation_contract(
    skills_dir: Path = SKILLS_DIR,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_activation_contract()
    core, optional = _catalog_skill_sets()
    active = [*core, *optional]
    reference_contracts = contract.get("reference_contracts")
    scenarios = contract.get("scenarios")
    budgets = contract.get("budgets")
    file_budgets = contract.get("skill_file_budgets")
    if not isinstance(reference_contracts, dict) or not isinstance(scenarios, list):
        raise ContractError("activation contract requires reference_contracts and scenarios")
    if not isinstance(budgets, dict) or not isinstance(file_budgets, dict):
        raise ContractError("activation contract requires budgets and skill_file_budgets")

    issues: list[str] = []
    manifests: dict[str, list[dict[str, str]]] = {}
    file_tokens: dict[str, dict[str, int]] = {}
    for skill_name in active:
        skill_file = skills_dir / skill_name / "SKILL.md"
        if skill_file.is_file():
            file_tokens[skill_name] = {"SKILL.md": count_file_tokens(skill_file)}
        else:
            issues.append(f"missing cataloged Skill main file: {skill_file.relative_to(REPO_ROOT) if skill_file.is_relative_to(REPO_ROOT) else skill_file}")
    for skill_name, expected in reference_contracts.items():
        if skill_name not in active:
            issues.append(f"reference_contracts contains non-catalog Skill: {skill_name}")
            continue
        skill_dir = skills_dir / skill_name
        try:
            actual = _load_reference_manifest(skill_dir, contract)
            issues.extend(_validate_reference_contract(skill_name, skill_dir, actual, expected))
        except ContractError as exc:
            issues.append(str(exc))
            continue
        manifests[skill_name] = actual
        file_tokens[skill_name] = {
            **file_tokens.get(skill_name, {}),
            **{item["path"]: count_file_tokens(skill_dir / item["path"]) for item in actual},
        }

    scenario_results: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    covered_runtime: dict[str, set[str]] = {skill: set() for skill in active}
    max_runtime_skills: set[str] = set()
    release = budgets.get("release") if isinstance(budgets, dict) else None
    if not isinstance(release, dict):
        raise ContractError("budgets.release must be an object")
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            issues.append(f"scenarios[{index}] must be an object")
            continue
        allowed_fields = {"id", "skill", "class", "references", "max_runtime"}
        if not set(scenario) <= allowed_fields:
            issues.append(f"scenarios[{index}] has unsupported fields")
        scenario_id = scenario.get("id")
        skill_name = scenario.get("skill")
        scenario_class = scenario.get("class")
        references = scenario.get("references")
        if not isinstance(scenario_id, str) or not scenario_id:
            issues.append(f"scenarios[{index}].id must be non-empty")
            continue
        if scenario_id in seen_ids:
            issues.append(f"duplicate token scenario id: {scenario_id}")
        seen_ids.add(scenario_id)
        if skill_name not in active or scenario_class not in {"typical", "heavy"}:
            issues.append(f"{scenario_id}: invalid skill or class")
            continue
        if not isinstance(references, list) or any(not isinstance(item, str) for item in references):
            issues.append(f"{scenario_id}: references must be an array of strings")
            continue
        manifest = manifests.get(skill_name, [])
        tokens = file_tokens.get(skill_name)
        if tokens is None:
            issues.append(f"{scenario_id}: Skill main file could not be measured")
            continue
        by_path = {item["path"]: item for item in manifest}
        always = {path for path, item in by_path.items() if item["load_mode"] == "always"}
        selected = set(references)
        if len(selected) != len(references):
            issues.append(f"{scenario_id}: references contain duplicates")
        unknown = selected - set(by_path)
        if unknown:
            issues.append(f"{scenario_id}: references absent from manifest: {sorted(unknown)}")
        authoring = {path for path in selected if by_path.get(path, {}).get("load_mode") == "authoring-only"}
        if authoring:
            issues.append(f"{scenario_id}: authoring-only references cannot enter runtime scenarios: {sorted(authoring)}")
        loaded = always | selected
        covered_runtime[skill_name].update(loaded)
        token_total = sum(tokens[path] for path in {"SKILL.md", *loaded} if path in tokens)
        budget_name = "typical_activation" if scenario_class == "typical" else "heavy_activation"
        budget = release.get(budget_name)
        if isinstance(budget, int) and token_total > budget:
            issues.append(f"{scenario_id}: {token_total} tokens exceeds {budget_name} budget {budget}")
        skill_limits = file_budgets.get(skill_name)
        if isinstance(skill_limits, dict):
            if scenario_class == "typical":
                typical_limit = skill_limits.get("typical_activation_max")
                if isinstance(typical_limit, int) and token_total > typical_limit:
                    issues.append(f"{scenario_id}: {token_total} tokens exceeds Skill typical limit {typical_limit}")
                single_limit = skill_limits.get("single_object_activation_max")
                if isinstance(single_limit, int) and token_total > single_limit:
                    issues.append(f"{scenario_id}: {token_total} tokens exceeds single-object limit {single_limit}")
            if scenario_id == "token-artifact-review-mixed-heavy":
                mixed_limit = skill_limits.get("mixed_activation_max")
                if isinstance(mixed_limit, int) and token_total > mixed_limit:
                    issues.append(f"{scenario_id}: {token_total} tokens exceeds mixed-object limit {mixed_limit}")
        if scenario.get("max_runtime") is True:
            expected_max = {
                path for path, item in by_path.items() if item["load_mode"] != "authoring-only"
            }
            if loaded != expected_max:
                issues.append(f"{scenario_id}: max_runtime must load every runtime reference exactly once")
            max_runtime_skills.add(skill_name)
        scenario_results.append({
            "id": scenario_id,
            "skill": skill_name,
            "class": scenario_class,
            "loaded_files": ["SKILL.md", *sorted(loaded)],
            "tokens": token_total,
        })

    for skill_name, manifest in manifests.items():
        runtime = {item["path"] for item in manifest if item["load_mode"] != "authoring-only"}
        missing = runtime - covered_runtime.get(skill_name, set())
        if missing:
            issues.append(f"{skill_name}: runtime references lack scenario coverage: {sorted(missing)}")
    expected_max_skills = set(file_budgets)
    if max_runtime_skills != expected_max_skills:
        issues.append(
            f"max_runtime scenarios differ from five budgeted Skills: "
            f"missing={sorted(expected_max_skills - max_runtime_skills)}, extra={sorted(max_runtime_skills - expected_max_skills)}"
        )

    for skill_name, limits in file_budgets.items():
        if not isinstance(limits, dict) or skill_name not in file_tokens:
            continue
        measured = file_tokens[skill_name]
        main = measured["SKILL.md"]
        if isinstance(limits.get("main_min"), int) and main < limits["main_min"]:
            issues.append(f"{skill_name}: main file {main} is below locked minimum {limits['main_min']}")
        if isinstance(limits.get("main_max"), int) and main > limits["main_max"]:
            issues.append(f"{skill_name}: main file {main} exceeds locked maximum {limits['main_max']}")
        for path, limit in limits.items():
            if path.startswith("references/") and isinstance(limit, int):
                actual = measured.get(path)
                if actual is None or actual > limit:
                    issues.append(f"{skill_name}: {path} tokens {actual!r} exceed file budget {limit}")
        runtime_paths = {
            item["path"] for item in manifests.get(skill_name, []) if item["load_mode"] != "authoring-only"
        }
        runtime_reference_total = sum(measured[path] for path in runtime_paths)
        runtime_reference_limit = limits.get("runtime_references_total_max")
        if isinstance(runtime_reference_limit, int) and runtime_reference_total > runtime_reference_limit:
            issues.append(
                f"{skill_name}: runtime references total {runtime_reference_total} exceeds {runtime_reference_limit}"
            )
        worst = sum(measured[path] for path in {"SKILL.md", *runtime_paths})
        worst_limit = limits.get("worst_runtime_max")
        if isinstance(worst_limit, int) and worst > worst_limit:
            issues.append(f"{skill_name}: worst runtime {worst} exceeds Skill limit {worst_limit}")
        if isinstance(release.get("worst_runtime_activation"), int) and worst > release["worst_runtime_activation"]:
            issues.append(f"{skill_name}: worst runtime {worst} exceeds global worst-runtime budget")

    return {
        **measurement_identity(),
        "scenarios": scenario_results,
        "max_typical_tokens": max((item["tokens"] for item in scenario_results if item["class"] == "typical"), default=0),
        "max_heavy_tokens": max((item["tokens"] for item in scenario_results if item["class"] == "heavy"), default=0),
        "validation_issues": issues,
    }


def measure_skills(*, actual_tokens: bool) -> dict[str, Any]:
    skills: list[dict[str, Any]] = []
    metadata_total = ""
    supporting_total = ""

    for skill_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue

        content = skill_file.read_text(encoding="utf-8")
        frontmatter, body = split_skill(content)
        metadata_text = (
            f"name: {frontmatter.get('name', '')}\n"
            f"description: {frontmatter.get('description', '')}\n"
        )
        supporting = read_supporting_text_files(skill_dir)
        supporting_text = "\n".join(text for _path, text in supporting)
        supporting_metrics = text_metrics(supporting_text, actual_tokens=actual_tokens)
        if actual_tokens:
            supporting_metrics["tokens"] = sum(count_tokens(text) for _path, text in supporting)

        metrics = file_metrics(skill_file, actual_tokens=actual_tokens)
        metrics.update(
            skill_name=skill_dir.name,
            body_lines=len(body.splitlines()),
            body_chars=len(body),
            over_500_lines=len(body.splitlines()) > 500,
            discovery_metadata=text_metrics(metadata_text, actual_tokens=actual_tokens),
            supporting_files_count=len(supporting),
            supporting_files=[str(path.relative_to(REPO_ROOT)) for path, _text in supporting],
            supporting_metrics=supporting_metrics,
        )
        if actual_tokens:
            metrics["body_tokens"] = count_tokens(body)
            metrics["package_tokens_upper_bound"] = metrics["tokens"] + metrics["supporting_metrics"]["tokens"]

        skills.append(metrics)
        metadata_total += metadata_text
        supporting_total += supporting_text

    supporting_aggregate = text_metrics(supporting_total, actual_tokens=actual_tokens)
    if actual_tokens:
        supporting_aggregate["tokens"] = sum(
            skill["supporting_metrics"]["tokens"] for skill in skills
        )
    result: dict[str, Any] = {
        "skills": skills,
        "count": len(skills),
        "total_lines": sum(skill["lines"] for skill in skills),
        "total_chars": sum(skill["chars"] for skill in skills),
        "total_bytes": sum(skill["bytes"] for skill in skills),
        "avg_lines_per_skill": (sum(skill["lines"] for skill in skills) / len(skills)) if skills else 0,
        "max_body_lines": max((skill["body_lines"] for skill in skills), default=0),
        "over_500_count": sum(skill["over_500_lines"] for skill in skills),
        "discovery_metadata": text_metrics(metadata_total, actual_tokens=actual_tokens),
        "supporting_files": {
            "count": sum(skill["supporting_files_count"] for skill in skills),
            **supporting_aggregate,
        },
    }
    if actual_tokens:
        result["total_tokens"] = sum(skill["tokens"] for skill in skills)
        result["total_tokens_estimate"] = sum(skill["tokens_estimate"] for skill in skills)
        result["avg_tokens_per_skill"] = result["total_tokens"] / len(skills) if skills else 0
        result["all_packages_tokens_upper_bound"] = (
            result["total_tokens"] + result["supporting_files"]["tokens"]
        )
    return result


def validate_global_budgets(results: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    budgets = contract.get("budgets")
    if not isinstance(budgets, dict) or not isinstance(budgets.get("release"), dict):
        raise ContractError("budgets.release must be an object")
    release = budgets["release"]
    engineering = budgets.get("engineering")
    if not isinstance(engineering, dict):
        raise ContractError("budgets.engineering must be an object")
    skills = results["skill_files"]
    governance = results["repository_governance"]
    core, optional = _catalog_skill_sets()
    by_name = {item["skill_name"]: item for item in skills["skills"]}
    active = set(core) | set(optional)
    if set(by_name) != active:
        issues.append(
            f"measured Skill set differs from catalog: missing={sorted(active - set(by_name))}, "
            f"extra={sorted(set(by_name) - active)}"
        )
    core_discovery = sum(
        by_name[name]["discovery_metadata"]["tokens"] for name in core if name in by_name
    )
    artifact_metadata = by_name.get("artifact-review-loop", {}).get("discovery_metadata", {}).get("tokens", 0)
    surfaces = {
        "full_discovery_metadata": skills["discovery_metadata"]["tokens"],
        "core_discovery_metadata": core_discovery,
        "artifact_review_metadata": artifact_metadata,
        "all_skill_main": skills["total_tokens"],
        "all_package_text": skills["all_packages_tokens_upper_bound"],
        "repository_governance": governance["tokens"],
    }
    for tier_name, tier in (("release", release), ("engineering", engineering)):
        for surface, limit in tier.items():
            if surface not in surfaces or not isinstance(limit, int):
                continue
            if surfaces[surface] > limit:
                issues.append(
                    f"{surface}: {surfaces[surface]} exceeds {tier_name} budget {limit}"
                )
    results["budget_surfaces"] = surfaces
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--actual-tokens", action="store_true")
    parser.add_argument(
        "--validate-activation-contract",
        action="store_true",
        help="Measure mandatory activation scenarios and fail on contract or budget drift",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=ACTIVATION_CONTRACT_PATH,
        help="Token activation contract JSON path",
    )
    parser.add_argument(
        "--fail-on-budget",
        action="store_true",
        help="Return exit 1 when a measured budget or activation contract is violated",
    )
    args = parser.parse_args()

    if args.validate_activation_contract:
        args.actual_tokens = True
    if args.fail_on_budget:
        args.validate_activation_contract = True
        args.actual_tokens = True
    if args.actual_tokens and not TIKTOKEN_AVAILABLE:
        print("OPERATIONAL ERROR: --actual-tokens requires tiktoken", file=sys.stderr)
        return 2

    try:
        contract = load_activation_contract(args.contract) if args.actual_tokens else None
        if args.actual_tokens:
            verify_counter_runtime()
    except ContractError as exc:
        print(f"OPERATIONAL ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        skills = measure_skills(actual_tokens=args.actual_tokens)
        governance = file_metrics(REPOSITORY_GOVERNANCE, actual_tokens=args.actual_tokens)
    except (ContractError, RuntimeError, OSError, UnicodeDecodeError) as exc:
        print(f"OPERATIONAL ERROR: {exc}", file=sys.stderr)
        return 2
    results = {
        **(measurement_identity() if args.actual_tokens else {}),
        "token_counting_method": TOKEN_ENCODING if args.actual_tokens and TIKTOKEN_AVAILABLE else "character_estimate",
        "scope_note": "Discovery metadata is normally visible first; SKILL.md and supporting files are loaded progressively. Full-package totals are theoretical upper bounds.",
        "skill_files": skills,
        "repository_governance": {
            **governance,
            "distribution_boundary": "internal repository governance; not part of Agent Skills packages",
        },
    }
    validation_issues: list[str] = []
    if args.validate_activation_contract and contract is not None:
        try:
            validation_issues.extend(validate_global_budgets(results, contract))
            activation = measure_activation_contract(contract=contract)
            results["activation_contract"] = activation
            validation_issues.extend(activation["validation_issues"])
        except ContractError as exc:
            print(f"OPERATIONAL ERROR: {exc}", file=sys.stderr)
            return 2
    results["validation_issues"] = validation_issues

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 1 if validation_issues and args.fail_on_budget else 0

    print("Agent Skills Prompt Surface")
    print(f"Token counting: {results['token_counting_method']}")
    print(f"Packages: {skills['count']}")
    if args.actual_tokens:
        print(f"Discovery metadata (all packages): {skills['discovery_metadata']['tokens']} tokens")
        print(f"All SKILL.md files: {skills['total_tokens']} tokens")
        print(f"All supporting text files: {skills['supporting_files']['tokens']} tokens")
        print(f"Theoretical all-package upper bound: {skills['all_packages_tokens_upper_bound']} tokens")
        print(f"Repository-only AGENTS.md: {governance['tokens']} tokens")
    else:
        print(f"All SKILL.md files: {skills['total_chars']} characters")
        print(f"All supporting text files: {skills['supporting_files']['chars']} characters")
    print("Largest activated SKILL.md bodies:")
    for skill in sorted(skills["skills"], key=lambda item: item.get("body_tokens", item["body_chars"]), reverse=True)[:10]:
        size = f"{skill['body_tokens']} tokens" if args.actual_tokens else f"{skill['body_chars']} chars"
        print(f"  {skill['skill_name']}: {size}; {skill['supporting_files_count']} supporting files")
    print(results["scope_note"])
    for issue in validation_issues:
        print(f"ERROR: {issue}")
    return 1 if validation_issues and args.fail_on_budget else 0


if __name__ == "__main__":
    raise SystemExit(main())
