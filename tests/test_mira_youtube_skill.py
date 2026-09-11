from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "docs" / "skill-drafts" / "mira-youtube" / "SKILL.md"


def test_skill_contract_has_modes_boundaries_and_compatibility() -> None:
    text = SKILL.read_text(encoding="utf-8")
    for value in ("discover", "verify", "capture", "triage", "monitor", "organize", "creator-ops", "handoff"):
        assert f"`{value}`" in text
    assert "default is read-only" in text
    assert "`tools\\run.ps1 youtube-capture ...` remains supported" in text
    assert "Unknown or ambiguous channels fail closed" in text
    assert "readable Markdown link" in text
    assert "canonical watch URL" in text


def test_receipt_validation_accepts_structured_browser_receipt(tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({
        "terminal_state": "browser-verified",
        "channel_url": "https://www.youtube.com/@example",
        "video_url": "https://www.youtube.com/watch?v=example1",
        "observed_surfaces": ["Subscriptions", "Watch"],
        "schema_version": 2,
        "account_access": {"account_visible": True, "eligible": True, "fresh_session_recheck": True},
        "coverage": {"complete": True},
        "candidates": [{
            "video_url": "https://www.youtube.com/watch?v=example1",
            "channel_url": "https://www.youtube.com/@example",
            "title": "Example",
            "channel": "Example",
            "date": "2026-09-11",
            "format": "video",
            "duration_seconds": 1200,
        }],
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "mira_youtube.py"), "receipt-validate", str(receipt)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    assert "MIRA_YOUTUBE_RECEIPT=valid" in result.stdout


def test_receipt_validation_rejects_account_data(tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({
        "terminal_state": "account-action-complete",
        "account_identifier": "mira@example.com",
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "mira_youtube.py"), "receipt-validate", str(receipt)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1


def test_contract_lands_exact_transcript_attachments_without_redundant_step() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "Attached transcript bundle rule" in text
    assert "Do not insert a redundant" in text
    assert "Unmatched, ambiguous, unrouted" in text


def test_comment_capability_probe_fails_closed_when_composer_is_missing(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(json.dumps({
        "account_visible": True,
        "watch_page_rendered": True,
        "comments_rendered": True,
        "composer_present": False,
        "submit_control_present": False,
        "posted": False,
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "mira_youtube.py"), "comment-capability-validate", str(probe)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    assert "MIRA_YOUTUBE_COMMENT_CAPABILITY=unconfirmed" in result.stdout


def test_triage_excludes_short_clip_and_duplicate_and_keeps_clickable_url(tmp_path: Path) -> None:
    source = tmp_path / "candidates.json"
    source.write_text(json.dumps({"candidates": [
        {"video_url": "https://www.youtube.com/watch?v=long1", "channel_url": "https://www.youtube.com/@a", "title": "Long", "channel": "A", "date": "2026-09-11", "format": "video", "duration_seconds": 1200},
        {"video_url": "https://www.youtube.com/watch?v=short1", "channel_url": "https://www.youtube.com/@a", "title": "Short", "channel": "A", "date": "2026-09-11", "format": "short", "duration_seconds": 1200},
        {"video_url": "https://www.youtube.com/watch?v=brief1", "channel_url": "https://www.youtube.com/@a", "title": "Brief", "channel": "A", "date": "2026-09-11", "format": "video", "duration_seconds": 300},
    ]}), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "mira_youtube.py"), "triage", str(source)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["candidates"][0]["canonical_url"].endswith("v=long1")
    assert payload["candidates"][1]["disposition"] == "skip"
    assert "short-or-clip" in payload["candidates"][1]["exclusion_reason"]
    assert "below-minimum-duration" in payload["candidates"][2]["exclusion_reason"]


def test_browser_verified_receipt_rejects_incomplete_coverage(tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({
        "schema_version": 2,
        "terminal_state": "browser-verified",
        "observed_surfaces": ["Subscriptions"],
        "coverage": {"complete": False},
        "account_access": {"account_visible": True, "eligible": True, "fresh_session_recheck": True},
        "candidates": [],
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "mira_youtube.py"), "receipt-validate", str(receipt)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
