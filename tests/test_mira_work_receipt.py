from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import mira_work_receipt as subject


def write_receipt(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def complete_inline_receipt() -> str:
    return "\n".join(f"{field}: filled" for field in subject.REQUIRED_FIELDS)


def complete_inline_preflight() -> str:
    return "\n".join(f"{field}: filled" for field in subject.PREFLIGHT_FIELDS)


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
```
Human review or handoff point: this code fence should not count
```
Unrelated prose should not backfill the fenced field.
""",
    )

    result = subject.check_preflight(preflight)

    assert result["status"] == "fail"
    assert result["missing_fields"] == ["Human review or handoff point"]


def test_parses_fenced_mira_work_preflight_template(tmp_path, monkeypatch) -> None:
    repo = set_repo_root(monkeypatch, tmp_path)
    preflight = write_receipt(
        repo / "preflight.md",
        f"""
```text
Mira Work preflight:
{complete_inline_preflight()}
```
""",
    )

    result = subject.check_preflight(preflight)

    assert result["status"] == "pass"


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
