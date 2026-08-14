#!/usr/bin/env python3
"""Validate the 12-package catalog and reject active retired-Skill references."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = Path("maintainer/data/skill_catalog.json")
MIGRATION_PATH = Path("maintainer/data/review_skill_migration_matrix.json")
GOVERNED_ROOTS = (".github", "docs", "examples", "maintainer", "scripts", "skills", "templates")
GOVERNED_TOP_LEVEL_FILES = (
    ".env.example",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CHANGELOG-trigger-optimization.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "phase-toolchain-optimization-zh.md",
)
ALLOWED_SCOPES = frozenset({
    "catalog-field:retired_skill_names",
    "catalog-field:approved_retired_index_deletions",
    "migration-field:legacy_skill",
    "migration-field:retired_skill_names",
    "migration-field:approved_retired_index_deletions",
    "python-field:id",
    "historical-file",
})
PYTHON_ID_EXCEPTION_PATHS = frozenset({
    "maintainer/data/trigger_test_data.py",
    "maintainer/data/artifact_review_test_data.py",
    "maintainer/data/skill_test_data.py",
})
HISTORICAL_EXCEPTION_PATHS = frozenset({
    "CHANGELOG.md",
    "docs/maintainer/model-comparison/20260411-111541_MiniMax-M2.5.txt",
    "docs/maintainer/model-comparison/20260411-111541_deepseek-v3.txt",
    "docs/maintainer/model-comparison/20260411-111541_glm-5.txt",
    "docs/maintainer/model-comparison/20260411-111541_qwen3.6-plus.txt",
    "docs/maintainer/model-comparison/20260411-111541_summary.md",
    "docs/maintainer/pre-phase-skill-gap-analysis.md",
    "docs/maintainer/review-loop-mainchain-design.md",
    "docs/maintainer/review-loop-mainchain-plan.md",
    "docs/maintainer/skill-optimization-analysis-2026-04-11.md",
    "docs/maintainer/skill-optimization-results-2026-04-11.md",
    "docs/maintainer/template-adoption-tracker.md",
    "docs/maintainer/template-rollout-plan.md",
    "docs/maintainer/v1.2-test-results.txt",
})
EXPECTED_CORE = (
    "requirement-interview",
    "scoped-tasking",
    "design-before-plan",
    "architecture-design",
    "implementation-planning",
    "bugfix-workflow",
    "safe-refactor",
    "artifact-review-loop",
    "impact-analysis",
    "targeted-validation",
)
EXPECTED_OPTIONAL = ("multi-agent-protocol", "manage-agents-md")
EXPECTED_RETIRED_DIGEST = "c9f9d0270f98e21db3665796cdf27707496c629316b726e78c6684616e37fe15"
EXPECTED_MIGRATIONS_DIGEST = "e1e49397b0e4e4568ae3abd366b9e971d7148f20e04625a0ce5f8e6c4088ca11"
EXPECTED_APPROVED_ABSENT_DIGEST = "dc306ef4e99e87e8d9edc5f5d9a4fe1072e9053fdc3dbcebcd2268c148f6c693"
EXPECTED_RETIRED_DELETIONS_DIGEST = "5d0a24f32ea170f8a7b710e8861bd81eb9b66bb434eb0a341d7a0546d41cd616"


class OperationalError(RuntimeError):
    """The scan could not establish repository truth."""


NONREGULAR = object()


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise OperationalError(result.stderr.decode("utf-8", "replace").strip() or "git command failed")
    return result.stdout


def _nul_paths(payload: bytes) -> list[str]:
    try:
        return [item.decode("utf-8") for item in payload.split(b"\0") if item]
    except UnicodeDecodeError as exc:
        raise OperationalError(f"git returned a non-UTF-8 repository path: {exc}") from exc


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperationalError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OperationalError(f"{path} must contain a JSON object")
    return value


def _plain_repo_path(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or any(char in value for char in "*?[]{}"):
        return None
    return value if str(path) == value else None


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        return None
    return list(value)


def _canonical_digest(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _retired_deletion_map(value: object) -> dict[str, str] | None:
    if not isinstance(value, list):
        return None
    result: dict[str, str] = {}
    for item in value:
        if not isinstance(item, dict) or set(item) != {"path", "index_sha256"}:
            return None
        path = _plain_repo_path(item.get("path"))
        digest = item.get("index_sha256")
        if (
            path is None
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
            or path in result
        ):
            return None
        result[path] = digest
    return result


def _catalog_issues(root: Path, catalog: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    expected_fields = {
        "schema_version",
        "core_skill_names",
        "optional_skill_names",
        "retired_skill_names",
        "approved_convergent_absent",
        "approved_retired_index_deletions",
        "retired_name_exceptions",
    }
    if set(catalog) != expected_fields:
        issues.append(
            "skill_catalog.json fields differ: "
            f"missing={sorted(expected_fields - set(catalog))}, extra={sorted(set(catalog) - expected_fields)}"
        )
    if catalog.get("schema_version") != "1.1":
        issues.append("skill_catalog.json schema_version must be '1.1'")

    core = _string_list(catalog.get("core_skill_names"))
    optional = _string_list(catalog.get("optional_skill_names"))
    retired = _string_list(catalog.get("retired_skill_names"))
    absent = _string_list(catalog.get("approved_convergent_absent"))
    retired_deletions = _retired_deletion_map(
        catalog.get("approved_retired_index_deletions")
    )
    for label, values in (
        ("core_skill_names", core),
        ("optional_skill_names", optional),
        ("retired_skill_names", retired),
        ("approved_convergent_absent", absent),
    ):
        if values is None:
            issues.append(f"{label} must be an array of non-empty strings")
        elif len(values) != len(set(values)):
            issues.append(f"{label} contains duplicates")
    if core is not None and tuple(core) != EXPECTED_CORE:
        issues.append("core_skill_names must equal the locked core-10 list in canonical order")
    if optional is not None and tuple(optional) != EXPECTED_OPTIONAL:
        issues.append("optional_skill_names must equal the locked optional-2 list in canonical order")
    if core is not None and optional is not None and set(core) & set(optional):
        issues.append("core_skill_names and optional_skill_names overlap")
    if retired is not None and _canonical_digest(retired) != EXPECTED_RETIRED_DIGEST:
        issues.append("retired_skill_names must equal the locked retired-6 list in canonical order")
    if absent is not None and _canonical_digest(absent) != EXPECTED_APPROVED_ABSENT_DIGEST:
        issues.append("approved_convergent_absent must equal the locked 27-path list in canonical order")
    if retired_deletions is None:
        issues.append(
            "approved_retired_index_deletions must contain exact path/index_sha256 objects"
        )
    elif _canonical_digest(catalog.get("approved_retired_index_deletions")) != EXPECTED_RETIRED_DELETIONS_DIGEST:
        issues.append(
            "approved_retired_index_deletions must equal the locked 9-path deletion list in canonical order"
        )
    if retired is not None and core is not None and optional is not None:
        if set(retired) & (set(core) | set(optional)):
            issues.append("retired Skill names overlap the active catalog")

    exceptions = catalog.get("retired_name_exceptions")
    if not isinstance(exceptions, list):
        issues.append("retired_name_exceptions must be an array")
        return issues
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(exceptions):
        label = f"retired_name_exceptions[{index}]"
        if not isinstance(item, dict) or set(item) != {"path", "scope", "reason"}:
            issues.append(f"{label} must contain only path, scope, and reason")
            continue
        path = _plain_repo_path(item.get("path"))
        scope = item.get("scope")
        reason = item.get("reason")
        if path is None:
            issues.append(f"{label}.path must be an exact repo-relative path without glob syntax")
            continue
        if scope not in ALLOWED_SCOPES:
            issues.append(f"{label}.scope is unsupported: {scope!r}")
        if scope in {
            "catalog-field:retired_skill_names",
            "catalog-field:approved_retired_index_deletions",
        } and path != str(CATALOG_PATH):
            issues.append(f"{label}: catalog-field scope is allowed only on {CATALOG_PATH}")
        if scope in {
            "migration-field:legacy_skill",
            "migration-field:retired_skill_names",
            "migration-field:approved_retired_index_deletions",
        } and path != str(MIGRATION_PATH):
            issues.append(f"{label}: migration-field scope is allowed only on {MIGRATION_PATH}")
        if scope == "python-field:id" and path not in PYTHON_ID_EXCEPTION_PATHS:
            issues.append(f"{label}: python-field:id path is not in the locked allowlist")
        if scope == "historical-file" and path not in HISTORICAL_EXCEPTION_PATHS:
            issues.append(f"{label}: historical-file path is not in the locked allowlist")
        if not isinstance(reason, str) or not reason.strip():
            issues.append(f"{label}.reason must be a non-empty string")
        if (path, str(scope)) in seen:
            issues.append(f"duplicate exception for {path} and {scope}")
        seen.add((path, str(scope)))
        full_path = root / path
        try:
            mode = full_path.lstat().st_mode
        except FileNotFoundError:
            issues.append(f"exception path does not exist: {path}")
            continue
        if not stat.S_ISREG(mode):
            issues.append(f"exception path must be a regular file: {path}")
            continue
        if scope == "historical-file":
            if path == "CHANGELOG.md":
                try:
                    changelog_text = full_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    issues.append(f"cannot validate changelog history marker: {exc}")
                else:
                    if "Entries below this point describe historical repository states" not in changelog_text:
                        issues.append("CHANGELOG.md lacks the locked history boundary marker")
            elif full_path.suffix.lower() == ".md":
                try:
                    first_lines = full_path.read_text(encoding="utf-8").splitlines()[:10]
                except (OSError, UnicodeDecodeError) as exc:
                    issues.append(f"cannot validate historical marker in {path}: {exc}")
                else:
                    if not any(line.strip() == "Status: Historical" for line in first_lines):
                        issues.append(f"historical Markdown lacks 'Status: Historical' in first 10 lines: {path}")
            elif full_path.suffix.lower() != ".txt":
                issues.append(f"historical-file exception must be an exact .md or .txt file: {path}")
    actual_python_paths = {
        item.get("path") for item in exceptions
        if isinstance(item, dict) and item.get("scope") == "python-field:id"
    }
    actual_historical_paths = {
        item.get("path") for item in exceptions
        if isinstance(item, dict) and item.get("scope") == "historical-file"
    }
    if actual_python_paths != PYTHON_ID_EXCEPTION_PATHS:
        issues.append(
            "python-field:id exception paths differ from the locked allowlist: "
            f"missing={sorted(PYTHON_ID_EXCEPTION_PATHS - actual_python_paths)}, "
            f"extra={sorted(actual_python_paths - PYTHON_ID_EXCEPTION_PATHS)}"
        )
    if actual_historical_paths != HISTORICAL_EXCEPTION_PATHS:
        issues.append(
            "historical-file exception paths differ from the locked allowlist: "
            f"missing={sorted(HISTORICAL_EXCEPTION_PATHS - actual_historical_paths)}, "
            f"extra={sorted(actual_historical_paths - HISTORICAL_EXCEPTION_PATHS)}"
        )
    return issues


def _exception_map(catalog: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for item in catalog.get("retired_name_exceptions", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str) and isinstance(item.get("scope"), str):
            result.setdefault(item["path"], set()).add(item["scope"])
    return result


def _occurring_names(payload: bytes, retired: Iterable[str]) -> list[str]:
    return [name for name in retired if name.encode("utf-8") in payload]


def _scan_json_fields(
    relative: str,
    payload: bytes,
    retired: list[str],
    scopes: set[str],
) -> list[str]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _occurring_names(payload, retired)
    violations: set[str] = set()

    def walk(node: object, path: tuple[object, ...]) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                for name in retired:
                    if name in str(key):
                        violations.add(name)
                walk(child, path + (key,))
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, path + (index,))
        elif isinstance(node, str):
            allowed = False
            if "catalog-field:retired_skill_names" in scopes:
                allowed = path == ("retired_skill_names",) or path[:1] == ("retired_skill_names",)
            if "migration-field:retired_skill_names" in scopes:
                allowed = allowed or path[:1] == ("retired_skill_names",)
            if "migration-field:legacy_skill" in scopes:
                allowed = allowed or (len(path) == 3 and path[0] == "migrations" and path[2] == "legacy_skill")
            if "catalog-field:approved_retired_index_deletions" in scopes:
                allowed = allowed or (
                    len(path) == 3
                    and path[0] == "approved_retired_index_deletions"
                    and path[2] == "path"
                )
            if "migration-field:approved_retired_index_deletions" in scopes:
                allowed = allowed or (
                    len(path) == 3
                    and path[0] == "approved_retired_index_deletions"
                    and path[2] == "path"
                )
            if not allowed:
                for name in retired:
                    if name in node:
                        violations.add(name)
    walk(value, ())
    return sorted(violations)


def _mask_python_id_literals(payload: bytes) -> bytes:
    try:
        text = payload.decode("utf-8")
        tree = ast.parse(text)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise OperationalError(f"cannot AST-parse python-field:id exception: {exc}") from exc
    lines = payload.splitlines(keepends=True)
    starts: list[int] = []
    offset = 0
    for line in lines:
        starts.append(offset)
        offset += len(line)
    masked = bytearray(payload)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            value = keyword.value
            if (
                keyword.arg == "id"
                and isinstance(value, ast.Constant)
                and isinstance(value.value, str)
                and hasattr(value, "end_lineno")
            ):
                start = starts[value.lineno - 1] + value.col_offset
                end = starts[value.end_lineno - 1] + value.end_col_offset
                masked[start:end] = b" " * (end - start)
    return bytes(masked)


def _scan_payload(
    relative: str,
    payload: bytes,
    retired: list[str],
    scopes: set[str],
) -> list[str]:
    if "historical-file" in scopes:
        if relative == "CHANGELOG.md":
            marker = b"Entries below this point describe historical repository states"
            payload = payload.split(marker, 1)[0]
        else:
            return []
    if any(scope.startswith("catalog-field:") or scope.startswith("migration-field:") for scope in scopes):
        return _scan_json_fields(relative, payload, retired, scopes)
    if "python-field:id" in scopes:
        payload = _mask_python_id_literals(payload)
    return _occurring_names(payload, retired)


def _regular_file_payload(path: Path) -> bytes | None | object:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(mode):
        return NONREGULAR
    try:
        return path.read_bytes()
    except OSError as exc:
        raise OperationalError(f"cannot read {path}: {exc}") from exc


def validate_repository(root: Path, catalog_path: Path = CATALOG_PATH) -> dict[str, Any]:
    resolved_catalog_path = catalog_path if catalog_path.is_absolute() else root / catalog_path
    catalog = _load_json(resolved_catalog_path)
    issues = _catalog_issues(root, catalog)
    retired = _string_list(catalog.get("retired_skill_names")) or []
    active = (_string_list(catalog.get("core_skill_names")) or []) + (
        _string_list(catalog.get("optional_skill_names")) or []
    )
    actual_skills = sorted(
        path.name
        for path in (root / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    ) if (root / "skills").is_dir() else []
    if actual_skills != sorted(active):
        issues.append(
            f"skills/ must contain exactly the cataloged 12 packages; actual={actual_skills}, expected={sorted(active)}"
        )

    migration = _load_json(root / MIGRATION_PATH)
    expected_migration_fields = {
        "schema_version",
        "target_skill",
        "retired_skill_names",
        "approved_convergent_absent",
        "approved_retired_index_deletions",
        "migrations",
    }
    if set(migration) != expected_migration_fields:
        issues.append(
            "review migration matrix fields differ: "
            f"missing={sorted(expected_migration_fields - set(migration))}, "
            f"extra={sorted(set(migration) - expected_migration_fields)}"
        )
    migration_retired = _string_list(migration.get("retired_skill_names"))
    if migration.get("schema_version") != "1.1" or migration.get("target_skill") != "artifact-review-loop":
        issues.append("review migration matrix header is invalid")
    if migration_retired != retired:
        issues.append("review migration matrix retired_skill_names differs from the catalog")
    if migration.get("approved_convergent_absent") != catalog.get("approved_convergent_absent"):
        issues.append("review migration matrix approved_convergent_absent differs from the catalog")
    if migration.get("approved_retired_index_deletions") != catalog.get("approved_retired_index_deletions"):
        issues.append(
            "review migration matrix approved_retired_index_deletions differs from the catalog"
        )
    rows = migration.get("migrations")
    if (
        not isinstance(rows, list)
        or len(rows) != len(retired)
        or any(not isinstance(row, dict) for row in rows)
        or [row.get("legacy_skill") for row in rows] != retired
    ):
        issues.append("review migration rows must cover the six retired Skills in catalog order")
    elif any(set(row) != {"legacy_skill", "artifact_type", "context"} for row in rows):
        issues.append("review migration rows must contain only legacy_skill, artifact_type, and context")
    elif _canonical_digest([
        [row["legacy_skill"], row["artifact_type"], row["context"]]
        for row in rows
    ]) != EXPECTED_MIGRATIONS_DIGEST:
        issues.append("review migration rows differ from the locked legacy-to-artifact mapping")

    exception_map = _exception_map(catalog)
    tracked = _nul_paths(_git(root, "ls-files", "-z", "--cached"))
    approved = _string_list(catalog.get("approved_convergent_absent")) or []
    approved_set = set(approved)
    planned_deletions = _retired_deletion_map(
        catalog.get("approved_retired_index_deletions")
    ) or {}
    planned_deletion_paths = set(planned_deletions)
    deleted_with_retired: set[str] = set()
    records: list[tuple[str, str, bytes]] = []
    counts = {"tracked_current": 0, "tracked_deleted": 0, "untracked": 0, "skipped_nonregular": 0}

    for relative in tracked:
        payload = _regular_file_payload(root / relative)
        if payload is None:
            payload = _git(root, "show", f":{relative}")
            names = _occurring_names(payload, retired)
            if names:
                deleted_with_retired.add(relative)
            counts["tracked_deleted"] += 1
            if relative in approved_set:
                continue
            if relative in planned_deletions:
                actual_digest = hashlib.sha256(payload).hexdigest()
                if actual_digest != planned_deletions[relative]:
                    issues.append(
                        "approved retired index deletion digest mismatch: "
                        f"{relative} expected={planned_deletions[relative]} actual={actual_digest}"
                    )
                if not names:
                    issues.append(
                        f"approved retired index deletion no longer contains a retired name: {relative}"
                    )
                continue
            records.append((relative, "tracked-deleted-index", payload))
        elif payload is NONREGULAR:
            counts["skipped_nonregular"] += 1
            issues.append(
                f"tracked governed path must be a regular file for retired-name scanning: {relative}"
            )
        else:
            counts["tracked_current"] += 1
            assert isinstance(payload, bytes)
            records.append((relative, "tracked-current", payload))

    approved_present: list[str] = []
    for path in approved_set:
        try:
            (root / path).lstat()
        except FileNotFoundError:
            continue
        approved_present.append(path)
    approved_present.sort()
    if approved_present:
        issues.append(f"approved_convergent_absent paths must remain absent: {approved_present}")
    present_planned_deletions: list[str] = []
    for path in planned_deletion_paths:
        try:
            (root / path).lstat()
        except FileNotFoundError:
            continue
        present_planned_deletions.append(path)
    present_planned_deletions.sort()
    if present_planned_deletions:
        issues.append(
            "approved_retired_index_deletions paths must remain absent: "
            f"{present_planned_deletions}"
        )
    if deleted_with_retired - approved_set - planned_deletion_paths:
        issues.append(
            "deleted index blobs containing retired names are not approved: "
            f"missing={sorted(deleted_with_retired - approved_set - planned_deletion_paths)}"
        )

    pathspecs = [*GOVERNED_ROOTS, *GOVERNED_TOP_LEVEL_FILES]
    for relative in _nul_paths(_git(root, "ls-files", "-z", "--others", "--exclude-standard", "--", *pathspecs)):
        payload = _regular_file_payload(root / relative)
        if payload is None:
            counts["skipped_nonregular"] += 1
            continue
        if payload is NONREGULAR:
            counts["skipped_nonregular"] += 1
            issues.append(
                f"untracked governed path must be a regular file for retired-name scanning: {relative}"
            )
            continue
        assert isinstance(payload, bytes)
        counts["untracked"] += 1
        records.append((relative, "untracked-governed", payload))

    violations: list[dict[str, Any]] = []
    for relative, source, payload in records:
        names = _scan_payload(relative, payload, retired, exception_map.get(relative, set()))
        if names:
            violations.append({"path": relative, "source": source, "retired_skill_names": names})

    return {
        "schema_version": "1.1",
        "catalog_path": str(catalog_path),
        "counts": {
            **counts,
            "files_scanned": len(records),
            "exceptions": sum(len(value) for value in exception_map.values()),
            "violations": len(violations),
            "catalog_issues": len(issues),
        },
        "catalog_issues": issues,
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument(
        "--print-all-skills",
        action="store_true",
        help="Validate the catalog, then print its 12 active Skill names in ASCII order",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        result = validate_repository(root, args.catalog)
    except OperationalError as exc:
        print(f"OPERATIONAL ERROR: {exc}", file=sys.stderr)
        return 2
    failed = bool(result["catalog_issues"] or result["violations"])
    if args.print_all_skills:
        if failed:
            for issue in result["catalog_issues"]:
                print(f"ERROR: {issue}", file=sys.stderr)
            for violation in result["violations"]:
                print(
                    f"ERROR: {violation['path']} ({violation['source']}): "
                    f"active retired references {', '.join(violation['retired_skill_names'])}",
                    file=sys.stderr,
                )
            return 1
        try:
            catalog_path = args.catalog if args.catalog.is_absolute() else root / args.catalog
            catalog = _load_json(catalog_path)
            active = [
                *(_string_list(catalog.get("core_skill_names")) or []),
                *(_string_list(catalog.get("optional_skill_names")) or []),
            ]
            active = sorted(active, key=lambda name: name.encode("ascii"))
        except (OperationalError, UnicodeEncodeError) as exc:
            print(f"OPERATIONAL ERROR: cannot produce ASCII Skill list: {exc}", file=sys.stderr)
            return 2
        print("\n".join(active))
        return 0
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for issue in result["catalog_issues"]:
            print(f"ERROR: {issue}")
        for violation in result["violations"]:
            print(
                f"ERROR: {violation['path']} ({violation['source']}): "
                f"active retired references {', '.join(violation['retired_skill_names'])}"
            )
        if not result["catalog_issues"] and not result["violations"]:
            print("OK: canonical 12-Skill catalog and retired-reference contract passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
