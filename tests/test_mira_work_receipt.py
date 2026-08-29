from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import mira_work_receipt as subject


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def snapshot_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.name", "Mira Test")
    git(repo, "config", "user.email", "mira@example.invalid")
    (repo / "tracked.txt").write_text("one", encoding="utf-8")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-m", "initial")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


@pytest.fixture
def git_cleanup(tmp_path: Path):
    yield
    for path in sorted(tmp_path.rglob("*"), reverse=True):
        try:
            path.chmod(path.stat().st_mode | stat.S_IWRITE)
        except OSError:
            pass


def write_receipt(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def complete_inline_receipt() -> str:
    return "\n".join(f"{field}: filled" for field in subject.REQUIRED_FIELDS)


def complete_inline_preflight() -> str:
    return "\n".join(f"{field}: filled" for field in subject.PREFLIGHT_FIELDS)


def complete_inline_preflight_advisory() -> str:
    return "\n".join(f"{field}: filled" for field in subject.PREFLIGHT_ADVISORY_FIELDS)


def set_repo_root(monkeypatch, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(subject, "REPO_ROOT", root)
    return root


def test_complete_inline_receipt_passes(tmp_path, monkeypatch, capsys) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    receipt = write_receipt(repo / "receipt.md", complete_inline_receipt())

    assert subject.main(["receipt-check", "--file", str(receipt)]) == 0
    assert capsys.readouterr().out.splitlines() == ["mira_work_receipt=pass"]


def test_complete_multiline_receipt_passes(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    receipt = write_receipt(
        repo / "receipt.md",
        "\n".join(
            f"**`{field}`:**\n  - filled over multiple lines\n  - with detail"
            for field in subject.REQUIRED_FIELDS
        ),
    )

    result = subject.check_receipt(receipt)

    assert result["status"] == "pass"
    assert result["missing_fields"] == []


def test_missing_required_label_fails(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    body = "\n".join(f"{field}: filled" for field in subject.REQUIRED_FIELDS if field != "Receipt target")
    receipt = write_receipt(repo / "receipt.md", body)

    result = subject.check_receipt(receipt)

    assert result["status"] == "fail"
    assert result["missing_fields"] == ["Receipt target"]


def test_empty_required_label_fails(tmp_path, monkeypatch, capsys) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    lines = []
    for field in subject.REQUIRED_FIELDS:
        lines.append(f"{field}:" if field == "Handoff quality" else f"{field}: filled")
    receipt = write_receipt(repo / "receipt.md", "\n".join(lines))

    assert subject.main(["receipt-check", "--file", str(receipt)]) == 1

    output = capsys.readouterr().out.splitlines()
    assert output == ["mira_work_receipt=fail", "missing_field=Handoff quality"]


def test_ignores_unrelated_prose_and_non_receipt_fenced_code(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    receipt = write_receipt(
        repo / "receipt.md",
        f"""
Receipt target: filled
Primary user or stakeholder: filled
Process or decision improved: filled
Observable proof of usefulness: filled
Human review or handoff point: filled
Handoff quality: filled
What changed: filled
Evidence or artifacts used: filled
Decisions made: filled
Risks or limits: filled
Landed-state snapshot digest: filled
Active transition: filled
Prior transition disposition: filled
Landed-state result: filled
```
Next owner can act without rediscovery: this code fence should not count
```
Unrelated prose should not backfill the fenced field.
""",
    )

    result = subject.check_receipt(receipt)

    assert result["status"] == "fail"
    assert result["missing_fields"] == ["Next owner can act without rediscovery"]


def test_parses_fenced_mira_work_completion_template(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    receipt = write_receipt(
        repo / "receipt.md",
        f"""
```text
Mira Work completion:
{complete_inline_receipt()}
```
""",
    )

    result = subject.check_receipt(receipt)

    assert result["status"] == "pass"


def test_receipt_check_ignores_fenced_mira_work_preflight_template(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    receipt = write_receipt(
        repo / "receipt.md",
        f"""
```text
Mira Work preflight:
{complete_inline_preflight()}
```
""",
    )

    result = subject.check_receipt(receipt)

    assert result["status"] == "fail"
    assert result["missing_fields"] == list(subject.REQUIRED_FIELDS)


def test_rejects_paths_outside_repository_and_non_markdown_files(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path / "repo")
    outside = write_receipt(tmp_path / "outside.md", complete_inline_receipt())
    text_file = write_receipt(repo / "receipt.txt", complete_inline_receipt())

    assert subject.main(["receipt-check", "--file", str(outside)]) == 2
    assert subject.main(["receipt-check", "--file", str(text_file)]) == 2


def test_json_output_is_parseable_and_authority_free(tmp_path, monkeypatch, capsys) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    receipt = write_receipt(repo / "receipt.md", complete_inline_receipt())

    assert subject.main(["receipt-check", "--file", str(receipt), "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["schema_version"] == subject.SCHEMA_VERSION
    assert output["status"] == "pass"
    assert output["authority_effect"] == "none"
    assert output["required_fields"] == list(subject.REQUIRED_FIELDS)
    assert output["present_fields"] == list(subject.REQUIRED_FIELDS)
    assert output["missing_fields"] == []


def test_complete_inline_preflight_passes(tmp_path, monkeypatch, capsys) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(repo / "preflight.md", complete_inline_preflight())

    assert subject.main(["preflight-check", "--file", str(preflight)]) == 0
    assert capsys.readouterr().out.splitlines() == ["mira_work_preflight=pass"]


def test_complete_multiline_preflight_passes(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(
        repo / "preflight.md",
        "\n".join(
            f"**`{field}`:**\n  - filled over multiple lines\n  - with detail"
            for field in subject.PREFLIGHT_FIELDS
        ),
    )

    result = subject.check_preflight(preflight)

    assert result["status"] == "pass"
    assert result["check_type"] == "preflight"
    assert result["missing_fields"] == []


def test_preflight_passes_when_advisory_fields_are_absent(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(repo / "preflight.md", complete_inline_preflight())

    result = subject.check_preflight(preflight)

    assert result["status"] == "pass"
    assert result["advisory_fields"] == list(subject.PREFLIGHT_ADVISORY_FIELDS)
    assert result["present_advisory_fields"] == []
    assert result["missing_advisory_fields"] == list(subject.PREFLIGHT_ADVISORY_FIELDS)


def test_preflight_counts_present_inline_advisory_fields(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(
        repo / "preflight.md",
        f"{complete_inline_preflight()}\n{complete_inline_preflight_advisory()}",
    )

    result = subject.check_preflight(preflight)

    assert result["status"] == "pass"
    assert result["present_advisory_fields"] == list(subject.PREFLIGHT_ADVISORY_FIELDS)
    assert result["missing_advisory_fields"] == []


def test_missing_required_preflight_label_fails(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    body = "\n".join(f"{field}: filled" for field in subject.PREFLIGHT_FIELDS if field != "Worker or model lane")
    preflight = write_receipt(repo / "preflight.md", body)

    result = subject.check_preflight(preflight)

    assert result["status"] == "fail"
    assert result["missing_fields"] == ["Worker or model lane"]


def test_empty_required_preflight_label_fails(tmp_path, monkeypatch, capsys) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    lines = []
    for field in subject.PREFLIGHT_FIELDS:
        lines.append(f"{field}:" if field == "Data sensitivity and exclusions" else f"{field}: filled")
    preflight = write_receipt(repo / "preflight.md", "\n".join(lines))

    assert subject.main(["preflight-check", "--file", str(preflight)]) == 1

    output = capsys.readouterr().out.splitlines()
    assert output == ["mira_work_preflight=fail", "missing_field=Data sensitivity and exclusions"]


def test_preflight_advisory_label_does_not_backfill_empty_required_field(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    lines = []
    for field in subject.PREFLIGHT_FIELDS:
        lines.append(f"{field}:" if field == "Validation plan" else f"{field}: filled")
    lines.append("Constraint attacked: manual rediscovery before every handoff")
    preflight = write_receipt(repo / "preflight.md", "\n".join(lines))

    result = subject.check_preflight(preflight)

    assert result["status"] == "fail"
    assert result["missing_fields"] == ["Validation plan"]
    assert result["present_advisory_fields"] == ["Constraint attacked"]


def test_preflight_ignores_unrelated_prose_and_non_preflight_fenced_code(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(
        repo / "preflight.md",
        f"""
Receipt target: filled
Primary user or stakeholder: filled
Role: filled
Authority boundary: filled
Worker or model lane: filled
Model/provider trust level: filled
Trusted instruction sources: filled
Credential or external-system exposure: filled
Data sensitivity and exclusions: filled
Validation plan: filled
Stop or rollback path: filled
Chunking and retry threshold: filled
Landed-state snapshot digest: filled
Active transition: filled
Prior transition disposition: filled
```
Human review or handoff point: this code fence should not count
```
Unrelated prose should not backfill the fenced field.
Constraint attacked: parser boundary should remain visible
""",
    )

    result = subject.check_preflight(preflight)

    assert result["status"] == "fail"
    assert result["missing_fields"] == ["Human review or handoff point"]
    assert result["present_advisory_fields"] == ["Constraint attacked"]


def test_preflight_advisory_labels_inside_unrelated_fenced_code_do_not_count(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(
        repo / "preflight.md",
        f"""
{complete_inline_preflight()}
```
Constraint attacked: this code fence should not count
Baseline: this code fence should not count
```
""",
    )

    result = subject.check_preflight(preflight)

    assert result["status"] == "pass"
    assert result["present_advisory_fields"] == []


def test_parses_fenced_mira_work_preflight_template(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(
        repo / "preflight.md",
        f"""
```text
Mira Work preflight:
{complete_inline_preflight()}
{complete_inline_preflight_advisory()}
```
""",
    )

    result = subject.check_preflight(preflight)

    assert result["status"] == "pass"
    assert result["present_advisory_fields"] == list(subject.PREFLIGHT_ADVISORY_FIELDS)


def test_preflight_check_ignores_fenced_mira_work_completion_template(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(
        repo / "preflight.md",
        f"""
```text
Mira Work completion:
{complete_inline_receipt()}
```
""",
    )

    result = subject.check_preflight(preflight)

    assert result["status"] == "fail"
    assert result["missing_fields"] == list(subject.PREFLIGHT_FIELDS)


def test_preflight_json_output_is_parseable_and_authority_free(tmp_path, monkeypatch, capsys) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(repo / "preflight.md", complete_inline_preflight())

    assert subject.main(["preflight-check", "--file", str(preflight), "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["schema_version"] == subject.SCHEMA_VERSION
    assert output["status"] == "pass"
    assert output["check_type"] == "preflight"
    assert output["authority_effect"] == "none"
    assert output["required_fields"] == list(subject.PREFLIGHT_FIELDS)
    assert output["present_fields"] == list(subject.PREFLIGHT_FIELDS)
    assert output["missing_fields"] == []
    assert output["advisory_fields"] == list(subject.PREFLIGHT_ADVISORY_FIELDS)
    assert output["present_advisory_fields"] == []
    assert output["missing_advisory_fields"] == list(subject.PREFLIGHT_ADVISORY_FIELDS)


def test_snapshot_reports_clean_landed_state_and_carriers(tmp_path: Path, git_cleanup) -> None:
    repo = snapshot_repo(tmp_path)
    state = tmp_path / "state"
    for relative in (
        "state/choice-history.sqlite3", "state/cadence.sqlite3",
        "state/mentorship.sqlite3", "archive/config.json",
    ):
        path = state / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    (state / "continuity/inbox").mkdir(parents=True)
    result = subject.landed_state_snapshot(
        repo.resolve(), environment={"MIRA_CORE_STATE_ROOT": str(state.resolve())},
    )
    assert result["dirty"]["count"] == 0
    assert result["ahead"] == 0 and result["behind"] == 0
    assert all(result["state"]["carriers"].values())
    assert len(result["snapshot_digest"]) == 64
    assert result["authority_effect"] == "none"


def test_snapshot_distinguishes_dirty_ahead_behind_diverged_and_detached(tmp_path: Path, git_cleanup) -> None:
    repo = snapshot_repo(tmp_path)
    (repo / "tracked.txt").write_text("dirty", encoding="utf-8")
    dirty = subject.landed_state_snapshot(repo.resolve(), environment={"MIRA_CORE_STATE_ROOT": str((tmp_path / "state").resolve())})
    assert dirty["dirty"]["tracked"] == 1
    git(repo, "checkout", "--", "tracked.txt")
    (repo / "ahead.txt").write_text("ahead", encoding="utf-8")
    git(repo, "add", "ahead.txt"); git(repo, "commit", "-m", "ahead")
    ahead = subject.landed_state_snapshot(repo.resolve(), environment={"MIRA_CORE_STATE_ROOT": str((tmp_path / "state").resolve())})
    assert ahead["ahead"] == 1 and ahead["behind"] == 0
    remote_tip = git(repo, "rev-parse", "HEAD")
    git(repo, "reset", "--hard", "HEAD~1")
    git(repo, "update-ref", "refs/remotes/origin/main", remote_tip)
    behind = subject.landed_state_snapshot(repo.resolve(), environment={"MIRA_CORE_STATE_ROOT": str((tmp_path / "state").resolve())})
    assert behind["behind"] == 1 and behind["ahead"] == 0
    (repo / "local.txt").write_text("local", encoding="utf-8")
    git(repo, "add", "local.txt"); git(repo, "commit", "-m", "local")
    diverged = subject.landed_state_snapshot(repo.resolve(), environment={"MIRA_CORE_STATE_ROOT": str((tmp_path / "state").resolve())})
    assert diverged["behind"] == 1 and diverged["ahead"] == 1
    git(repo, "checkout", "--detach")
    assert subject.landed_state_snapshot(repo.resolve(), environment={"MIRA_CORE_STATE_ROOT": str((tmp_path / "state").resolve())})["detached"]


def test_snapshot_handles_alternate_worktree_missing_remote_and_environment_conflict(tmp_path: Path, git_cleanup) -> None:
    repo = snapshot_repo(tmp_path)
    worktree = tmp_path / "worktree"
    git(repo, "worktree", "add", "-b", "codex/test", str(worktree))
    environment = {
        "MIRA_CORE_STATE_ROOT": str((tmp_path / "state").resolve()),
        "MIRA_CORE_CHOICE_DB": str((tmp_path / "new.sqlite3").resolve()),
        "NARRATIVE_CHOICE_DB": str((tmp_path / "old.sqlite3").resolve()),
    }
    result = subject.landed_state_snapshot(worktree.resolve(), remote="origin/missing", environment=environment)
    assert result["remote_available"] is False
    assert result["worktree_git_dir"] != result["git_common_dir"]
    assert result["environment"]["conflicts"][0]["canonical"] == "MIRA_CORE_CHOICE_DB"
