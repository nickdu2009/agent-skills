#!/usr/bin/env python3
"""Self-tests for the canonical catalog and retired-name scanner."""

from __future__ import annotations

import hashlib
import contextlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / "analysis"))

import validate_skill_catalog as validator


EXPECTED_MIGRATION_ROUTES = (
    ("requirements", "requested"),
    ("design", "requested"),
    ("plan", "requested"),
    ("code", "requested"),
    ("tests", "requested"),
    ("code", "self-delivery"),
)
EXPECTED_MIGRATIONS_DIGEST = "e1e49397b0e4e4568ae3abd366b9e971d7148f20e04625a0ce5f8e6c4088ca11"
EXPECTED_APPROVED_ABSENT_DIGEST = "dc306ef4e99e87e8d9edc5f5d9a4fe1072e9053fdc3dbcebcd2268c148f6c693"
EXPECTED_RETIRED_DELETIONS_DIGEST = "5d0a24f32ea170f8a7b710e8861bd81eb9b66bb434eb0a341d7a0546d41cd616"


def canonical_digest(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def main() -> int:
    source_catalog = json.loads(
        (validator.REPO_ROOT / validator.CATALOG_PATH).read_text(encoding="utf-8")
    )
    retired = source_catalog["retired_skill_names"]
    approved_absent = source_catalog["approved_convergent_absent"]
    retired_deletions = source_catalog["approved_retired_index_deletions"]
    assert canonical_digest(approved_absent) == EXPECTED_APPROVED_ABSENT_DIGEST
    assert canonical_digest(retired_deletions) == EXPECTED_RETIRED_DELETIONS_DIGEST
    expected_migrations = tuple(
        (name, artifact_type, context)
        for name, (artifact_type, context) in zip(
            retired,
            EXPECTED_MIGRATION_ROUTES,
            strict=True,
        )
    )
    assert canonical_digest([list(row) for row in expected_migrations]) == EXPECTED_MIGRATIONS_DIGEST
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        for name in (*validator.EXPECTED_CORE, *validator.EXPECTED_OPTIONAL):
            skill_dir = root / "skills" / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: Fixture.\n---\n",
                encoding="utf-8",
            )

        catalog = {
            "schema_version": "1.1",
            "core_skill_names": list(validator.EXPECTED_CORE),
            "optional_skill_names": list(validator.EXPECTED_OPTIONAL),
            "retired_skill_names": retired,
            "approved_convergent_absent": approved_absent,
            "approved_retired_index_deletions": retired_deletions,
            "retired_name_exceptions": [
                {
                    "path": str(validator.CATALOG_PATH),
                    "scope": "catalog-field:retired_skill_names",
                    "reason": "Fixture catalog contract.",
                },
                {
                    "path": str(validator.MIGRATION_PATH),
                    "scope": "migration-field:legacy_skill",
                    "reason": "Fixture migration rows.",
                },
                {
                    "path": str(validator.MIGRATION_PATH),
                    "scope": "migration-field:retired_skill_names",
                    "reason": "Fixture migration set.",
                },
                {
                    "path": str(validator.CATALOG_PATH),
                    "scope": "catalog-field:approved_retired_index_deletions",
                    "reason": "Fixture cutover deletion contract.",
                },
                {
                    "path": str(validator.MIGRATION_PATH),
                    "scope": "migration-field:approved_retired_index_deletions",
                    "reason": "Fixture migration deletion contract.",
                },
                *[
                    {
                        "path": path,
                        "scope": "python-field:id",
                        "reason": "Fixture stable case id.",
                    }
                    for path in sorted(validator.PYTHON_ID_EXCEPTION_PATHS)
                ],
                *[
                    {
                        "path": path,
                        "scope": "historical-file",
                        "reason": "Fixture historical document.",
                    }
                    for path in sorted(validator.HISTORICAL_EXCEPTION_PATHS)
                ],
            ],
        }
        write_json(root / validator.CATALOG_PATH, catalog)
        migration = {
            "schema_version": "1.1",
            "target_skill": "artifact-review-loop",
            "retired_skill_names": retired,
            "approved_convergent_absent": approved_absent,
            "approved_retired_index_deletions": retired_deletions,
            "migrations": [
                {
                    "legacy_skill": name,
                    "artifact_type": artifact_type,
                    "context": context,
                }
                for name, artifact_type, context in expected_migrations
            ],
        }
        write_json(root / validator.MIGRATION_PATH, migration)
        for path in validator.PYTHON_ID_EXCEPTION_PATHS:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                f"Case(id={retired[0] + '-legacy'!r}, expected=())\n",
                encoding="utf-8",
            )
        cases = root / "maintainer/data/trigger_test_data.py"
        for path in validator.HISTORICAL_EXCEPTION_PATHS:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                (
                    (
                        "# Changelog\n\n"
                        "Entries below this point describe historical repository states\n\n"
                        f"{retired[1]}\n"
                    )
                    if path == "CHANGELOG.md"
                    else f"# History\n\nStatus: Historical\n\n{retired[1]}\n"
                    if target.suffix == ".md"
                    else f"{retired[1]}\n"
                ),
                encoding="utf-8",
            )
        (root / "README.md").write_text("fixture\n", encoding="utf-8")
        approved_deleted = root / approved_absent[0]
        approved_deleted.parent.mkdir(parents=True, exist_ok=True)
        approved_deleted.write_text("\n".join(retired) + "\n", encoding="utf-8")

        run_git(root, "init", "-q")
        run_git(root, "config", "user.email", "fixture@example.invalid")
        run_git(root, "config", "user.name", "Fixture")
        run_git(root, "add", ".")
        run_git(root, "commit", "-qm", "fixture")
        approved_deleted.unlink()

        clean = validator.validate_repository(root)
        assert clean["catalog_issues"] == [], clean
        assert clean["violations"] == [], clean
        assert clean["counts"]["tracked_deleted"] == 1, clean

        original_argv = sys.argv
        output = io.StringIO()
        sys.argv = [
            "validate_skill_catalog.py",
            "--root",
            str(root),
            "--print-all-skills",
        ]
        try:
            with contextlib.redirect_stdout(output):
                assert validator.main() == 0
        finally:
            sys.argv = original_argv
        assert output.getvalue().splitlines() == sorted(
            [*validator.EXPECTED_CORE, *validator.EXPECTED_OPTIONAL],
            key=lambda name: name.encode("ascii"),
        )

        untracked_link = root / "docs" / "untracked-nonregular.md"
        untracked_link.parent.mkdir(parents=True, exist_ok=True)
        untracked_link.symlink_to("../README.md")
        nonregular_untracked = validator.validate_repository(root)
        assert any(
            "untracked governed path must be a regular file" in issue
            and "docs/untracked-nonregular.md" in issue
            for issue in nonregular_untracked["catalog_issues"]
        ), nonregular_untracked
        untracked_link.unlink()

        tracked_link = root / "docs" / "tracked-nonregular.md"
        tracked_link.symlink_to("../README.md")
        run_git(root, "add", "docs/tracked-nonregular.md")
        nonregular_tracked = validator.validate_repository(root)
        assert any(
            "tracked governed path must be a regular file" in issue
            and "docs/tracked-nonregular.md" in issue
            for issue in nonregular_tracked["catalog_issues"]
        ), nonregular_tracked
        run_git(root, "rm", "--cached", "docs/tracked-nonregular.md")
        tracked_link.unlink()

        approved_broken_link = root / approved_absent[0]
        approved_broken_link.parent.mkdir(parents=True, exist_ok=True)
        approved_broken_link.symlink_to("missing-approved-target")
        approved_presence = validator.validate_repository(root)
        assert any(
            "approved_convergent_absent paths must remain absent" in issue
            and approved_absent[0] in issue
            for issue in approved_presence["catalog_issues"]
        ), approved_presence
        approved_broken_link.unlink()

        planned_path = retired_deletions[0]["path"]
        planned_target = root / planned_path
        planned_target.parent.mkdir(parents=True, exist_ok=True)
        planned_target.write_text(retired[0] + "\n", encoding="utf-8")
        run_git(root, "add", planned_path)
        planned_target.unlink()
        digest_mismatch = validator.validate_repository(root)
        assert any(
            "approved retired index deletion digest mismatch" in issue
            and planned_path in issue
            for issue in digest_mismatch["catalog_issues"]
        ), digest_mismatch
        run_git(root, "rm", "--cached", planned_path)

        planned_target.write_text("unexpected live file\n", encoding="utf-8")
        planned_present = validator.validate_repository(root)
        assert any(
            "approved_retired_index_deletions paths must remain absent" in issue
            and planned_path in issue
            for issue in planned_present["catalog_issues"]
        ), planned_present
        planned_target.unlink()

        untracked_makefile = root / "Makefile"
        untracked_makefile.write_text(retired[3] + "\n", encoding="utf-8")
        governed_top_level = validator.validate_repository(root)
        assert any(
            item["path"] == "Makefile"
            for item in governed_top_level["violations"]
        ), governed_top_level
        untracked_makefile.unlink()

        (root / "README.md").write_text(retired[2] + "\n", encoding="utf-8")
        active_reference = validator.validate_repository(root)
        assert any(item["path"] == "README.md" for item in active_reference["violations"]), active_reference
        output = io.StringIO()
        errors = io.StringIO()
        sys.argv = [
            "validate_skill_catalog.py",
            "--root",
            str(root),
            "--print-all-skills",
        ]
        try:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                assert validator.main() == 1
        finally:
            sys.argv = original_argv
        assert output.getvalue() == ""
        assert "README.md" in errors.getvalue()
        (root / "README.md").write_text("fixture\n", encoding="utf-8")

        cases.write_text(
            f"Case(id={retired[0] + '-legacy'!r}, expected=({retired[0]!r},))\n",
            encoding="utf-8",
        )
        expected_not_masked = validator.validate_repository(root)
        assert any(item["path"] == "maintainer/data/trigger_test_data.py" for item in expected_not_masked["violations"]), expected_not_masked
        cases.write_text(
            f"Case(id={retired[0] + '-legacy'!r}, expected=())\n",
            encoding="utf-8",
        )

        migration["migrations"][0]["artifact_type"] = "code"
        write_json(root / validator.MIGRATION_PATH, migration)
        migration_drift = validator.validate_repository(root)
        assert any(
            "legacy-to-artifact mapping" in issue
            for issue in migration_drift["catalog_issues"]
        ), migration_drift
        migration["migrations"][0]["artifact_type"] = "requirements"
        write_json(root / validator.MIGRATION_PATH, migration)

        migration["migrations"].append(None)
        write_json(root / validator.MIGRATION_PATH, migration)
        malformed_migration = validator.validate_repository(root)
        assert any(
            "must cover the six retired Skills" in issue
            for issue in malformed_migration["catalog_issues"]
        ), malformed_migration
        migration["migrations"].pop()
        write_json(root / validator.MIGRATION_PATH, migration)

        catalog["approved_convergent_absent"] = approved_absent[:-1]
        migration["approved_convergent_absent"] = approved_absent[:-1]
        catalog["approved_retired_index_deletions"] = retired_deletions[:-1]
        migration["approved_retired_index_deletions"] = retired_deletions[:-1]
        write_json(root / validator.CATALOG_PATH, catalog)
        write_json(root / validator.MIGRATION_PATH, migration)
        drift = validator.validate_repository(root)
        assert any("locked 27-path list" in issue for issue in drift["catalog_issues"]), drift
        assert any("locked 9-path deletion list" in issue for issue in drift["catalog_issues"]), drift

    print("OK: Skill catalog, exception scopes, and deleted-index scanner contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
