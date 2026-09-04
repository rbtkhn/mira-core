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
    assert "For manually added or browser-discovered rows" in text
    assert "include `channel_slug=SLUG` in notes" in text
    assert "current exporter contract" in text
