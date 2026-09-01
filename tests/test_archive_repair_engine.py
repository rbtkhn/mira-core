from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
import sys

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import archive_repair_engine as engine


def source_text(
    *,
    host: str = "daniel-davis",
    body: str = "The straight of hormones stayed broken in Anchora.\n",
    extra: str = "",
) -> str:
    return (
        "---\n"
        "pub_date: 2026-07-31\n"
        f"host_slug: {host}\n"
        "title: Example Archive Source\n"
        "routing_state: provisional\n"
        f"{extra}"
        "---\n"
        "# Example Archive Source\n\n"
        "## Transcript\n\n"
        f"{body}"
    )


def archive_repo(
    tmp_path: Path,
    *,
    host: str = "daniel-davis",
    body: str = "The straight of hormones stayed broken in Anchora.\n",
    extra: str = "",
    second: bool = False,
    source_identity: str | None = None,
) -> tuple[Path, Path, Path, list[str]]:
    repo = tmp_path / "repo"
    sources = repo / "archive" / "sources" / "geopolitics" / "sources"
    day = sources / "2026-07-31"
    day.mkdir(parents=True)
    manifest_path = sources.parent / "source-manifest.json"
    paths: list[str] = []
    rows = []
    count = 2 if second else 1
    for index in range(count):
        path = day / f"source-example-{index}.md"
        path.write_text(
            source_text(host=host, body=body, extra=extra),
            encoding="utf-8",
            newline="\n",
        )
        relative = path.relative_to(repo).as_posix()
        paths.append(relative)
        rows.append(
            {
                "date": "2026-07-31",
                "host_slug": host,
                "local_path": relative,
                "title": f"Example {index}",
                "voice_slugs": ["example"],
                **({"source_identity": source_identity} if source_identity else {}),
            }
        )
    manifest = {
        "manifest_id": "manifest-test",
        "source_count": len(rows),
        "sources": rows,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return repo, sources, manifest_path, paths


def build(
    repo: Path,
    sources: Path,
    manifest: Path,
    paths: list[str],
    repair_class: str,
    *,
    resection: bool = False,
) -> engine.ArchiveRepairPlan:
    return engine.build_plan(
        paths,
        repair_class,
        resection=resection,
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest,
    )


@pytest.mark.parametrize(
    "bad_path",
    (
        "../outside.md",
        "archive/sources/geopolitics/sources/*.md",
        "README.md",
    ),
)
def test_target_paths_must_be_contained_archive_files(tmp_path: Path, bad_path: str) -> None:
    repo, sources, _, _ = archive_repo(tmp_path)
    with pytest.raises(engine.ArchiveRepairError):
        engine.resolve_targets([bad_path], repo_root=repo, sources_root=sources)


def test_absolute_target_is_rejected(tmp_path: Path) -> None:
    repo, sources, _, paths = archive_repo(tmp_path)
    absolute = str(repo / paths[0])
    with pytest.raises(engine.ArchiveRepairError, match="repository-relative"):
        engine.resolve_targets([absolute], repo_root=repo, sources_root=sources)


def test_duplicate_target_is_rejected(tmp_path: Path) -> None:
    repo, sources, _, paths = archive_repo(tmp_path)
    with pytest.raises(engine.ArchiveRepairError, match="duplicate target"):
        engine.resolve_targets([paths[0], paths[0]], repo_root=repo, sources_root=sources)


def test_target_limit_is_enforced(tmp_path: Path) -> None:
    repo, sources, _, paths = archive_repo(tmp_path)
    with pytest.raises(engine.ArchiveRepairError, match="bounded"):
        engine.resolve_targets(paths * (engine.MAX_TARGETS + 1), repo_root=repo, sources_root=sources)


def test_escaping_symlink_is_rejected(tmp_path: Path) -> None:
    repo, sources, _, _ = archive_repo(tmp_path)
    outside = repo / "outside.md"
    outside.write_text("outside", encoding="utf-8", newline="\n")
    link = sources / "2026-07-31" / "escape.md"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("creating symlinks is unavailable in this environment")
    relative = link.relative_to(repo).as_posix()
    with pytest.raises(engine.ArchiveRepairError, match="stay under"):
        engine.resolve_targets([relative], repo_root=repo, sources_root=sources)


def test_missing_or_duplicate_manifest_membership_is_rejected(tmp_path: Path) -> None:
    repo, sources, manifest_path, paths = archive_repo(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources"].append(dict(manifest["sources"][0]))
    manifest["source_count"] = 2
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(engine.ArchiveRepairError, match="exactly one"):
        build(repo, sources, manifest_path, paths, "metadata")


def test_manifest_and_source_host_must_agree(tmp_path: Path) -> None:
    repo, sources, manifest_path, paths = archive_repo(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources"][0]["host_slug"] = "dialogue-works"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(engine.ArchiveRepairError, match="host routes disagree"):
        build(repo, sources, manifest_path, paths, "metadata")


def test_metadata_class_changes_frontmatter_only(tmp_path: Path) -> None:
    repo, sources, manifest, paths = archive_repo(
        tmp_path,
        extra="transcript_curation: curated_sectioned\nsection_count: 9\n",
    )
    plan = build(repo, sources, manifest, paths, "metadata")
    item = plan.files[0]
    original_body = item.original_bytes.split(b"## Transcript", 1)[1]
    proposed_body = item.proposed_bytes.split(b"## Transcript", 1)[1]
    assert original_body == proposed_body
    assert set(item.changed_fields) == {
        "asr_disposition",
        "quotation_readiness",
        "quotation_readiness_reason",
        "section_count",
        "sectioning_disposition",
        "sectioning_reason",
        "speaker_attribution",
        "speaker_attribution_reason",
        "transcript_curation",
    }
    assert item.operations == (
        "metadata-normalization",
        "processing-disposition-reconciliation",
    )
    assert "asr_disposition: needs-repair" in item.proposed_bytes.decode("utf-8")
    assert "sectioning_disposition: preserved-unsectioned" in item.proposed_bytes.decode("utf-8")
    assert item.public()["processing_evidence"][0]["field"] == "asr_disposition"


def test_metadata_derives_evidence_bounded_processing_without_body_changes(tmp_path: Path) -> None:
    body = ">> First turn.\n\n>> Second turn.\n"
    extra = (
        "asr_repair_applied: true\n"
        'asr_repair_pass: "2026-07-09 asr-repair-v1"\n'
    )
    repo, sources, manifest, paths = archive_repo(tmp_path, body=body, extra=extra)
    plan = build(repo, sources, manifest, paths, "metadata")
    item = plan.files[0]
    proposed = item.proposed_bytes.decode("utf-8")
    assert item.original_bytes.split(b"## Transcript", 1)[1] == item.proposed_bytes.split(b"## Transcript", 1)[1]
    assert "asr_disposition: repaired" in proposed
    assert "speaker_attribution: turn-labeled" in proposed
    assert "sectioning_disposition: preserved-unsectioned" in proposed
    assert "quotation_readiness: restricted" in proposed


def test_source_scoped_metadata_review_is_identity_and_host_bounded(
    tmp_path: Path,
) -> None:
    identity = "youtube:reviewed-metadata"
    extra = (
        f'source_identity: "{identity}"\n'
        "source_form: monologue\n"
        "host: Example Speaker\n"
        "asr_repair_applied: true\n"
        'asr_repair_pass: "reviewed-pass"\n'
    )
    repo, sources, manifest, paths = archive_repo(
        tmp_path,
        host="example-channel",
        body="A reviewed solo statement.\n",
        extra=extra,
        source_identity=identity,
    )
    review = {
        "host_slug": "example-channel",
        "requires": {
            "source_form": "monologue",
            "host": "Example Speaker",
        },
        "updates": {
            "channel_name": "Example Channel",
            "speaker_attribution": "confirmed-solo",
            "speaker_attribution_reason": "Reviewed exact-source solo attribution.",
        },
    }
    engine.SOURCE_METADATA_REVIEWS[identity] = review
    try:
        plan = build(repo, sources, manifest, paths, "metadata")
        proposed = plan.files[0].proposed_bytes.decode("utf-8")
        assert 'channel_name: "Example Channel"' in proposed
        assert "speaker_attribution: confirmed-solo" in proposed
        assert "source-scoped-metadata-review" in plan.files[0].operations

        review["host_slug"] = "different-channel"
        with pytest.raises(engine.ArchiveRepairError, match="host drift"):
            build(repo, sources, manifest, paths, "metadata")
    finally:
        del engine.SOURCE_METADATA_REVIEWS[identity]


def test_source_scoped_section_recipe_preserves_wording_and_rejects_drift(
    tmp_path: Path,
) -> None:
    identity = "youtube:reviewed-sectioning"
    body = "Opening anchor and context.\nSecond anchor and analysis.\n"
    extra = f'source_identity: "{identity}"\n'
    repo, sources, manifest, paths = archive_repo(
        tmp_path,
        host="alexander-mercouris",
        body=body,
        extra=extra,
        source_identity=identity,
    )
    engine.SOURCE_SECTION_RECIPES[identity] = (
        ("Opening", "Opening anchor"),
        ("Analysis", "Second anchor"),
    )
    try:
        plan = build(repo, sources, manifest, paths, "sectioning")
        original = plan.files[0].original_bytes.decode("utf-8").split("## Transcript", 1)[1]
        proposed = plan.files[0].proposed_bytes.decode("utf-8").split("## Transcript", 1)[1]
        assert engine.wording_tokens(original) == engine.wording_tokens(proposed)
        assert proposed.count("### ") == 2
        assert plan.files[0].operations[0] == "source-scoped-sectioning"

        engine.SOURCE_SECTION_RECIPES[identity] = (("Missing", "absent anchor"),)
        with pytest.raises(engine.ArchiveRepairError, match="anchor count mismatch"):
            build(repo, sources, manifest, paths, "sectioning")
    finally:
        del engine.SOURCE_SECTION_RECIPES[identity]


@pytest.mark.parametrize(
    ("extra", "body", "message"),
    [
        ("asr_disposition: repaired\n", "Body.\n", "repair-pass provenance"),
        ("speaker_attribution: turn-labeled\n", ">> One turn.\n", "turn markers"),
        ("sectioning_disposition: sectioned\n", "Body.\n", "transcript headings"),
    ],
)
def test_metadata_rejects_detectable_processing_contradictions(
    tmp_path: Path, extra: str, body: str, message: str
) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path, body=body, extra=extra)
    with pytest.raises(engine.ArchiveRepairError, match=message):
        build(repo, sources, manifest, paths, "metadata")


def test_metadata_rejects_ready_quotation_with_unresolved_processing(tmp_path: Path) -> None:
    repo, sources, manifest, paths = archive_repo(
        tmp_path,
        extra="quotation_readiness: ready\n",
    )
    with pytest.raises(engine.ArchiveRepairError, match="quotation_readiness ready"):
        build(repo, sources, manifest, paths, "metadata")


def test_asr_class_preserves_layout_and_does_not_section_or_trim(tmp_path: Path) -> None:
    body = "The straight of hormones stayed broken in Anchora.\n\n\nSecond paragraph remains.\n"
    repo, sources, manifest, paths = archive_repo(tmp_path, body=body)
    plan = build(repo, sources, manifest, paths, "asr")
    proposed = plan.files[0].proposed_bytes.decode("utf-8")
    assert "Strait of Hormuz" in proposed
    assert "\n\n\nSecond paragraph" in proposed
    assert "### " not in proposed
    assert plan.files[0].operations == ("asr-repair",)
    assert set(plan.files[0].changed_fields) <= {
        "asr_repair_applied",
        "asr_repair_pass",
        *engine.land_best_intake.PROCESSING_FIELD_ORDER,
    }
    assert plan.files[0].public()["processing_evidence"][0]["disposition"] == "repaired"


def test_asr_rejects_unapproved_host(tmp_path: Path) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path, host="neutrality-studies")
    with pytest.raises(engine.ArchiveRepairError, match="not approved"):
        build(repo, sources, manifest, paths, "asr")


def test_source_scoped_asr_repairs_unapproved_host_without_global_rules(tmp_path: Path) -> None:
    identity = "youtube:test-source-scoped"
    body = "theou and the straight of Hormones remain distinct.\n"
    extra = f'source_identity: "{identity}"\n'
    repo, sources, manifest, paths = archive_repo(
        tmp_path,
        host="the-duran",
        body=body,
        extra=extra,
        source_identity=identity,
    )
    rules = ((r"\btheou\b", "the MOU", 1),)
    engine.land_best_intake.SOURCE_ASR_REPAIRS[identity] = rules
    try:
        plan = build(repo, sources, manifest, paths, "asr")
    finally:
        del engine.land_best_intake.SOURCE_ASR_REPAIRS[identity]
    item = plan.files[0]
    proposed = item.proposed_bytes.decode("utf-8")
    assert "the MOU" in proposed
    assert "straight of Hormones" in proposed
    assert item.operations == ("asr-repair-source-scoped-partial",)
    assert item.asr_rule_applications == ((r"\btheou\b", "the MOU", 1),)
    assert "asr_disposition: needs-repair" in proposed
    assert "quotation_readiness: not-ready" in proposed
    assert item.public()["asr_rule_applications"] == [
        {"pattern": r"\btheou\b", "replacement": "the MOU", "count": 1}
    ]


def test_source_scoped_asr_rejects_identity_or_count_drift(tmp_path: Path) -> None:
    identity = "youtube:test-source-scoped-drift"
    rules = ((r"\btheou\b", "the MOU", 2),)
    engine.land_best_intake.SOURCE_ASR_REPAIRS[identity] = rules
    try:
        repo, sources, manifest, paths = archive_repo(
            tmp_path,
            host="the-duran",
            body="theou appears once.\n",
            extra=f'source_identity: "{identity}"\n',
            source_identity=identity,
        )
        with pytest.raises(engine.ArchiveRepairError, match="count mismatch"):
            build(repo, sources, manifest, paths, "asr")

        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
        manifest_payload["sources"][0]["source_identity"] = identity
        manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
        target = repo / paths[0]
        target.write_text(
            source_text(
                host="the-duran",
                body="theou appears twice: theou.\n",
                extra='source_identity: "youtube:different"\n',
            ),
            encoding="utf-8",
            newline="\n",
        )
        with pytest.raises(engine.ArchiveRepairError, match="identities disagree"):
            build(repo, sources, manifest, paths, "asr")
    finally:
        del engine.land_best_intake.SOURCE_ASR_REPAIRS[identity]


def test_wrapper_trim_is_its_own_class(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path)
    monkeypatch.setitem(engine.land_best_intake.HOST_TRIM_RULES, "daniel-davis", object())

    def trim(args, body):
        args.opening_trim_applied = True
        args.opening_trim_rule = "test-rule"
        args.opening_trim_chars_saved = 6
        args.opening_trim_words_saved = 1
        return body.removeprefix("The ")

    monkeypatch.setattr(engine.land_best_intake, "apply_trim_metadata", trim)
    plan = build(repo, sources, manifest, paths, "wrapper-trim")
    assert plan.files[0].operations == ("wrapper-trim",)
    assert "opening_trim_rule" in plan.files[0].changed_fields


def test_sectioning_preserves_transcript_word_order(tmp_path: Path) -> None:
    body = (
        "Hi everybody. Today we have to talk about the White House terms for Iran and the shipping crisis in Hormuz.\n\n"
        "I want to ask first about the White House offer and whether Tehran sees it as coercive diplomacy.\n\n"
        "Another point is the regional shipping lane, insurance costs, and whether the blockade threat is credible.\n"
    )
    repo, sources, manifest, paths = archive_repo(tmp_path, host="dialogue-works", body=body)
    plan = build(repo, sources, manifest, paths, "sectioning")
    original = plan.files[0].original_bytes.decode("utf-8").split("## Transcript", 1)[1]
    proposed = plan.files[0].proposed_bytes.decode("utf-8").split("## Transcript", 1)[1]
    assert engine.wording_tokens(original) == engine.wording_tokens(proposed)
    assert plan.files[0].section_count_after >= 2
    assert "sectioning_disposition: sectioned" in plan.files[0].proposed_bytes.decode("utf-8")
    assert plan.files[0].operations[-1] == "processing-disposition-reconciliation"
    section_evidence = next(
        item
        for item in plan.files[0].public()["processing_evidence"]
        if item["field"] == "sectioning_disposition"
    )
    assert section_evidence["disposition"] == "sectioned"


def test_resection_is_valid_only_for_sectioning(tmp_path: Path) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path)
    with pytest.raises(engine.ArchiveRepairError, match="only for"):
        build(repo, sources, manifest, paths, "asr", resection=True)


def test_plan_order_and_digest_are_deterministic(tmp_path: Path) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path, second=True)
    first = build(repo, sources, manifest, list(reversed(paths)), "metadata")
    second = build(repo, sources, manifest, paths, "metadata")
    assert first.plan_digest == second.plan_digest
    assert [item.path for item in first.files] == sorted(paths)


def test_apply_rejects_wrong_digest_manifest_drift_and_input_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path)
    plan = build(repo, sources, manifest, paths, "metadata")
    monkeypatch.setattr(engine, "dirty_paths", lambda *args, **kwargs: set())
    with pytest.raises(engine.ArchiveRepairError, match="digest"):
        engine.apply_plan(plan, expected_digest="bad", repo_root=repo, manifest_path=manifest)
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(engine.ArchiveRepairError, match="manifest changed"):
        engine.apply_plan(plan, expected_digest=plan.plan_digest, repo_root=repo, manifest_path=manifest)

    repo, sources, manifest, paths = archive_repo(tmp_path / "fresh")
    plan = build(repo, sources, manifest, paths, "metadata")
    monkeypatch.setattr(engine, "dirty_paths", lambda *args, **kwargs: set())
    target = repo / paths[0]
    target.write_text(target.read_text(encoding="utf-8") + "drift", encoding="utf-8")
    with pytest.raises(engine.ArchiveRepairError, match="target changed"):
        engine.apply_plan(plan, expected_digest=plan.plan_digest, repo_root=repo, manifest_path=manifest)


def test_apply_rejects_dirty_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path)
    plan = build(repo, sources, manifest, paths, "metadata")
    monkeypatch.setattr(engine, "dirty_paths", lambda *args, **kwargs: {paths[0]})
    with pytest.raises(engine.ArchiveRepairError, match="already dirty"):
        engine.apply_plan(plan, expected_digest=plan.plan_digest, repo_root=repo, manifest_path=manifest)


def test_apply_writes_exact_planned_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path)
    plan = build(repo, sources, manifest, paths, "metadata")
    monkeypatch.setattr(engine, "dirty_paths", lambda *args, **kwargs: set())
    payload = engine.apply_plan(
        plan,
        expected_digest=plan.plan_digest,
        repo_root=repo,
        manifest_path=manifest,
    )
    assert payload["disposition"] == "executed"
    assert (repo / paths[0]).read_bytes() == plan.files[0].proposed_bytes


def test_apply_rolls_back_prior_writes_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path, second=True)
    plan = build(repo, sources, manifest, paths, "metadata")
    monkeypatch.setattr(engine, "dirty_paths", lambda *args, **kwargs: set())
    original_replace = engine._atomic_replace
    calls = 0

    def fail_second_write(path: Path, payload: bytes) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated write failure")
        original_replace(path, payload)

    monkeypatch.setattr(engine, "_atomic_replace", fail_second_write)
    with pytest.raises(engine.ArchiveRepairError, match="rolled back"):
        engine.apply_plan(
            plan,
            expected_digest=plan.plan_digest,
            repo_root=repo,
            manifest_path=manifest,
        )
    for item in plan.files:
        assert (repo / item.path).read_bytes() == item.original_bytes


def test_dry_run_plan_never_writes(tmp_path: Path) -> None:
    repo, sources, manifest, paths = archive_repo(tmp_path)
    target = repo / paths[0]
    before = (target.read_bytes(), target.stat().st_mtime_ns)
    plan = build(repo, sources, manifest, paths, "metadata")
    assert (target.read_bytes(), target.stat().st_mtime_ns) == before
    assert plan.public()["authority_effect"] == "none"
    assert plan.public()["capability_token"] is False
