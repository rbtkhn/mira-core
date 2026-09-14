from __future__ import annotations

import json
import hashlib
import re
import subprocess
import sys
from argparse import Namespace
from datetime import date
from pathlib import Path

import pytest

import voice_accountability


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "docs" / "skill-drafts" / "voice-accountability"
SCRIPT = SKILL_ROOT / "scripts" / "find_revision_candidates.py"


def run_finder(repo_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(repo_root),
            *arguments,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def write_source(
    repo_root: Path, day: str, name: str, guest: str, body: str
) -> Path:
    source_dir = (
        repo_root / "archive" / "sources" / "geopolitics" / "sources" / day
    )
    source_dir.mkdir(parents=True, exist_ok=True)
    path = source_dir / name
    path.write_text(
        f"---\npub_date: {day}\nguest: {guest}\nreview_state: unreviewed\n---\n{body}\n",
        encoding="utf-8",
    )
    return path


def test_skill_metadata_and_deployable_contract() -> None:
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    keys = {
        line.split(":", 1)[0]
        for line in frontmatter.splitlines()
        if line.strip() and ":" in line
    }
    assert keys == {"name", "description"}
    assert "explicit-personal-admission" in text
    assert "qualified-collective-revision" in text
    assert "Do not convert a host's statement into a guest finding" in text

    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )
    assert 'display_name: "Voice Accountability"' in metadata
    assert "$voice-accountability" in metadata


def test_finder_filters_dates_and_voices_and_keeps_stdout_json(tmp_path: Path) -> None:
    expected = write_source(
        tmp_path,
        "2026-06-10",
        "source-alex-example.md",
        "Alex Example",
        "I was wrong. I thought the talks would succeed, but they did not.",
    )
    write_source(
        tmp_path,
        "2026-06-11",
        "source-sam-example.md",
        "Sam Example",
        "I was wrong about the timing.",
    )
    write_source(
        tmp_path,
        "2026-07-01",
        "source-alex-later.md",
        "Alex Example",
        "I was wrong about the later event.",
    )

    result = run_finder(
        tmp_path,
        "--from",
        "2026-06-01",
        "--to",
        "2026-06-30",
        "--voice",
        "alex example",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["files_examined"] == 1
    assert payload["candidate_count"] == 1
    assert payload["candidates"][0]["path"] == str(expected.resolve())
    assert payload["candidates"][0]["signals"] == [
        "explicit",
        "prediction",
        "revision",
    ]


def test_finder_rejects_conditional_false_positive_and_ranks_admission(
    tmp_path: Path,
) -> None:
    write_source(
        tmp_path,
        "2026-06-10",
        "source-example.md",
        "Example Voice",
        "If I am wrong, I will correct myself.\nI expected a delay.\nI was wrong.",
    )

    result = run_finder(
        tmp_path, "--from", "2026-06-10", "--to", "2026-06-10"
    )

    assert result.returncode == 0
    candidates = json.loads(result.stdout)["candidates"]
    assert len(candidates) == 2
    assert candidates[0]["score"] > candidates[1]["score"]
    assert candidates[0]["context"].splitlines()[-1].endswith("I was wrong.")


def test_finder_rejects_reversed_date_range(tmp_path: Path) -> None:
    result = run_finder(
        tmp_path, "--from", "2026-07-02", "--to", "2026-07-01"
    )

    assert result.returncode != 0
    assert "--from must not be later than --to" in result.stderr
    assert result.stdout == ""


def test_legacy_alias_routes_to_the_canonical_skill_without_a_script_copy() -> None:
    from validate_repository import LOCAL_SKILLS
    from codex_skill_registry import DEPLOYABLE_SKILL_NAMES

    alias = SKILL_ROOT.parent / "voice-revision-audit"
    text = (alias / "SKILL.md").read_text(encoding="utf-8")
    targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    assert [(alias / target).resolve() for target in targets] == [
        (SKILL_ROOT / "SKILL.md").resolve()
    ]
    assert not (alias / "scripts").exists()
    assert "voice-revision-audit" in LOCAL_SKILLS
    assert "voice-revision-audit" not in DEPLOYABLE_SKILL_NAMES
    assert voice_accountability.CANDIDATE_SCRIPT.resolve() == SCRIPT.resolve()


@pytest.mark.parametrize("dry_run", [True, False])
def test_audit_does_not_write_sources_or_ledger_with_or_without_dry_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    dry_run: bool,
) -> None:
    write_source(
        tmp_path, "2026-06-10", "source-example.md", "Example Voice",
        "I was wrong. I thought the talks would succeed, but they did not.",
    )
    tracker = tmp_path / "narrative-geopolitics" / "work" / "voice-accountability"
    tracker.mkdir(parents=True)
    (tracker / "voice-revision-ledger.json").write_text('{"entries": []}', encoding="utf-8")
    (tracker / "voice-revision-ledger.md").write_text("untouched mirror", encoding="utf-8")

    def snapshot() -> dict[str, str]:
        return {
            path.relative_to(tmp_path).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in tmp_path.rglob("*") if path.is_file()
        }

    before = snapshot()
    monkeypatch.setattr(voice_accountability, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(voice_accountability, "LEDGER_JSON_PATH", tracker / "voice-revision-ledger.json")
    monkeypatch.setattr(voice_accountability, "LEDGER_MD_PATH", tracker / "voice-revision-ledger.md")
    args = Namespace(date_from=date(2026, 6, 10), date_to=date(2026, 6, 10),
                     voice="Example Voice", mode="audit", dry_run=dry_run)
    assert voice_accountability.run_candidates(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["candidate_count"] > 0
    assert payload["ledger_mutation"] == "none"
    assert snapshot() == before


@pytest.mark.skipif(
    not (REPO_ROOT / "archive" / "sources" / "geopolitics" / "sources").is_dir(),
    reason="requires hydrated archive transcript bodies",
)
def test_july_known_explicit_admissions_are_retrieved() -> None:
    result = run_finder(
        REPO_ROOT,
        "--from",
        "2026-07-01",
        "--to",
        "2026-07-16",
        "--limit",
        "100",
    )

    assert result.returncode == 0
    candidates = json.loads(result.stdout)["candidates"]
    evidence = {(Path(item["path"]).name, item["line"]) for item in candidates}
    assert (
        "source-scott-ritter-trump-briefed-on-all-out-war-scenario-in-iran-2026-07-01.md",
        202,
    ) in evidence
    assert (
        "source-larry-johnson-u-s-attacks-iran-now-iran-hits-back-as-hormuz-turns-into-a-firing-hell-2026-07-13.md",
        65,
    ) in evidence
