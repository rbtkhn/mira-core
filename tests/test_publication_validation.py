from __future__ import annotations

from pathlib import Path

import publication_validation as routing


def make_tree(root: Path) -> None:
    for relative in (
        "archive/notes/2026-08-17-note.md",
        "archive/essays/2026-08-17-essay.md",
        "archive/sessions/registry.json",
        "archive/schemas/session-memorial.schema.json",
        "projects/grace-gems/README.md",
        "archive/sources/geopolitics/source-manifest.json",
        "archive/sources/geopolitics/sources/2026-08-17/source-example.md",
        "narrative-geopolitics/voices/aguilar/source-index.md",
        "narrative-geopolitics/work/daily/2026-08-17/synthesis.md",
        "narrative-geopolitics/work/forecasts/forecast-ledger.md",
        "narrative-geopolitics/work/morning-brief/2026-08-17.md",
        "narrative-geopolitics/work/morning-brief/2026-08-17.receipt.json",
        "docs/skill-drafts/mira-github/SKILL.md",
        "docs/mira-core-name-migration.md",
        "docs/plans/2026-08-16-mira-archive-name-migration.md",
        "mira/continuity/session-registry.json",
        "archive/library/README.md",
        "archive/library/library-registry.json",
        "archive/library/ancient/index.md",
        "scripts/example.py",
        "tools/example.py",
        "tests/test_example.py",
        "AGENTS.md",
        "unknown/file.md",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")
    owning_test = root / "tests/test_mira_github_skill.py"
    owning_test.write_text("fixture\n", encoding="utf-8")


def test_router_resolves_initial_artifact_classes(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(
        [
            "archive/notes/2026-08-17-note.md",
            "archive/essays/2026-08-17-essay.md",
            "projects/grace-gems/README.md",
            "docs/skill-drafts/mira-github/SKILL.md",
            "scripts/example.py",
            "tools/example.py",
            "tests/test_example.py",
            "AGENTS.md",
        ],
        repo_root=tmp_path,
    )
    assert report["status"] == "manual-required"
    assert report["owners"] == [
        "mira-notes",
        "mira-essays",
        "grace-gems/stewardship",
        "skill/control",
        "repo-structural",
    ]
    assert report["validation_classes"] == ["domain-governed", "repo-structural"]
    assert report["commands"] == [
        "tools/run.ps1 test --path tests/test_mira_github_skill.py",
        "tools/run.ps1 test --mode fast --explain-route",
        "tools/run.ps1 test --path tests/test_example.py",
    ]
    assert len(report["manual_checks"]) == 4
    assert report["blockers"] == []


def test_router_resolves_mira_control_plane_paths(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(
        [
            "docs/mira-core-name-migration.md",
            "docs/plans/2026-08-16-mira-archive-name-migration.md",
            "mira/continuity/session-registry.json",
        ],
        repo_root=tmp_path,
    )

    assert report["status"] == "manual-required"
    assert report["owners"] == ["mira-control-plane"]
    assert report["validation_classes"] == ["repo-structural"]
    assert report["commands"] == ["tools/run.ps1 test --mode fast --explain-route"]
    assert report["manual_checks"] == [
        "Verify Mira control-plane semantics, authority boundaries, and historical "
        "provenance preservation remain coherent."
    ]
    assert report["blockers"] == []


def test_router_resolves_mira_library_paths(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(
        [
            "archive/library/README.md",
            "archive/library/library-registry.json",
            "archive/library/ancient/index.md",
        ],
        repo_root=tmp_path,
    )

    assert report["status"] == "resolved"
    assert report["owners"] == ["mira-library"]
    assert report["validation_classes"] == ["repo-structural"]
    assert report["commands"] == [
        "tools/run.ps1 library validate --json",
        "tools/run.ps1 test --path tests/test_archive_library.py",
    ]
    assert report["manual_checks"] == []
    assert report["blockers"] == []


def test_router_resolves_narrative_geopolitics_artifacts(tmp_path: Path) -> None:
    make_tree(tmp_path)
    daily_dir = tmp_path / "narrative-geopolitics/work/daily/2026-08-17"
    daily_dir.mkdir(parents=True, exist_ok=True)

    report = routing.build_report(
        [
            "archive/sources/geopolitics/source-manifest.json",
            "narrative-geopolitics/voices/aguilar/source-index.md",
            "narrative-geopolitics/work/daily/2026-08-17",
            "narrative-geopolitics/work/forecasts/forecast-ledger.md",
            "narrative-geopolitics/work/morning-brief/2026-08-17.receipt.json",
        ],
        repo_root=tmp_path,
    )

    assert report["status"] == "manual-required"
    assert report["owners"] == [
        "narrative-geopolitics/archive",
        "geo-strategy",
        "geo-strategy/forecast-ledger",
        "morning-brief",
    ]
    assert report["validation_classes"] == ["domain-governed"]
    assert report["commands"] == [
        "tools/run.ps1 test --path tests/test_voice_count_authority.py",
        "tools/run.ps1 daily-validate --date 2026-08-17 --stage issue",
        "tools/run.ps1 test --path tests/test_morning_brief.py",
    ]
    assert report["manual_checks"] == [routing.MANUAL_NARRATIVE_GEOPOLITICS_CHECK]
    assert report["blockers"] == []


def test_router_resolves_grace_gems_files_to_stewardship_review(
    tmp_path: Path,
) -> None:
    make_tree(tmp_path)
    matrix = tmp_path / "projects/grace-gems/admission-matrix.md"
    matrix.write_text("fixture\n", encoding="utf-8")

    report = routing.build_report(
        ["projects/grace-gems/README.md", "projects/grace-gems/admission-matrix.md"],
        repo_root=tmp_path,
    )

    assert report["status"] == "manual-required"
    assert report["owners"] == ["grace-gems/stewardship"]
    assert report["validation_classes"] == ["domain-governed"]
    assert report["commands"] == []
    assert report["manual_checks"] == [routing.MANUAL_GRACE_GEMS_CHECK]
    assert report["blockers"] == []


def test_router_assigns_session_memorials_to_governing_validator(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(["archive/sessions/registry.json", "archive/schemas/session-memorial.schema.json"], repo_root=tmp_path)
    assert report["status"] == "manual-required"
    assert report["owners"] == ["mira-sessions"]
    assert report["commands"] == ["tools/run.ps1 mira-sessions validate"]
    assert report["manual_checks"] == [routing.MANUAL_SESSION_MEMORIAL_CHECK]


def test_router_blocks_unknown_duplicate_and_unsafe_paths(tmp_path: Path) -> None:
    make_tree(tmp_path)
    outside = tmp_path.parent / "outside-publication-validation.md"
    outside.write_text("fixture\n", encoding="utf-8")
    try:
        report = routing.build_report(
            [
                "unknown/file.md",
                "AGENTS.md",
                "AGENTS.md",
                "../outside-publication-validation.md",
                "tests/test_*.py",
                str(outside),
            ],
            repo_root=tmp_path,
        )
    finally:
        outside.unlink(missing_ok=True)
    assert report["status"] == "blocked"
    assert any("no deterministic" in blocker for blocker in report["blockers"])
    assert any("duplicate path" in blocker for blocker in report["blockers"])
    assert any("traversal" in blocker for blocker in report["blockers"])
    assert any("globbed" in blocker for blocker in report["blockers"])
    assert any("outside repository" in blocker for blocker in report["blockers"])


def test_router_rejects_missing_paths(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(["archive/notes/missing.md"], repo_root=tmp_path)
    assert report["status"] == "blocked"
    assert report["paths"] == []
    assert report["blockers"] == ["path does not exist: archive/notes/missing.md"]
