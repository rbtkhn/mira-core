import pytest

def test_native_intake_preserves_publication_homepage(monkeypatch):
    import sys
    import land_best_intake as intake
    monkeypatch.setattr(sys, "argv", ["intake", "--pub-date", "2026-09-14", "--ingest-date", "2026-09-14", "--title", "Test article",
        "--url", "https://glenndiesen.substack.com/p/test", "--body-text", "A complete test article.",
        "--voice-slug", "diesen", "--voice-slug", "blumenthal", "--host-slug", "glenndiesen", "--source-form", "newsletter",
        "--publication-url", "https://glenndiesen.substack.com", "--trim-opening", "none",
        "--asr-repair", "none", "--sectioning", "none"])
    args = intake.args_from_cli(intake.parse_args())
    plan = intake.prepare_landing(args)
    assert plan.manifest_row["publication_url"] == "https://glenndiesen.substack.com"
    assert 'publication_url: "https://glenndiesen.substack.com"' in plan.source_text
    assert plan.manifest_row["voice_roles"] == {"diesen": ["author"], "blumenthal": ["author"]}
    assert plan.manifest_row["role_status"] == {"diesen": "confirmed", "blumenthal": "confirmed"}
    assert plan.manifest_row["source_form"] == "newsletter"
    assert plan.source_text.count("\nsource_form:") == 1
    assert 'voice_roles: {"diesen": ["author"], "blumenthal": ["author"]}' in plan.source_text
    import role_aware_archive
    assert role_aware_archive.validate_row(plan.manifest_row) == []
