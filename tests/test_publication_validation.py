from __future__ import annotations

from pathlib import Path

import publication_validation as routing


def make_tree(root: Path) -> None:
    for relative in (
        "archive/notes/2026-08-17-note.md",
        "archive/essays/2026-08-17-essay.md",
        "archive/sessions/registry.json",
        "archive/schemas/session-memorial.schema.json",
        "archive/collections.json",
        "archive/registries/moonshots.json",
        "archive/registries/innermost-loop.json",
        "archive/sources/singularity/moonshots/transcripts/2026-08-27-example.md",
        "archive/sources/singularity/singularity-signal-ledger.json",
        "mira/journal-registry.json",
        "mira/journal.md",
        "mira/journal/2026-08-28.md",
        "mira/journal/references/MJTR-20260828-v1.json",
        "mira/journal/references/MJTR-20260828-v1.md",
        "mira/journal/continuity-index.json",
        "mira/journal/continuity-index.md",
        "projects/grace-gems/README.md",
        "archive/sources/geopolitics/source-manifest.json",
        "archive/sources/geopolitics/sources/2026-08-17/source-example.md",
        "narrative-geopolitics/method/strategy-notebook-library-routing.md",
        "narrative-geopolitics/templates/strategy-notebook.md",
        "narrative-geopolitics/voices/aguilar/source-index.md",
        "narrative-geopolitics/work/daily/2026-08-17/synthesis.md",
        "narrative-geopolitics/work/coverage/contracts/2026-08.json",
        "narrative-geopolitics/work/coverage/receipts/2026-08.jsonl",
        "narrative-geopolitics/work/forecasts/forecast-ledger.md",
        "narrative-geopolitics/work/morning-brief/2026-08-17.md",
        "narrative-geopolitics/work/morning-brief/2026-08-17.receipt.json",
        "narrative-geopolitics/work/capture/youtube/2026-08-22.jsonl",
        "narrative-geopolitics/work/historical-reference/2026-08-22-run.json",
        "narrative-geopolitics/work/historical-reference/2026-08-22-run-review-queue.json",
        "narrative-geopolitics/work/reality/claims/OPC-20260822-01.json",
        "narrative-geopolitics/work/reality/views/outcome-ledger.md",
        "docs/skill-drafts/mira-github/SKILL.md",
        "docs/mira-core-name-migration.md",
        "docs/plans/2026-08-16-mira-archive-name-migration.md",
        "docs/experiments/leaner-skills/experiment.json",
        "docs/dev-journal/README.md",
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


def test_router_resolves_experiment_contracts(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(
        ["docs/experiments/leaner-skills/experiment.json"], repo_root=tmp_path
    )
    assert report["status"] == "manual-required"
    assert report["owners"] == ["repo-structural"]
    assert report["commands"] == ["tools/run.ps1 test --mode fast --explain-route"]
    assert "frozen inputs" in report["manual_checks"][0]
    assert report["blockers"] == []


def test_router_resolves_dev_journal_docs(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(["docs/dev-journal/README.md"], repo_root=tmp_path)

    assert report["status"] == "manual-required"
    assert report["owners"] == ["dev-journal"]
    assert report["validation_classes"] == ["repo-structural"]
    assert report["commands"] == ["tools/run.ps1 test --path tests/test_publication_validation.py"]
    assert report["manual_checks"] == [routing.MANUAL_DEV_JOURNAL_CHECK]
    assert report["blockers"] == []


def test_dev_journal_readme_documents_retrospective_governance() -> None:
    readme = (Path(__file__).resolve().parents[1] / "docs" / "dev-journal" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in (
        "retrospective-current",
        "retrospective-draft",
        "Temporal stance: contemporaneous | near-contemporaneous | retrospective reconstruction",
        "Source basis: commits, diffs, tests, notes, plans, journal references, session receipts",
        "Confidence: high | medium | low",
        "Record system rationale, not Mira selfhood.",
        "Mira Journal prose is interpretive context only",
        "not contemporaneous\nmental state",
    ):
        assert phrase in readme


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


def test_router_resolves_singularity_archive_paths(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(
        [
            "archive/collections.json",
            "archive/registries/moonshots.json",
            "archive/registries/innermost-loop.json",
            "archive/sources/singularity/moonshots/transcripts/2026-08-27-example.md",
            "archive/sources/singularity/singularity-signal-ledger.json",
        ],
        repo_root=tmp_path,
    )

    assert report["status"] == "manual-required"
    assert report["owners"] == ["singularity-science/archive"]
    assert report["validation_classes"] == ["domain-governed"]
    assert report["commands"] == ["tools/run.ps1 archive validate --git-only --json"]
    assert report["manual_checks"] == [routing.MANUAL_SINGULARITY_ARCHIVE_CHECK]
    assert report["blockers"] == []


def test_router_resolves_mira_journal_paths(tmp_path: Path) -> None:
    make_tree(tmp_path)
    report = routing.build_report(
        [
            "mira/journal/2026-08-28.md",
            "mira/journal/references/MJTR-20260828-v1.json",
            "mira/journal/references/MJTR-20260828-v1.md",
            "mira/journal-registry.json",
            "mira/journal.md",
            "mira/journal/continuity-index.json",
            "mira/journal/continuity-index.md",
        ],
        repo_root=tmp_path,
    )

    assert report["status"] == "manual-required"
    assert report["owners"] == ["mira-journal"]
    assert report["validation_classes"] == ["domain-governed"]
    assert report["commands"] == [
        "tools/run.ps1 mira-journal status --from 2026-08-28 --to 2026-08-28 --json",
        "tools/run.ps1 mira-journal status --json",
    ]
    assert report["manual_checks"] == [routing.MANUAL_MIRA_JOURNAL_CHECK]
    assert report["blockers"] == []


def test_router_resolves_narrative_geopolitics_artifacts(tmp_path: Path) -> None:
    make_tree(tmp_path)
    daily_dir = tmp_path / "narrative-geopolitics/work/daily/2026-08-17"
    daily_dir.mkdir(parents=True, exist_ok=True)

    report = routing.build_report(
        [
            "archive/sources/geopolitics/source-manifest.json",
            "narrative-geopolitics/voices/aguilar/source-index.md",
            "narrative-geopolitics/method/strategy-notebook-library-routing.md",
            "narrative-geopolitics/templates/strategy-notebook.md",
            "narrative-geopolitics/work/daily/2026-08-17",
            "narrative-geopolitics/work/forecasts/forecast-ledger.md",
            "narrative-geopolitics/work/morning-brief/2026-08-17.receipt.json",
        ],
        repo_root=tmp_path,
    )

    assert report["status"] == "manual-required"
    assert report["owners"] == [
        "narrative-geopolitics/archive",
        "geo-strategy/method",
        "geo-strategy/templates",
        "geo-strategy",
        "geo-strategy/forecast-ledger",
        "morning-brief",
    ]
    assert report["validation_classes"] == ["domain-governed"]
    assert report["commands"] == [
        "tools/run.ps1 test --path tests/test_voice_count_authority.py",
        "tools/run.ps1 test --mode fast --explain-route",
        "tools/run.ps1 daily-validate --date 2026-08-17 --stage issue",
        "tools/run.ps1 test --path tests/test_morning_brief.py",
    ]
    assert report["manual_checks"] == [routing.MANUAL_NARRATIVE_GEOPOLITICS_CHECK]
    assert report["blockers"] == []


def test_router_resolves_monthly_coverage_contract_and_receipts(tmp_path: Path) -> None:
    make_tree(tmp_path)

    report = routing.build_report(
        [
            "narrative-geopolitics/work/coverage/contracts/2026-08.json",
            "narrative-geopolitics/work/coverage/receipts/2026-08.jsonl",
        ],
        repo_root=tmp_path,
    )

    assert report["status"] == "manual-required"
    assert report["owners"] == ["archive-audit/monthly-completeness"]
    assert report["validation_classes"] == ["domain-governed"]
    assert report["commands"] == [
        "tools/run.ps1 archive-audit --month 2026-08 --format json"
    ]
    assert report["manual_checks"] == [routing.MANUAL_NARRATIVE_GEOPOLITICS_CHECK]
    assert report["blockers"] == []


def test_router_resolves_narrative_geopolitics_work_surfaces(tmp_path: Path) -> None:
    make_tree(tmp_path)
    policy = tmp_path / "narrative-geopolitics/work/capture/youtube/youtube-capture-policy.yml"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text("version: 1\n", encoding="utf-8")
    legacy_inventory = tmp_path / "narrative-geopolitics/work/verification/legacy-inventory.json"
    legacy_inventory.parent.mkdir(parents=True, exist_ok=True)
    legacy_inventory.write_text("{}\n", encoding="utf-8")
    legacy_packet = (
        tmp_path
        / "narrative-geopolitics/work/verification/packets/VER-20260822-01-example/README.md"
    )
    legacy_packet.parent.mkdir(parents=True, exist_ok=True)
    legacy_packet.write_text("# Fixture\n", encoding="utf-8")
    report = routing.build_report(
        [
            "narrative-geopolitics/work/capture/youtube/youtube-capture-policy.yml",
            "narrative-geopolitics/work/capture/youtube/2026-08-22.jsonl",
            "narrative-geopolitics/work/historical-reference/2026-08-22-run.json",
            "narrative-geopolitics/work/historical-reference/2026-08-22-run-review-queue.json",
            "narrative-geopolitics/work/reality/claims/OPC-20260822-01.json",
            "narrative-geopolitics/work/reality/views/outcome-ledger.md",
            "narrative-geopolitics/work/verification/legacy-inventory.json",
            "narrative-geopolitics/work/verification/packets/VER-20260822-01-example/README.md",
        ],
        repo_root=tmp_path,
    )

    assert report["status"] == "manual-required"
    assert report["owners"] == [
        "youtube-capture/policy",
        "youtube-capture",
        "historical-reference",
        "reality-check",
    ]
    assert report["validation_classes"] == ["repo-structural", "domain-governed"]
    assert report["commands"] == [
        "tools/run.ps1 test --path tests/test_youtube_capture.py",
        "python -X utf8 scripts/youtube_capture.py status --date 2026-08-22",
        "python -X utf8 scripts/youtube_capture.py audit-duplicates --date 2026-08-22 --json",
        "python scripts/validate_historical_reference_taxonomy.py --run "
        "narrative-geopolitics/work/historical-reference/2026-08-22-run.json",
        "python scripts/reality.py check",
    ]
    assert report["manual_checks"] == [
        routing.MANUAL_YOUTUBE_CAPTURE_CHECK,
        routing.MANUAL_HISTORICAL_REFERENCE_CHECK,
        routing.MANUAL_REALITY_CHECK,
    ]
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
