from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "land_best_intake.py"
REPORT_PATH = REPO_ROOT / "scripts" / "report_trim_stats.py"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


land_best_intake = load_module("land_best_intake", SCRIPT_PATH)
report_trim_stats = load_module("report_trim_stats", REPORT_PATH)


def trim_args(host_slug: str | None, mode: str = "auto") -> SimpleNamespace:
    return SimpleNamespace(
        host_slug=host_slug,
        trim_opening=mode,
        asr_repair="auto",
        asr_repair_applied=False,
        asr_repair_pass="",
        sectioning="auto",
        title="Example Title",
        source_form="interview",
    )


def make_local_temp_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="mira-core-trim-"))


def build_fast_args(pub_date: str, url: str, title: str, body_text: str) -> SimpleNamespace:
    return SimpleNamespace(
        pub_date=pub_date,
        ingest_date=pub_date,
        title=title,
        url=url,
        body_file="",
        body_text=body_text,
        voice_slugs=[],
        host_slug=None,
        host="",
        guest="",
        host_people=[],
        guest_people=[],
        show_title="",
        channel_name="",
        show="",
        thread=None,
        kind="cleaned-transcript",
        source_form="interview",
        source_class="guest interview pressure test",
        modality="cleaned-transcript",
        review_state="unreviewed",
        routing_state="provisional",
        source_note="",
        editorial_note="Preserve as raw cleaned transcript. Not human-verified verbatim.",
        upstream_path=None,
        dry_run=True,
        trim_opening="auto",
        asr_repair="auto",
        sectioning="auto",
        opening_trim_applied=False,
        opening_trim_rule="",
        opening_trim_chars_saved=0,
        opening_trim_words_saved=0,
        closing_trim_applied=False,
        closing_trim_rule="",
        closing_trim_chars_saved=0,
        closing_trim_words_saved=0,
        transcript_curation="preserved_unsectioned",
        section_count=0,
        section_pass=land_best_intake.SECTIONING_PASS_LABEL,
        asr_repair_applied=False,
        asr_repair_pass="",
    )


def configure_transaction_root(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    archive = tmp_path / "archive" / "sources" / "geopolitics"
    sources = archive / "sources"
    sources.mkdir(parents=True)
    manifest_path = archive / "source-manifest.json"
    manifest_path.write_text('{"source_count": 0, "sources": []}\n', encoding="utf-8")
    monkeypatch.setattr(land_best_intake, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(land_best_intake, "NG_ROOT", tmp_path / "narrative-geopolitics")
    monkeypatch.setattr(land_best_intake, "ARCHIVE_ROOT", archive)
    monkeypatch.setattr(land_best_intake, "ARCHIVE_SOURCES_ROOT", sources)
    monkeypatch.setattr(land_best_intake, "MANIFEST_PATH", manifest_path)
    return sources, manifest_path


def transaction_args(pub_date: str, title: str, url: str = "https://example.com") -> SimpleNamespace:
    args = build_fast_args(pub_date, url, title, "Material source body.\n")
    args.host_slug = "audit-host"
    args.voice_slugs = ["audit-voice"]
    return land_best_intake.normalize_args(args)


def documented_hosts(text: str, label: str) -> set[str]:
    lines = text.splitlines()
    start = lines.index(label) + 1
    values: set[str] = set()
    for line in lines[start:]:
        if line.startswith("- `") and line.endswith("`"):
            values.add(line[3:-1])
        elif values and line.strip():
            break
    return values


def test_mario_opening_trim_applies_before_substance() -> None:
    body = "Hey guys thanks for waiting.\nSo just to kind of recap for the audience Iran struck ships.\n"

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_opening(
        trim_args("mario-nawfal"),
        body,
    )

    assert applied is True
    assert rule == "mario-nawfal-v1"
    assert trimmed.startswith("So just to kind of recap for the audience")
    assert chars_saved == len("Hey guys thanks for waiting.\n")
    assert words_saved == land_best_intake.count_words("Hey guys thanks for waiting.\n")


def test_mario_opening_marker_at_position_zero_does_not_trim() -> None:
    body = "So just to kind of recap for the audience Iran struck ships.\n"

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_opening(
        trim_args("mario-nawfal"),
        body,
    )

    assert trimmed == body
    assert applied is False
    assert rule == ""
    assert chars_saved == 0
    assert words_saved == 0


def test_daniel_davis_closing_trim_uses_earliest_marker() -> None:
    body = (
        "Substantive ending.\n"
        "And uh we will be back in about 1 hour.\n"
        "You know we don't have sponsors cuz we hate to hit you over the head with ads.\n"
    )

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_closing(
        trim_args("daniel-davis"),
        body,
    )

    removed = (
        "And uh we will be back in about 1 hour.\n"
        "You know we don't have sponsors cuz we hate to hit you over the head with ads.\n"
    )
    assert applied is True
    assert rule == "daniel-davis-closing-v1"
    assert trimmed == "Substantive ending.\n"
    assert chars_saved == len(removed)
    assert words_saved == land_best_intake.count_words(removed)


def test_daniel_davis_closing_trim_cuts_at_next_episode_marker() -> None:
    body = (
        "Substantive ending.\n"
        "We'll see you on the next episode of the Daniel Davis deep dive.\n"
        "You know, I don't try to talk you into buying gold or tell you how to run your stock portfolio, but there is a way you can help us.\n"
    )

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_closing(
        trim_args("daniel-davis"),
        body,
    )

    removed = (
        "We'll see you on the next episode of the Daniel Davis deep dive.\n"
        "You know, I don't try to talk you into buying gold or tell you how to run your stock portfolio, but there is a way you can help us.\n"
    )
    assert applied is True
    assert rule == "daniel-davis-closing-v1"
    assert trimmed == "Substantive ending.\n"
    assert chars_saved == len(removed)
    assert words_saved == land_best_intake.count_words(removed)


def test_mercouris_opening_snippet_trim_removes_subscribe_sentence_only() -> None:
    body = (
        "Good day. Today is Monday, 1st June 2026. "
        "And before I proceed with this program, let me remind you again to tick the like button "
        "and to check your subscription to this channel. "
        "Well, today we continue to have the two ongoing conflicts.\n"
    )

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_opening(
        trim_args("alexander-mercouris"),
        body,
    )

    removed = (
        " And before I proceed with this program, let me remind you again to tick the like button "
        "and to check your subscription to this channel. "
    )
    assert applied is True
    assert rule == "alexander-mercouris-v1"
    assert trimmed == "Good day. Today is Monday, 1st June 2026. Well, today we continue to have the two ongoing conflicts.\n"
    assert chars_saved == len(removed)
    assert words_saved == land_best_intake.count_words(removed)


def test_mercouris_closing_trim_cuts_at_close_heading() -> None:
    body = (
        "Substantive ending.\n"
        "\n"
        "### Close - Platforms And Subscribe\n"
        "\n"
        "Anyway, this is where I'm going to finish today's program.\n"
    )

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_closing(
        trim_args("alexander-mercouris"),
        body,
    )

    removed = (
        "\n### Close - Platforms And Subscribe\n"
        "\n"
        "Anyway, this is where I'm going to finish today's program.\n"
    )
    assert applied is True
    assert rule == "alexander-mercouris-v1"
    assert trimmed == "Substantive ending.\n"
    assert chars_saved == len(removed)
    assert words_saved == land_best_intake.count_words(removed)


def test_mercouris_closing_trim_cuts_at_i_am_finish_variant() -> None:
    body = (
        "Substantive ending.\n"
        "Anyway, this is where I am going to finish today's program.\n"
        "Let me remind you again that you can find all our programs on our various platforms.\n"
    )

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_closing(
        trim_args("alexander-mercouris"),
        body,
    )

    removed = (
        "Anyway, this is where I am going to finish today's program.\n"
        "Let me remind you again that you can find all our programs on our various platforms.\n"
    )
    assert applied is True
    assert rule == "alexander-mercouris-v1"
    assert trimmed == "Substantive ending.\n"
    assert chars_saved == len(removed)
    assert words_saved == land_best_intake.count_words(removed)


def test_dialogue_works_opening_trim_removes_youtube_transcript_wrapper() -> None:
    body = (
        "Larry Johnson: Iran Strikes US Bases in Bahrain & Kuwait After US Strikes South Iran - Hormuz CLOSED - YouTube\n"
        "\n"
        "Transcripts:\n"
        "Hi everybody. Today's Wednesday, July 8th, 2026.\n"
    )

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_opening(
        trim_args("dialogue-works"),
        body,
    )

    removed = (
        "Larry Johnson: Iran Strikes US Bases in Bahrain & Kuwait After US Strikes South Iran - Hormuz CLOSED - YouTube\n"
        "\n"
        "Transcripts:\n"
    )
    assert applied is True
    assert rule == "dialogue-works-wrapper-v1"
    assert trimmed == "Hi everybody. Today's Wednesday, July 8th, 2026.\n"
    assert chars_saved == len(removed)
    assert words_saved == land_best_intake.count_words(removed)


def test_dialogue_works_opening_trim_leaves_plain_transcript_alone() -> None:
    body = "Hi everybody. Today's Wednesday, July 8th, 2026.\n"

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_opening(
        trim_args("dialogue-works"),
        body,
    )

    assert trimmed == body
    assert applied is False
    assert rule == ""
    assert chars_saved == 0
    assert words_saved == 0


def test_moral_resistance_opening_trim_removes_youtube_transcript_wrapper() -> None:
    body = (
        "PROFESSOR MARANDI: GROUND INVASION COMING - YouTube\n"
        "\n"
        "Transcripts:\n"
        "And we are live with Professor Marandi.\n"
    )

    trimmed, applied, rule, chars_saved, words_saved = land_best_intake.maybe_trim_opening(
        trim_args("moral-resistance"),
        body,
    )

    removed = (
        "PROFESSOR MARANDI: GROUND INVASION COMING - YouTube\n"
        "\n"
        "Transcripts:\n"
    )
    assert applied is True
    assert rule == "moral-resistance-wrapper-v1"
    assert trimmed == "And we are live with Professor Marandi.\n"
    assert chars_saved == len(removed)
    assert words_saved == land_best_intake.count_words(removed)


def test_none_mode_disables_all_trimming() -> None:
    body = (
        "noise\nSo just to kind of recap for the audience test.\n"
        "And uh we will be back in about 1 hour.\n"
    )
    args = trim_args("mario-nawfal", mode="none")

    opening = land_best_intake.maybe_trim_opening(args, body)
    closing = land_best_intake.maybe_trim_closing(args, body)

    assert opening == (body, False, "", 0, 0)
    assert closing == (body, False, "", 0, 0)


def test_unapproved_host_is_left_unchanged_in_auto_mode() -> None:
    body = "Oh, I can't hear you, by the way.\nHi everybody.\n"

    opening = land_best_intake.maybe_trim_opening(trim_args("glenn-diesen"), body)
    closing = land_best_intake.maybe_trim_closing(trim_args("glenn-diesen"), body)

    assert opening == (body, False, "", 0, 0)
    assert closing == (body, False, "", 0, 0)


def test_frontmatter_includes_rule_and_metric_fields() -> None:
    args = SimpleNamespace(
        ingest_date="2026-07-08",
        pub_date="2026-07-07",
        kind="cleaned-transcript",
        source_form="interview",
        host_people=["Mario Nawfal"],
        guest_people=["Brandon Weichert"],
        show_title="Mario Nawfal",
        channel_name="Mario Nawfal",
        show="Mario Nawfal",
        host="Mario Nawfal",
        guest="Brandon Weichert",
        thread="weichert",
        voice_slugs=["weichert"],
        url="https://example.com",
        source_note="note",
        editorial_note="note",
        review_state="unreviewed",
        routing_state="provisional",
        opening_trim_applied=True,
        opening_trim_rule="mario-nawfal-v1",
        opening_trim_chars_saved=25,
        opening_trim_words_saved=5,
        closing_trim_applied=True,
        closing_trim_rule="mario-nawfal-v1",
        closing_trim_chars_saved=50,
        closing_trim_words_saved=10,
        transcript_curation="curated_sectioned",
        section_count=3,
        section_pass="2026-07-09 semantic-section-v1",
        title="Example Title",
    )

    doc = land_best_intake.build_frontmatter(args, "transcript-example", "Body\n")

    assert 'opening_trim_rule: "mario-nawfal-v1"' in doc
    assert "opening_trim_chars_saved: 25" in doc
    assert 'closing_trim_rule: "mario-nawfal-v1"' in doc
    assert "closing_trim_words_saved: 10" in doc
    assert "transcript_curation: curated_sectioned" in doc
    assert "section_count: 3" in doc
    assert 'source_url: "https://example.com"' in doc
    assert "source_url_status: provided" in doc

    args.url = ""
    unavailable = land_best_intake.build_frontmatter(
        args, "transcript-example", "Body\n"
    )
    assert 'source_url: ""' in unavailable
    assert "source_url_status: unavailable" in unavailable


def stale_section_transcript_creates_show_open_and_segments_for_clear_dialogue_works_shape() -> None:
    body = (
        "Hi everybody. Today we have to talk about the White House terms for Iran and the shipping crisis in Hormuz.\n\n"
        "I want to ask first about the White House offer and whether Tehran sees it as coercive diplomacy.\n\n"
        "Another point is the regional shipping lane, insurance costs, and whether the blockade threat is credible.\n"
    )

    rewritten, curation, section_count, skip_reason = land_best_intake.section_transcript(
        trim_args("dialogue-works"),
        body,
    )

    assert curation == "curated_sectioned"
    assert section_count >= 2
    assert skip_reason == ""
    assert rewritten.startswith("### Show Open — ")
    assert "\n### Segment 2 — " in rewritten
    assert "White House" in rewritten or "Shipping" in rewritten


def test_derive_topic_label_prefers_domain_topics_over_asr_surface_noise() -> None:
    block = (
        "policy for even a 15minute span. So all of this is to say it is perfectly plain why Iran would say what are we even talking about? "
        "But I would say we don't have to be completely pessimistic about it because there's a better alternative than a negotiated agreement and that is the United States should just stop what it's doing and go home. "
        "If the US goes home, Iran is going to open the straight of Hormuz and there's going to be some normalization of the world energy markets."
    )

    label = land_best_intake.derive_topic_label(block, "Prof. Jeffrey Sachs : How the Best Military and Intel Failed")

    assert label
    assert "Policy For Even" not in label
    assert "Iran" in label or "Hormuz" in label or "US" in label


def test_derive_topic_label_prefers_structural_phrases_like_white_house() -> None:
    block = (
        "I want to ask first about the White House offer and whether Tehran sees it as coercive diplomacy. "
        "Another point is the regional shipping lane, insurance costs, and whether the blockade threat is credible."
    )

    label = land_best_intake.derive_topic_label(block, "Example Dialogue Works Source")

    assert label
    assert "White House" in label or "Shipping Lane" in label


def test_derive_topic_label_filters_low_signal_asr_noise_tokens() -> None:
    block = (
        "These big questions are what the president keeps saying. "
        "Meanwhile Iran and Hormuz remain the substantive issue. "
        "Iran still holds leverage over Hormuz and shipping."
    )

    label = land_best_intake.derive_topic_label(block, "Example Source")

    assert label
    assert "These" not in label
    assert "Big" not in label
    assert "Questions" not in label
    assert "President" not in label
    assert "Iran" in label or "Hormuz" in label


def test_cleanup_section_label_drops_trailing_noise_words() -> None:
    label = land_best_intake.cleanup_section_label("Israel Big Questions It's")

    assert label == "Israel"


def test_derive_topic_label_does_not_promote_title_flavored_singletons() -> None:
    block = (
        "The president has to hear more than one perspective. "
        "Iran and Israel remain the real issue. "
        "Iran is central here and Israel keeps driving escalation. "
        "The Strait of Hormuz remains part of the pressure story."
    )

    label = land_best_intake.derive_topic_label(block, "Iran Trump Russia Hear")

    assert label
    assert "Hear" not in label
    assert "Iran" in label


def test_derive_topic_label_prefers_multiword_domain_phrases_when_available() -> None:
    block = (
        "The strategic petroleum reserve is being drained while fertilizer costs rise. "
        "The American people will feel the pressure if energy markets tighten further. "
        "That is the real economic risk in this war."
    )

    label = land_best_intake.derive_topic_label(block, "Example Source")

    assert label
    assert "Strategic Petroleum Reserve" in label or "American People" in label or "Fertilizer" in label


def test_derive_topic_label_prefers_missile_city_cluster_over_noise_tokens() -> None:
    block = (
        "Iran's missile cities and missile factories remain intact. "
        "The IRGC can reopen tunnel access with bulldozers and mountain ranges still protect the sites. "
        "That is why the strike campaign failed."
    )

    label = land_best_intake.derive_topic_label(block, "Example Source")

    assert label
    assert "Missile Cities" in label or "Missile Factories" in label or "IRGC" in label


def test_section_transcript_skips_when_cues_are_weak() -> None:
    body = (
        "This is one long transcript paragraph about events.\n\n"
        "It continues in roughly the same register without a strong pivot.\n\n"
        "Nothing here clearly marks a section transition or semantic turn.\n"
    )

    rewritten, curation, section_count, skip_reason = land_best_intake.section_transcript(
        trim_args("glenn-diesen"),
        body,
    )

    assert rewritten == body
    assert curation == "preserved_unsectioned"
    assert section_count == 0
    assert skip_reason in {"weak-cues", "unclean-open-label", "unclean-segment-label"}


def test_section_transcript_respects_none_mode() -> None:
    args = trim_args("dialogue-works")
    args.sectioning = "none"
    body = "Hi everybody.\n\nI want to ask about Iran.\n\nAnother point is Russia.\n"

    rewritten, curation, section_count, skip_reason = land_best_intake.section_transcript(args, body)

    assert rewritten == body
    assert curation == "preserved_unsectioned"
    assert section_count == 0
    assert skip_reason == "disabled"


def test_update_editorial_note_appends_section_pass_suffix() -> None:
    updated = land_best_intake.update_editorial_note(
        "Preserve as raw cleaned transcript. Not human-verified verbatim.",
        "curated_sectioned",
        4,
    )

    assert "source-section pass 2026-07-09 (4 sections)." in updated


def test_report_frontmatter_parser_extracts_generated_fields() -> None:
    text = (
        "---\n"
        'host_slug: "daniel-davis"\n'
        "opening_trim_applied: false\n"
        "opening_trim_chars_saved: 0\n"
        "closing_trim_applied: true\n"
        "closing_trim_chars_saved: 120\n"
        "---\n"
        "# Example\n"
        "\n"
        "## Transcript\n"
        "\n"
        "Body\n"
    )

    parsed = report_trim_stats.parse_frontmatter(text)

    assert parsed["host_slug"] == "daniel-davis"
    assert parsed["closing_trim_applied"] == "true"
    assert parsed["closing_trim_chars_saved"] == "120"


def test_retrofit_source_trims_body_and_normalizes_metadata() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: daniel-davis\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "Substantive ending.\n"
            "And uh we will be back in about 1 hour.\n"
            "You know we don't have sponsors cuz we hate to hit you over the head with ads.\n",
            encoding="utf-8",
        )

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert result is not None
        assert result.startswith("TRIMMED")
        assert "closing_trim_applied: true" in text
        assert 'closing_trim_rule: "daniel-davis-closing-v1"' in text
        assert "And uh we will be back in about 1 hour." not in text
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_normalizes_without_trimming() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: daniel-davis\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "Fully substantive ending only.\n",
            encoding="utf-8",
        )

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        expected_rel = source.as_posix()
        assert result == f"NORMALIZED {expected_rel}"
        assert "opening_trim_applied: false" in text
        assert 'opening_trim_rule: ""' in text
        assert "closing_trim_applied: false" in text
        assert "transcript_curation: preserved_unsectioned" in text
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_normalizes_dialogue_works_without_wrapper_trim() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        original = (
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: dialogue-works\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "Oh, I can't hear you, by the way.\n"
        )
        source.write_text(original, encoding="utf-8")

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        expected_rel = source.as_posix()
        assert result == f"NORMALIZED {expected_rel}"
        assert "Oh, I can't hear you, by the way.\n" in text
        assert "opening_trim_applied: false" in text
        assert "closing_trim_applied: false" in text
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_uses_channel_slug_for_mercouris() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-06-10\n"
            "channel_slug: alexander-mercouris\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "Good day. Today is Wednesday 10th June 2026. "
            "And before I proceed with this program, let me remind you again to tick the like button "
            "and to check your subscription to this channel. "
            "Main body.\n"
            "\n"
            "### Close - Platforms And Subscribe\n"
            "\n"
            "Anyway, this is where I'm going to finish today's program.\n",
            encoding="utf-8",
        )

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert result is not None
        assert result.startswith("TRIMMED")
        assert 'opening_trim_rule: "alexander-mercouris-v1"' in text
        assert 'closing_trim_rule: "alexander-mercouris-v1"' in text
        assert "tick the like button" not in text
        assert "### Close - Platforms And Subscribe" not in text
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_uses_filename_fallback_for_mercouris() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-alexander-mercouris-example-2026-06-11.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-06-11\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "Good day. Today is Wednesday 11th June 2026. "
            "And before I proceed with this program, let me remind you again to tick the like button "
            "and to check your subscription to this channel. "
            "Main body.\n"
            "\n"
            "Let me remind you again, you can find all our programs on our various platforms, Locals, Rumble, X, and Substack.\n",
            encoding="utf-8",
        )

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert result is not None
        assert result.startswith("TRIMMED")
        assert 'opening_trim_rule: "alexander-mercouris-v1"' in text
        assert 'closing_trim_rule: "alexander-mercouris-v1"' in text
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_sections_clear_eligible_transcript() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: dialogue-works\n"
            "title: Example Dialogue Works Source\n"
            "source_form: interview\n"
            "editorial_note: Preserve as raw cleaned transcript. Not human-verified verbatim.\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "Hi everybody. Today we are looking at White House demands on Iran and the Hormuz crisis.\n"
            "\n"
            "I want to ask about the White House position and whether it can force Tehran into concessions.\n"
            "\n"
            "Another point is the shipping lane, insurance markets, and whether closure pressure can hold.\n",
            encoding="utf-8",
        )

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert result is not None
        assert result.startswith("TRIMMED")
        assert "transcript_curation: curated_sectioned" in text
        assert "section_count: 2" in text or "section_count: 3" in text
        assert "### Show Open — " in text
        assert "source-section pass 2026-07-09" in text
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_sectioning_is_idempotent() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: dialogue-works\n"
            "title: Example Dialogue Works Source\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n\n"
            "## Transcript\n\n"
            "Hi everybody. Today we are looking at White House demands on Iran and the Hormuz crisis.\n\n"
            "I want to ask first about the White House offer and whether Tehran sees it as coercive diplomacy.\n\n"
            "Another point is the regional shipping lane, insurance costs, and whether the blockade threat is credible.\n",
            encoding="utf-8",
        )

        first = land_best_intake.retrofit_source(
            source, "2026-06-01", force_sections=True
        )
        first_text = source.read_text(encoding="utf-8")
        second = land_best_intake.retrofit_source(
            source, "2026-06-01", force_sections=True
        )
        second_text = source.read_text(encoding="utf-8")

        assert first is not None and first.startswith("TRIMMED")
        assert second is not None
        assert second.startswith("UNCHANGED") or second.startswith("NORMALIZED")
        assert second_text == first_text
        assert second_text.count("### ") == 3
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_preserves_existing_sectioned_body_without_force() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        original = (
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: dialogue-works\n"
            "transcript_curation: curated_sectioned\n"
            "section_count: 2\n"
            "section_pass: \"2026-07-01 semantic-section-v1\"\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "### Show Open — Existing\n"
            "\n"
            "Already sectioned block.\n"
            "\n"
            "### Segment 2 — Existing Turn\n"
            "\n"
            "Second block.\n"
        )
        source.write_text(original, encoding="utf-8")

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert result is not None
        assert result.startswith("NORMALIZED") or result.startswith("UNCHANGED")
        assert "### Show Open — Existing" in text
        assert text.count("### ") == 2
    finally:
        shutil.rmtree(tmp_dir)


def test_section_transcript_creates_show_open_and_segments_for_clear_dialogue_works_shape() -> None:
    body = (
        "Hi everybody. Today we have to talk about the White House terms for Iran and the shipping crisis in Hormuz.\n\n"
        "I want to ask first about the White House offer and whether Tehran sees it as coercive diplomacy.\n\n"
        "Another point is the regional shipping lane, insurance costs, and whether the blockade threat is credible.\n"
    )

    rewritten, curation, section_count, skip_reason = land_best_intake.section_transcript(
        trim_args("dialogue-works"),
        body,
    )

    assert curation == "curated_sectioned"
    assert section_count >= 2
    assert skip_reason == ""
    assert rewritten.startswith("### Show Open - ")
    assert "\n### Segment 2 - " in rewritten
    assert "White House" in rewritten or "Shipping" in rewritten


def test_repair_asr_text_repairs_global_phrase_corruption() -> None:
    args = trim_args("daniel-davis")
    body = "The whole thing with the straight of hormones was breaking down in Anchora.\n"

    repaired = land_best_intake.repair_asr_text(args, body)

    assert repaired == "The whole thing with the Strait of Hormuz was breaking down in Ankara.\n"
    assert args.asr_repair_applied is True
    assert args.asr_repair_pass == "2026-07-09 asr-repair-v1"


def test_repair_asr_text_repairs_host_specific_noise() -> None:
    args = trim_args("mario-nawfal")
    body = (
        "This is all part of the plan. They just want breathing space before they continue their operation to capture Khagan and whatever. "
        "Do you think this argument is gaining more weight? want breathing space before they continue their operation to capture car guy into whatever do you think you know this argument is gaining more weight "
        "i don't think there is any grand plan.\n"
    )

    repaired = land_best_intake.repair_asr_text(args, body)

    assert "capture car guy" not in repaired
    assert "Kharg Island" in repaired
    assert args.asr_repair_applied is True


def test_repair_asr_text_respects_none_mode() -> None:
    args = trim_args("daniel-davis")
    args.asr_repair = "none"
    body = "The whole thing with the straight of hormones stayed broken in Anchora.\n"

    repaired = land_best_intake.repair_asr_text(args, body)

    assert repaired == body
    assert args.asr_repair_applied is False
    assert args.asr_repair_pass == ""


def test_repair_asr_text_can_preserve_layout_for_class_isolated_repair() -> None:
    args = trim_args("daniel-davis")
    body = "The straight of hormones remained open.\n\n\nLayout boundary stays visible.\n"

    repaired = land_best_intake.repair_asr_text(
        args,
        body,
        normalize_layout=False,
    )

    assert "Strait of Hormuz" in repaired
    assert "\n\n\nLayout boundary" in repaired
    assert args.asr_repair_applied is True


def test_repair_asr_text_preserves_existing_provenance_when_body_is_clean() -> None:
    args = trim_args("daniel-davis")
    args.asr_repair_applied = True
    args.asr_repair_pass = "2026-07-09 asr-repair-v1"
    body = "The Strait of Hormuz remained open during the briefing.\n"

    repaired = land_best_intake.repair_asr_text(args, body)

    assert repaired == body
    assert args.asr_repair_applied is True
    assert args.asr_repair_pass == "2026-07-09 asr-repair-v1"


def test_repair_asr_text_preserves_existing_provenance_for_unapproved_host() -> None:
    args = trim_args("neutrality-studies")
    args.asr_repair_applied = True
    args.asr_repair_pass = "manual-review-v1"
    body = "The transcript remains unchanged.\n"

    repaired = land_best_intake.repair_asr_text(args, body)

    assert repaired == body
    assert args.asr_repair_applied is True
    assert args.asr_repair_pass == "manual-review-v1"


def test_retrofit_source_is_idempotent_for_already_repaired_source() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: daniel-davis\n"
            "asr_repair_applied: true\n"
            "asr_repair_pass: \"2026-07-09 asr-repair-v1\"\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n\n"
            "## Transcript\n\n"
            "The Strait of Hormuz remained open during the briefing.\n",
            encoding="utf-8",
        )

        land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert "asr_repair_applied: true" in text
        assert 'asr_repair_pass: "2026-07-09 asr-repair-v1"' in text
    finally:
        shutil.rmtree(tmp_dir)


def test_apply_trim_metadata_preserves_existing_trim_provenance_when_clean() -> None:
    args = trim_args("daniel-davis")
    args.closing_trim_applied = True
    args.closing_trim_rule = "daniel-davis-closing-v1"
    args.closing_trim_chars_saved = 213
    args.closing_trim_words_saved = 41
    body = "The substantive discussion continues without the show closing.\n"

    trimmed = land_best_intake.apply_trim_metadata(args, body)

    assert trimmed == body
    assert args.closing_trim_applied is True
    assert args.closing_trim_rule == "daniel-davis-closing-v1"
    assert args.closing_trim_chars_saved == 213
    assert args.closing_trim_words_saved == 41


def test_retrofit_source_preserves_existing_trim_provenance() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: daniel-davis\n"
            "closing_trim_applied: true\n"
            "closing_trim_rule: \"daniel-davis-closing-v1\"\n"
            "closing_trim_chars_saved: 213\n"
            "closing_trim_words_saved: 41\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n\n"
            "## Transcript\n\n"
            "The substantive discussion continues without the show closing.\n",
            encoding="utf-8",
        )

        land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert "closing_trim_applied: true" in text
        assert 'closing_trim_rule: "daniel-davis-closing-v1"' in text
        assert "closing_trim_chars_saved: 213" in text
        assert "closing_trim_words_saved: 41" in text
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_sections_clear_eligible_transcript() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        source.write_text(
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: dialogue-works\n"
            "title: Example Dialogue Works Source\n"
            "source_form: interview\n"
            "editorial_note: Preserve as raw cleaned transcript. Not human-verified verbatim.\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "Hi everybody. Today we are looking at White House demands on Iran and the Hormuz crisis.\n"
            "\n"
            "I want to ask about the White House position and whether it can force Tehran into concessions.\n"
            "\n"
            "Another point is the shipping lane, insurance markets, and whether closure pressure can hold.\n",
            encoding="utf-8",
        )

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert result is not None
        assert result.startswith("TRIMMED")
        assert "transcript_curation: curated_sectioned" in text
        assert "section_count: 2" in text or "section_count: 3" in text
        assert "### Show Open - " in text
        assert "source-section pass 2026-07-09" in text
    finally:
        shutil.rmtree(tmp_dir)


def test_retrofit_source_preserves_existing_sectioned_body_without_force() -> None:
    tmp_dir = make_local_temp_dir()
    try:
        source = tmp_dir / "source-test.md"
        original = (
            "---\n"
            "pub_date: 2026-07-07\n"
            "host_slug: dialogue-works\n"
            "transcript_curation: curated_sectioned\n"
            "section_count: 2\n"
            "section_pass: \"2026-07-01 semantic-section-v1\"\n"
            "routing_state: provisional\n"
            "---\n"
            "# Example\n"
            "\n"
            "## Transcript\n"
            "\n"
            "### Show Open - Existing\n"
            "\n"
            "Already sectioned block.\n"
            "\n"
            "### Segment 2 - Existing Turn\n"
            "\n"
            "Second block.\n"
        )
        source.write_text(original, encoding="utf-8")

        result = land_best_intake.retrofit_source(source, "2026-06-01")
        text = source.read_text(encoding="utf-8")

        assert result is not None
        assert result.startswith("NORMALIZED") or result.startswith("UNCHANGED")
        assert "### Show Open - Existing" in text
        assert text.count("### ") == 2
    finally:
        shutil.rmtree(tmp_dir)


def test_fast_intake_infers_mercouris_solo_from_body_text() -> None:
    args = build_fast_args(
        "2026-07-08",
        "https://www.youtube.com/watch?v=4m2KLrVw1kA",
        "",
        "Alexander Mercouris: Russia Gives WW3 Warning - YouTube Transcripts: Good day everybody.\n",
    )

    normalized = land_best_intake.normalize_args(args)

    assert normalized.title == "Alexander Mercouris: Russia Gives WW3 Warning"
    assert normalized.host_slug == "alexander-mercouris"
    assert normalized.voice_slugs == ["mercouris"]
    assert normalized.source_form == "solo"
    assert normalized.thread == "mercouris"


def test_fast_intake_explicit_mercouris_guest_stays_interview() -> None:
    args = build_fast_args(
        "2026-08-28",
        "https://www.youtube.com/watch?v=mercouris-guest",
        "Alexander Mercouris with Jeffrey Sachs",
        "Alexander Mercouris speaks with Jeffrey Sachs about European security.\n",
    )
    args.host_slug = "alexander-mercouris"
    args.voice_slugs = ["sachs"]
    args.guest = "Jeffrey Sachs"
    args.guest_people = ["Jeffrey Sachs"]

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "alexander-mercouris"
    assert normalized.guest == "Jeffrey Sachs"
    assert normalized.source_form == "interview"
    assert normalized.source_class == "guest interview pressure test"


def test_fast_intake_generic_with_phrase_does_not_imply_guest() -> None:
    args = build_fast_args(
        "2026-08-28",
        "https://www.youtube.com/watch?v=davis-monologue",
        "Daniel Davis: Problems With the US Army",
        "Daniel Davis explains force readiness in a solo update.\n",
    )
    args.host_slug = "daniel-davis"

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "daniel-davis"
    assert normalized.source_form == "monologue"
    assert normalized.source_class == "host monologue"


def test_fast_intake_known_named_with_guest_still_implies_interview() -> None:
    args = build_fast_args(
        "2026-08-28",
        "https://www.youtube.com/watch?v=davis-guest",
        "Daniel Davis with Matthew Hoh",
        "Daniel Davis discusses military readiness.\n",
    )
    args.host_slug = "daniel-davis"

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "daniel-davis"
    assert normalized.voice_slugs == ["hoh"]
    assert normalized.source_form == "interview"
    assert normalized.source_class == "guest interview pressure test"


@pytest.mark.parametrize(
    ("host_slug", "title"),
    (
        ("daniel-davis", "Daniel Davis with Jane Doe"),
        ("alexander-mercouris", "Alexander Mercouris w/ Alex Example"),
    ),
)
def test_fast_intake_unknown_named_guest_requires_clarification(host_slug: str, title: str) -> None:
    args = build_fast_args(
        "2026-08-28",
        "https://www.youtube.com/watch?v=unknown-guest",
        title,
        "The host discusses military readiness and European security.\n",
    )
    args.host_slug = host_slug

    with pytest.raises(ValueError, match="title suggests an unrecognized guest"):
        land_best_intake.normalize_args(args)


def test_fast_intake_infers_dialogue_works_guest_from_body_text() -> None:
    args = build_fast_args(
        "2026-07-08",
        "https://www.youtube.com/watch?v=gjA5wIT9DZ8",
        "Larry Johnson: Iran Strikes US Bases in Bahrain & Kuwait - YouTube Transcripts",
        "Hi everybody. Today we have Larry Johnson back with us to talk about Iran and Hormuz.\n",
    )

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "dialogue-works"
    assert normalized.host == "Nima Alkhorshid"
    assert normalized.voice_slugs == ["johnson"]
    assert normalized.guest == "Larry Johnson"
    assert normalized.source_form == "interview"


def test_fast_intake_raises_single_blocker_for_ambiguous_multiple_guest_candidates() -> None:
    args = build_fast_args(
        "2026-07-09",
        "https://www.youtube.com/watch?v=SMBheNf3JHc",
        "BREAKING: Bahrain & Kuwait Just Struck Iran - w/ Col. Macgregor and Larry Johnson",
        "Hi everybody. Today we have Col Douglas Macgregor and Larry Johnson.\n",
    )
    args.host_slug = "dialogue-works"

    with pytest.raises(ValueError, match="primary guest/voice is ambiguous"):
        land_best_intake.normalize_args(args)


def test_fast_intake_real_july_dialogue_works_barnes_routes_to_guest_thread() -> None:
    body = (
        "Robert Barnes: U.S. Just REVOKED Iran Waivers - We Heading to War - YouTube Transcripts\n"
        "Hi everybody. Today's Tuesday, July 7, 2026, and our dear friend Robert Barnes is here with us.\n"
    )
    args = build_fast_args(
        "2026-07-07",
        "https://www.youtube.com/watch?v=H0UPyniTc_Q",
        "",
        body,
    )

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "dialogue-works"
    assert normalized.voice_slugs == ["barnes"]
    assert normalized.thread == "barnes"
    assert normalized.guest == "Robert Barnes"


def test_fast_intake_real_july_glenn_diesen_davis_routes_to_davis_thread() -> None:
    body = (
        "Daniel Davis: Trump Says the Ceasefire Is Over With Iran & Escalates the War With Russia - YouTube\n\n"
        "Transcripts:\n"
        "Welcome back. We are joined again by Lieutenant Colonel Daniel Davis.\n"
        "You know, Glenn, the bottom line here is that President Trump has no idea what he's doing.\n"
    )
    args = build_fast_args(
        "2026-07-09",
        "https://www.youtube.com/watch?v=Mp1drUnqlig",
        "",
        body,
    )

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "glenn-diesen"
    assert normalized.voice_slugs == ["davis"]
    assert normalized.thread == "davis"
    assert normalized.source_form == "interview"


def test_fast_intake_explicit_daniel_davis_guest_stays_interview() -> None:
    args = build_fast_args(
        "2026-08-26",
        "https://www.youtube.com/watch?v=4Q99MtTzrjk",
        "IRAN WAR: Why Everyone Is Falling in Line /Lt Col Daniel Davis & Matt Hoh",
        "IRAN WAR: Why Everyone Is Falling in Line /Lt Col Daniel Davis & Matt Hoh\n",
    )
    args.host_slug = "daniel-davis"
    args.voice_slugs = ["hoh"]
    args.guest = "Matthew Hoh"
    args.guest_people = ["Matthew Hoh"]

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "daniel-davis"
    assert normalized.voice_slugs == ["hoh"]
    assert normalized.guest == "Matthew Hoh"
    assert normalized.source_form == "interview"
    assert normalized.source_class == "guest interview pressure test"


def test_fast_intake_non_host_voice_stays_interview_without_guest_field() -> None:
    args = build_fast_args(
        "2026-08-26",
        "https://www.youtube.com/watch?v=4Q99MtTzrjk",
        "IRAN WAR: Why Everyone Is Falling in Line /Lt Col Daniel Davis & Matt Hoh",
        "IRAN WAR: Why Everyone Is Falling in Line /Lt Col Daniel Davis & Matt Hoh\n",
    )
    args.host_slug = "daniel-davis"
    args.voice_slugs = ["hoh"]

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "daniel-davis"
    assert normalized.voice_slugs == ["hoh"]
    assert normalized.source_form == "interview"
    assert normalized.source_class == "guest interview pressure test"


def test_fast_intake_real_july_dialogue_works_martyanov_routes_to_martyanov_thread() -> None:
    body = (
        "Andrei Martyanov: IRAN BOMBSHELL: Hypersonic Missile Hit U.S. Targets in 6 Minutes - Trump WARNED! - YouTube Transcripts\n"
        "Hi everybody. Today's Thursday, July 9, 2026 and our dear friend, our brother Andrei Martyanov is here with us.\n"
    )
    args = build_fast_args(
        "2026-07-09",
        "https://www.youtube.com/watch?v=V64fLKo3uHg",
        "",
        body,
    )

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "dialogue-works"
    assert normalized.voice_slugs == ["martyanov"]
    assert normalized.thread == "martyanov"


def test_fast_intake_real_july_moral_resistance_aguilar_infers_host_and_guest() -> None:
    body = (
        "U.S PLAN GROUND INVASION w/ Col Anthony Aguilar - YouTube\n\n"
        "Transcripts:\n"
        "And we are live. We've got Lieutenant Colonel Anthony Aguiler here. Lots happening.\n"
        "Thank you so much for joining us, Anthony. How are you?\n"
    )
    args = build_fast_args(
        "2026-07-09",
        "https://www.youtube.com/watch?v=cdtK9HajIVY",
        "",
        body,
    )

    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "moral-resistance"
    assert normalized.host == "Sulaiman Ahmed"
    assert normalized.voice_slugs == ["aguilar"]
    assert normalized.thread == "aguilar"


def test_quick_intake_infers_metadata_and_strips_exact_wrappers() -> None:
    body = (
        "Larry Johnson: US Running Out of Ammo - YouTube\n"
        "Transcripts:\n"
        "Hi everybody. Today we have Larry Johnson back with us to discuss Iran.\n"
    )
    args = build_fast_args("2026-07-20", "https://www.youtube.com/watch?v=test", "", body)
    args.quick = True
    args.host_slug = "judging-freedom"
    args.quick_positionals = []
    args.date = None
    args.inference_basis = []
    normalized = land_best_intake.normalize_args(args)

    assert normalized.title == "Larry Johnson: US Running Out of Ammo"
    assert normalized.host_slug == "judging-freedom"
    assert normalized.voice_slugs == ["johnson"]
    assert normalized.guest == "Larry Johnson"
    assert "Transcripts:" not in normalized._body_text_cache
    assert "wrapper-normalized" in normalized.inference_basis


def test_quick_intake_accepts_positional_host_and_url() -> None:
    body = "John Mearsheimer: A Warning - YouTube\nProfessor John Mearsheimer discusses the war.\n"
    args = build_fast_args("2026-07-20", "", "", body)
    args.quick = True
    args.host_slug = None
    args.quick_positionals = ["breaking-points", "https://www.youtube.com/watch?v=test2"]
    args.date = None
    args.inference_basis = []
    normalized = land_best_intake.normalize_args(args)

    assert normalized.host_slug == "breaking-points"
    assert normalized.url.endswith("test2")
    assert normalized.title == "John Mearsheimer: A Warning"


def test_quick_intake_today_records_date_basis() -> None:
    body = "Daniel Davis: Breaking Update - YouTube\nThe latest update is on the battlefield.\n"
    args = build_fast_args("", "https://www.youtube.com/watch?v=test3", "", body)
    args.pub_date = ""
    args.ingest_date = ""
    args.quick = True
    args.host_slug = "daniel-davis"
    args.quick_positionals = []
    args.date = "today"
    args.inference_basis = []
    normalized = land_best_intake.normalize_args(args)

    assert normalized.pub_date == date.today().isoformat()
    assert normalized.ingest_date == date.today().isoformat()
    assert "intake-assigned-today" in normalized.inference_basis


def test_quick_intake_dry_run_plan_has_inference_basis(monkeypatch, tmp_path: Path) -> None:
    sources, _ = configure_transaction_root(monkeypatch, tmp_path)
    body_file = tmp_path / "source.txt"
    body_file.write_text(
        "Max Blumenthal: Iran War - YouTube\n"
        "Hi everyone, Max Blumenthal is here to discuss Iran.\n",
        encoding="utf-8",
    )
    args = build_fast_args("2026-07-20", "https://www.youtube.com/watch?v=test4", "", "")
    args.quick = True
    args.host_slug = "judging-freedom"
    args.body_file = str(body_file)
    args.body_text = ""
    args.quick_positionals = []
    args.date = None
    args.inference_basis = []
    normalized = land_best_intake.normalize_args(args)
    plans, _ = land_best_intake.prepare_batch([normalized], {"source_count": 0, "sources": []})
    messages = land_best_intake.dry_run_messages(plans)

    assert messages[0].startswith("DRY RUN:")
    assert "inference_basis" in messages[0]
    assert not list(sources.rglob("source-*.md"))


def test_quick_batch_builds_one_plan_per_body_file(monkeypatch, tmp_path: Path) -> None:
    batch_dir = tmp_path / "quick-batch"
    batch_dir.mkdir()
    (batch_dir / "one.txt").write_text(
        "Larry Johnson: One - YouTube\nLarry Johnson discusses Iran.\n",
        encoding="utf-8",
    )
    (batch_dir / "two.txt").write_text(
        "Larry Johnson: Two - YouTube\nLarry Johnson discusses Russia.\n",
        encoding="utf-8",
    )
    args = build_fast_args("2026-07-20", "", "", "")
    args.quick = True
    args.host_slug = "judging-freedom"
    args.date = None
    args.batch_dir = str(batch_dir)
    args.quick_positionals = []
    args.inference_basis = []
    cli_args = SimpleNamespace(
        quick=True,
        batch_dir=str(batch_dir),
        metadata_file=None,
        pub_date="2026-07-20",
        ingest_date="2026-07-20",
        date=None,
        title="",
        url="",
        body_file=None,
        body_text=None,
        voice_slugs=[],
        host_slug="judging-freedom",
        host="",
        guest="",
        host_people=[],
        guest_people=[],
        show_title="",
        channel_name="",
        show="",
        thread=None,
        kind="cleaned-transcript",
        source_form="interview",
        source_class="guest interview pressure test",
        modality="cleaned-transcript",
        review_state="unreviewed",
        routing_state="provisional",
        source_note="",
        editorial_note="Preserve as raw cleaned transcript. Not human-verified verbatim.",
        upstream_path=None,
        dry_run=True,
        trim_opening="auto",
        asr_repair="auto",
        sectioning="auto",
        quick_positionals=[],
    )
    sources = land_best_intake.gather_sources(cli_args)

    assert len(sources) == 2
    assert {item.title for item in sources} == {"Larry Johnson: One", "Larry Johnson: Two"}


@pytest.mark.parametrize(
    "value",
    ["2026-7-01", "2026-02-30", "..\\..\\outside", "2026/07/01", ""],
)
def test_date_validation_rejects_malformed_impossible_and_escaping_values(value: str) -> None:
    with pytest.raises(ValueError, match="valid YYYY-MM-DD"):
        land_best_intake.validate_iso_date(value, "pub_date")


def test_backfill_rejects_reversed_range_before_scanning(monkeypatch, tmp_path: Path) -> None:
    sources, _ = configure_transaction_root(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="must not be earlier"):
        land_best_intake.backfill_sources("2026-07-10", "2026-07-09")

    assert list(sources.iterdir()) == []


def test_legacy_backfill_execution_is_disabled_before_scanning(monkeypatch, tmp_path: Path) -> None:
    sources, _ = configure_transaction_root(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="Legacy backfill execution is disabled"):
        land_best_intake.backfill_sources("2026-07-01")

    assert list(sources.iterdir()) == []


def test_url_is_optional_and_upstream_provenance_remains_distinct(monkeypatch, tmp_path: Path) -> None:
    _, _ = configure_transaction_root(monkeypatch, tmp_path)
    args = transaction_args("2026-07-15", "URL unavailable", url="")

    plans, proposed = land_best_intake.prepare_batch([args], {"source_count": 0, "sources": []})

    assert 'source_url: ""' in plans[0].source_text
    assert "source_url_status: unavailable" in plans[0].source_text
    assert plans[0].manifest_row["upstream_path"].startswith("operator-paste://")
    assert proposed["source_count"] == 1


def test_batch_preflight_rejects_duplicate_and_existing_targets_without_writes(
    monkeypatch, tmp_path: Path
) -> None:
    sources, _ = configure_transaction_root(monkeypatch, tmp_path)
    first = transaction_args("2026-07-15", "Duplicate")
    second = transaction_args("2026-07-15", "Duplicate")

    with pytest.raises(ValueError, match="duplicate source path"):
        land_best_intake.prepare_batch([first, second], {"source_count": 0, "sources": []})
    assert list(sources.iterdir()) == []

    target, _, _ = land_best_intake.source_plan(first)
    target.parent.mkdir()
    target.write_text("existing\n", encoding="utf-8")
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        land_best_intake.prepare_batch([first], {"source_count": 0, "sources": []})
    assert target.read_text(encoding="utf-8") == "existing\n"


def test_batch_preflight_rejects_manifest_path_collision(monkeypatch, tmp_path: Path) -> None:
    configure_transaction_root(monkeypatch, tmp_path)
    args = transaction_args("2026-07-15", "Manifest duplicate")
    target, _, _ = land_best_intake.source_plan(args)
    relative = target.relative_to(tmp_path).as_posix()
    manifest = {"source_count": 1, "sources": [{"local_path": relative}]}

    with pytest.raises(ValueError, match="Manifest already contains"):
        land_best_intake.prepare_batch([args], manifest)

    duplicated = {
        "source_count": 2,
        "sources": [{"local_path": relative}, {"local_path": relative}],
    }
    with pytest.raises(ValueError, match="duplicate source paths"):
        land_best_intake.prepare_batch([args], duplicated)


def test_dry_run_preparation_creates_no_directories(monkeypatch, tmp_path: Path) -> None:
    sources, _ = configure_transaction_root(monkeypatch, tmp_path)
    args = transaction_args("2026-07-15", "Dry run")

    plans, _ = land_best_intake.prepare_batch([args], {"source_count": 0, "sources": []})
    messages = land_best_intake.dry_run_messages(plans)

    assert messages[0].startswith("DRY RUN:")
    assert list(sources.iterdir()) == []


def test_successful_batch_publishes_sources_and_manifest_atomically(
    monkeypatch, tmp_path: Path
) -> None:
    _, manifest_path = configure_transaction_root(monkeypatch, tmp_path)
    args = [
        transaction_args("2026-07-15", "First source"),
        transaction_args("2026-07-15", "Second source"),
    ]
    original = json.loads(manifest_path.read_text(encoding="utf-8"))
    plans, proposed = land_best_intake.prepare_batch(args, original)

    messages = land_best_intake.publish_batch(plans, proposed)

    assert len(messages) == 2
    assert all(plan.source_path.exists() for plan in plans)
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["source_count"] == 2
    assert not list(manifest_path.parent.rglob("*.stage"))


def test_voice_indexes_sync_after_successful_publish(monkeypatch, tmp_path: Path) -> None:
    _, manifest_path = configure_transaction_root(monkeypatch, tmp_path)
    voice_root = tmp_path / "narrative-geopolitics" / "voices" / "audit-voice"
    voice_root.mkdir(parents=True)
    (voice_root / "source-index.md").write_text(
        "# Audit Voice Source Index\n\n"
        "Corpus: 0 local route rows across 0 central archive source files.\n\n"
        "| Date | Source | Role | Host slug | Archive link |\n"
        "| --- | --- | --- | --- | --- |\n",
        encoding="utf-8",
    )
    args = [transaction_args("2026-07-15", "Voice shelf source")]
    original = json.loads(manifest_path.read_text(encoding="utf-8"))
    plans, proposed = land_best_intake.prepare_batch(args, original)

    voice_updates, voice_messages = land_best_intake.project_voice_indexes_for_plans(
        plans, proposed
    )
    messages = land_best_intake.publish_batch(plans, proposed, voice_updates)
    messages.extend(voice_messages)

    index_text = (voice_root / "source-index.md").read_text(encoding="utf-8")
    assert "Voice shelves changed: audit-voice" in messages
    assert "Voice routes added: 1" in messages
    assert "Corpus: 1 local route rows across 1 central archive source files." in index_text
    assert "| `2026-07-15` | Voice shelf source | `guest` | `audit-host` |" in index_text


def test_voice_index_failure_rolls_back_sources_indexes_and_manifest(
    monkeypatch, tmp_path: Path
) -> None:
    _, manifest_path = configure_transaction_root(monkeypatch, tmp_path)
    index = (
        tmp_path / "narrative-geopolitics" / "voices" / "audit-voice" / "source-index.md"
    )
    index.parent.mkdir(parents=True)
    original_index = (
        "# Audit Voice Source Index\n\n"
        "Corpus: 0 local route rows across 0 central archive source files.\n\n"
        "| Date | Source | Role | Host slug | Archive link |\n"
        "| --- | --- | --- | --- | --- |\n"
    )
    index.write_text(original_index, encoding="utf-8")
    args = [transaction_args("2026-07-15", "Rollback voice source")]
    original_manifest = manifest_path.read_text(encoding="utf-8")
    plans, proposed = land_best_intake.prepare_batch(
        args, json.loads(original_manifest)
    )
    updates, _ = land_best_intake.project_voice_indexes_for_plans(plans, proposed)
    real_replace = os.replace

    def fail_index(source, destination):
        if Path(destination) == index:
            raise OSError("simulated voice index publication failure")
        return real_replace(source, destination)

    monkeypatch.setattr(land_best_intake.os, "replace", fail_index)
    with pytest.raises(OSError, match="simulated voice index"):
        land_best_intake.publish_batch(plans, proposed, updates)

    assert not plans[0].source_path.exists()
    assert index.read_text(encoding="utf-8") == original_index
    assert manifest_path.read_text(encoding="utf-8") == original_manifest


def test_source_publication_failure_rolls_back_prior_sources_and_manifest(
    monkeypatch, tmp_path: Path
) -> None:
    _, manifest_path = configure_transaction_root(monkeypatch, tmp_path)
    args = [
        transaction_args("2026-07-15", "First source"),
        transaction_args("2026-07-15", "Second source"),
    ]
    original_text = manifest_path.read_text(encoding="utf-8")
    plans, proposed = land_best_intake.prepare_batch(
        args, json.loads(original_text)
    )
    real_replace = os.replace

    def fail_second(source, destination):
        if Path(destination) == plans[1].source_path:
            raise OSError("simulated source publication failure")
        return real_replace(source, destination)

    monkeypatch.setattr(land_best_intake.os, "replace", fail_second)
    with pytest.raises(OSError, match="simulated source"):
        land_best_intake.publish_batch(plans, proposed)

    assert all(not plan.source_path.exists() for plan in plans)
    assert manifest_path.read_text(encoding="utf-8") == original_text
    assert not list(manifest_path.parent.rglob("*.stage"))


def test_manifest_publication_failure_rolls_back_all_sources(
    monkeypatch, tmp_path: Path
) -> None:
    _, manifest_path = configure_transaction_root(monkeypatch, tmp_path)
    args = [transaction_args("2026-07-15", "Manifest failure")]
    original_text = manifest_path.read_text(encoding="utf-8")
    plans, proposed = land_best_intake.prepare_batch(
        args, json.loads(original_text)
    )
    real_replace = os.replace

    def fail_manifest(source, destination):
        if Path(destination) == manifest_path:
            raise OSError("simulated manifest publication failure")
        return real_replace(source, destination)

    monkeypatch.setattr(land_best_intake.os, "replace", fail_manifest)
    with pytest.raises(OSError, match="simulated manifest"):
        land_best_intake.publish_batch(plans, proposed)

    assert not plans[0].source_path.exists()
    assert manifest_path.read_text(encoding="utf-8") == original_text
    assert not list(manifest_path.parent.rglob("*.stage"))


def test_documented_host_allowlists_match_executable_contracts() -> None:
    method = (
        REPO_ROOT / "narrative-geopolitics" / "method" / "best-intake.md"
    ).read_text(encoding="utf-8")
    expected = {
        "Current approved hosts:": set(land_best_intake.HOST_TRIM_RULES),
        "Current approved auto-section hosts:": land_best_intake.SECTIONING_APPROVED_HOSTS,
        "Current approved auto-ASR-repair hosts:": land_best_intake.ASR_REPAIR_APPROVED_HOSTS,
    }

    for label, hosts in expected.items():
        assert documented_hosts(method, label) == hosts
def test_transcript_title_wins_and_operator_title_is_preserved_as_alias() -> None:
    args = build_fast_args(
        "2026-07-24",
        "https://www.youtube.com/watch?v=abc123XYZ_1",
        "Operator title variant",
        "Transcript title - YouTube\n\nTranscripts:\n\nGood day.\n",
    )
    args.host_slug = "audit-host"
    args.voice_slugs = ["audit-voice"]
    normalized = land_best_intake.normalize_args(args)
    assert normalized.title == "Transcript title"
    assert normalized.title_source == "transcript"
    assert normalized.title_aliases == ["Operator title variant"]
    assert normalized.source_identity == "youtube:abc123XYZ_1"
    assert "operator-title-differs-from-transcript-title" in normalized.metadata_warnings


def test_preflight_reports_video_identity_and_duplicate_warning(monkeypatch, tmp_path: Path) -> None:
    _, manifest_path = configure_transaction_root(monkeypatch, tmp_path)
    manifest_path.write_text(
        json.dumps({
            "source_count": 1,
            "sources": [{
                "local_path": "archive/sources/geopolitics/sources/2026-07-24/source-existing.md",
                "source_identity": "youtube:abc123XYZ_1",
                "source_url": "https://www.youtube.com/watch?v=abc123XYZ_1",
            }],
        }), encoding="utf-8"
    )
    args = build_fast_args(
        "2026-07-24", "https://www.youtube.com/watch?v=abc123XYZ_1", "A title", "Real body.\n"
    )
    args.host_slug = "audit-host"
    args.voice_slugs = ["audit-voice"]
    normalized = land_best_intake.normalize_args(args)
    receipt = land_best_intake.preflight_receipt([normalized], json.loads(manifest_path.read_text(encoding="utf-8")))
    row = receipt["sources"][0]
    assert receipt["status"] == "warning"
    assert row["video_id"] == "abc123XYZ_1"
    assert row["duplicate"] is True
    assert "already-landed-identity" in row["warnings"]
    assert receipt["outcome_metrics"]["attempted_sources"] == 1
    assert receipt["outcome_metrics"]["warning_events"] == 1
    assert receipt["outcome_metrics"]["duplicate_stops"] == 1
    assert receipt["outcome_metrics"]["correction_signal_events"] == 0


def test_manifest_row_carries_identity_and_date_basis() -> None:
    args = build_fast_args(
        "2026-07-24", "https://www.youtube.com/watch?v=abc123XYZ_1", "A title", "Real body.\n"
    )
    args.host_slug = "audit-host"
    args.voice_slugs = ["audit-voice"]
    normalized = land_best_intake.normalize_args(args)
    path = REPO_ROOT / "archive" / "sources" / "geopolitics" / "sources" / "2026-07-24" / "source-a-title-2026-07-24.md"
    row = land_best_intake.build_manifest_row(normalized, path, "operator-paste://2026-07-24/a-title")
    assert row["source_identity"] == "youtube:abc123XYZ_1"
    assert row["date_basis"] == "operator-supplied"


def test_terminal_receipt_target_requires_absolute_external_path(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="must be absolute"):
        land_best_intake.validate_terminal_receipt_target(Path("receipt.json"))

    with pytest.raises(ValueError, match="outside the repository"):
        land_best_intake.validate_terminal_receipt_target(
            REPO_ROOT / "receipt.json"
        )

    existing = tmp_path / "existing.json"
    existing.write_text("{}\n", encoding="utf-8")
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        land_best_intake.validate_terminal_receipt_target(existing)


def test_prepare_terminal_receipt_target_enforces_measurement_contract(
    tmp_path: Path,
) -> None:
    target = tmp_path / "receipt.json"
    base = {
        "receipt": target,
        "json": True,
        "backfill_since": None,
        "no_preflight": False,
    }
    assert land_best_intake.prepare_terminal_receipt_target(
        SimpleNamespace(**base)
    ) == target.resolve()

    with pytest.raises(ValueError, match="requires --json"):
        land_best_intake.prepare_terminal_receipt_target(
            SimpleNamespace(**(base | {"json": False}))
        )
    with pytest.raises(ValueError, match="backfill"):
        land_best_intake.prepare_terminal_receipt_target(
            SimpleNamespace(**(base | {"backfill_since": "2026-08-01"}))
        )
    with pytest.raises(ValueError, match="governed preflight"):
        land_best_intake.prepare_terminal_receipt_target(
            SimpleNamespace(**(base | {"no_preflight": True}))
        )


def test_terminal_receipt_write_is_canonical_and_no_clobber(
    tmp_path: Path,
) -> None:
    target = tmp_path / "receipt.json"
    payload = land_best_intake.terminal_receipt_payload(
        {
            "status": "landed",
            "preflight": {"sources": []},
            "outcome_metrics": {"disposition": "landed"},
        },
        measurement_scope="preflight-qualified",
    )

    land_best_intake.write_terminal_receipt(target, payload)

    raw = target.read_bytes()
    assert raw.endswith(b"\n")
    assert b"\r\n" not in raw
    written = json.loads(raw)
    assert written["schema"] == "best-intake-terminal-receipt-v1"
    assert written["measurement_scope"] == "preflight-qualified"

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        land_best_intake.write_terminal_receipt(target, payload)


def test_post_landing_receipt_failure_preserves_landed_outcome() -> None:
    result = {
        "status": "landed",
        "outcome_metrics": {
            "disposition": "landed",
            "successful_landings": 1,
            "failed_attempts": 0,
        },
    }

    payload = land_best_intake.post_landing_receipt_failure_payload(
        result, OSError("receipt disk unavailable")
    )

    assert payload["status"] == "landed"
    assert payload["landing_status"] == "landed"
    assert payload["receipt_status"] == "write-failed-after-land"
    assert payload["receipt_error"] == "receipt disk unavailable"
    assert payload["outcome_metrics"]["failed_attempts"] == 0
    assert "receipt_status" not in result


def test_main_does_not_reclassify_landing_when_receipt_write_fails(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    receipt_target = tmp_path / "receipt.json"
    cli_args = SimpleNamespace(
        backfill_since=None,
        preflight=False,
        dry_run=False,
        json=True,
    )
    preflight = {"status": "ready", "sources": [{"warnings": []}]}
    metrics = {
        "disposition": "landed",
        "attempted_sources": 1,
        "warning_sources": 0,
        "warning_events": 0,
        "duplicate_stops": 0,
        "correction_signal_sources": 0,
        "correction_signal_events": 0,
        "successful_landings": 1,
        "failed_attempts": 0,
    }
    source = SimpleNamespace(source_identity="youtube:one", url="https://example.test/one")

    monkeypatch.setattr(land_best_intake, "parse_args", lambda: cli_args)
    monkeypatch.setattr(
        land_best_intake,
        "prepare_terminal_receipt_target",
        lambda _: receipt_target,
    )
    monkeypatch.setattr(land_best_intake, "gather_sources", lambda _: [source])
    monkeypatch.setattr(land_best_intake, "load_manifest", lambda: {})
    monkeypatch.setattr(
        land_best_intake, "preflight_receipt", lambda *_: preflight
    )
    monkeypatch.setattr(land_best_intake, "archived_source_urls", lambda: {})
    monkeypatch.setattr(land_best_intake, "archived_source_identities", lambda: {})
    monkeypatch.setattr(
        land_best_intake,
        "prepare_batch",
        lambda *_: ([object()], {"source_count": 1}),
    )
    monkeypatch.setattr(
        land_best_intake,
        "project_voice_indexes_for_plans",
        lambda *_: ({}, []),
    )
    monkeypatch.setattr(
        land_best_intake, "publish_batch", lambda *_: ["Source landed"]
    )
    monkeypatch.setattr(
        land_best_intake, "disposition_metrics", lambda *_args, **_kwargs: metrics
    )
    monkeypatch.setattr(
        land_best_intake,
        "write_terminal_receipt",
        lambda *_: (_ for _ in ()).throw(OSError("receipt disk unavailable")),
    )

    assert land_best_intake.main() == 1

    result = json.loads(capsys.readouterr().err)
    assert result["status"] == "landed"
    assert result["landing_status"] == "landed"
    assert result["receipt_status"] == "write-failed-after-land"
    assert result["outcome_metrics"]["failed_attempts"] == 0


def test_preflight_unavailable_failure_metrics_invent_no_attempt() -> None:
    metrics = land_best_intake.empty_failure_metrics()

    assert metrics["disposition"] == "failed"
    assert metrics["attempted_sources"] == 0
    assert metrics["failed_attempts"] == 1
