from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "docs" / "skill-drafts" / "youtube-capture" / "SKILL.md"


def skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_named_voice_browser_only_excludes_yt_dlp_helpers() -> None:
    text = " ".join(skill_text().split())
    assert "If the operator says browser-only" in text
    assert "in-app browser only" in text
    assert "`yt-dlp`" in text
    assert (
        "do not use that helper for discovery, transcript capture, metadata "
        "closure, or duplicate resolution"
    ) in text


def test_manual_rows_preserve_channel_slug_for_export_intake() -> None:
    text = " ".join(skill_text().split())
    assert "For manually added or browser-discovered Geopolitics rows" in text
    assert "include `channel_slug=SLUG` in notes" in text
    assert "current exporter contract" in text


def test_skill_defines_one_cross_archive_router() -> None:
    text = " ".join(skill_text().split())
    assert "single repository-local front door" in text
    assert "Route by channel first" in text
    assert "archive/sources/youtube-channel-routing.yml" in text
    assert "Unknown channels fail closed" in text


def test_skill_routes_nate_channels_to_singularity_not_geopolitics() -> None:
    text = " ".join(skill_text().split())
    assert "Nate Herk and Nate B. Jones route to Singularity capture-target notes" in text
    assert "archive/sources/singularity/nate-herk-capture-targets-YYYY-MM-DD.md" in text
    assert "archive/sources/singularity/nate-b-jones-capture-targets-YYYY-MM-DD.md" in text
    assert "must not update `archive/sources/singularity/singularity-signal-ledger.*`" in text


def test_skill_explains_capture_integrity_failure_and_reentry() -> None:
    text = " ".join(skill_text().split())
    assert "known Geopolitics channels through the delegated channel index" in text
    assert "earlier dated capture-target notes" in text
    assert "pending capture does not prove admission" in text
    assert "malformed existing table row stops the write without changing the note" in text
