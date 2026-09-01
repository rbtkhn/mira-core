from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import archive_repair
import archive_repair_engine as engine
import backfill_section_list
import run_asr_repair_pilot


def fake_plan() -> engine.ArchiveRepairPlan:
    file_plan = engine.FileRepairPlan(
        path="archive/sources/geopolitics/sources/2026-07-31/source.md",
        host_slug="daniel-davis",
        repair_class="asr",
        input_sha256="1" * 64,
        output_sha256="2" * 64,
        changed=True,
        operations=("asr-repair",),
        changed_fields=("asr_repair_applied",),
        section_count_before=0,
        section_count_after=0,
        asr_rule_applications=(),
        processing_evidence=(),
        diff="diff",
        original_bytes=b"before",
        proposed_bytes=b"after",
    )
    return engine.ArchiveRepairPlan(
        manifest_id="manifest-test",
        manifest_sha256="3" * 64,
        repair_class="asr",
        resection=False,
        files=(file_plan,),
        plan_digest="4" * 64,
    )


@pytest.mark.parametrize(
    "arguments",
    (
        ["--path", "source.md", "--dry-run"],
        ["--class", "asr", "--path", "source.md"],
        ["--class", "asr", "--path", "source.md", "--execute"],
        ["--class", "asr", "--path", "source.md", "--dry-run", "--plan-digest", "x"],
        ["--class", "asr", "--path", "source.md", "--dry-run", "--resection"],
        ["--class", "body-merge", "--path", "source.md", "--dry-run"],
    ),
)
def test_invalid_invocation_exits_two(arguments: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        archive_repair.parse_args(arguments)
    assert error.value.code == 2


def test_dry_run_emits_stable_json(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    plan = fake_plan()
    observed = {}

    def build(paths, repair_class, **kwargs):
        observed["paths"] = list(paths)
        observed["class"] = repair_class
        return plan

    monkeypatch.setattr(archive_repair.engine, "build_plan", build)
    assert archive_repair.main(
        [
            "--class",
            "asr",
            "--path",
            "archive/sources/geopolitics/sources/2026-07-31/source.md",
            "--dry-run",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert observed["class"] == "asr"
    assert payload["plan_digest"] == plan.plan_digest
    assert payload["authority_effect"] == "none"


def test_execute_passes_reviewed_digest(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    plan = fake_plan()
    monkeypatch.setattr(archive_repair.engine, "build_plan", lambda *args, **kwargs: plan)
    observed = {}

    def apply(value, *, expected_digest):
        observed["digest"] = expected_digest
        return value.public(disposition="executed")

    monkeypatch.setattr(archive_repair.engine, "apply_plan", apply)
    assert archive_repair.main(
        [
            "--class",
            "asr",
            "--path",
            "archive/sources/geopolitics/sources/2026-07-31/source.md",
            "--execute",
            "--plan-digest",
            plan.plan_digest,
            "--format",
            "json",
        ]
    ) == 0
    assert observed["digest"] == plan.plan_digest
    assert json.loads(capsys.readouterr().out)["disposition"] == "executed"


def test_blocked_plan_returns_one(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(
        archive_repair.engine,
        "build_plan",
        lambda *args, **kwargs: (_ for _ in ()).throw(engine.ArchiveRepairError("blocked")),
    )
    assert archive_repair.main(
        ["--class", "asr", "--path", "source.md", "--dry-run"]
    ) == 1
    assert "archive repair blocked" in capsys.readouterr().err


@pytest.mark.parametrize("newline", ("\n", "\r\n"))
def test_heading_only_components_preserve_source_and_insert_one_heading(newline: str) -> None:
    source = newline.join(
        (
            "---",
            "host_slug: judging-freedom",
            "---",
            "",
            "# Ray McGovern",
            "",
            "Transcript body.",
            "",
        )
    )
    parsed = engine.heading_only_components(source)
    assert parsed is not None
    _, _, body, proposed = parsed
    assert proposed == source.replace(
        f"# Ray McGovern{newline}{newline}",
        f"# Ray McGovern{newline}{newline}## Transcript{newline}{newline}",
        1,
    )
    assert proposed.count("## Transcript") == 1
    assert "Transcript body." in body


@pytest.mark.parametrize("newline", ("\n", "\r\n"))
def test_heading_only_components_use_source_text_for_authored_work(newline: str) -> None:
    source = newline.join(
        (
            "---",
            "kind: substack-post",
            "source_form: newsletter",
            "host_slug: ritter",
            "---",
            "# Artificial Intelligence versus the OODA Loop",
            "",
            "Essay body.",
            "",
        )
    )
    parsed = engine.heading_only_components(source)
    assert parsed is not None
    _, _, body, proposed = parsed
    assert proposed == source.replace(
        f"# Artificial Intelligence versus the OODA Loop{newline}{newline}",
        f"# Artificial Intelligence versus the OODA Loop{newline}{newline}## Source Text{newline}{newline}",
        1,
    )
    assert proposed.count("## Source Text") == 1
    assert "## Transcript" not in proposed
    assert "Essay body." in body


def test_body_merge_components_uses_bounded_markers_and_preserves_frontmatter() -> None:
    source = "---\ntitle: Existing\nhost_slug: judging-freedom\n---\n## Transcript\n\n# Existing\n\nOld truncated body.\n"
    supplied = (
        "Existing - YouTube Transcripts:\n"
        "wrapper text\n"
        "Hi everyone, Judge Andrew Napolitano here for Judging Freedom.\n"
        "Recovered body.\n"
        "All the best. I look forward to it. Likewise.\n"
        "trailing wrapper\n"
    )
    parsed = engine.body_merge_components(source, supplied, expected_title="Existing")
    assert parsed is not None
    _, transcript, proposed = parsed
    assert "wrapper text" not in transcript
    assert "trailing wrapper" not in transcript
    assert "Old truncated body." not in proposed
    assert proposed.startswith("---\ntitle: Existing\nhost_slug: judging-freedom\n---\n## Transcript")
    assert proposed.endswith("All the best. I look forward to it. Likewise.\n")


def test_markdown_and_json_describe_same_plan() -> None:
    payload = fake_plan().public()
    markdown = engine.render_markdown(payload)
    assert payload["plan_digest"] in markdown
    assert payload["files"][0]["path"] in markdown
    assert "Authority effect: `none`" in markdown


def test_asr_adapter_requires_mode_and_fixes_class(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit) as error:
        run_asr_repair_pilot.parse_args(["--list-file", "targets.txt"])
    assert error.value.code == 2
    observed = {}
    def invoke(arguments):
        observed["arguments"] = arguments
        return 0

    monkeypatch.setattr(
        run_asr_repair_pilot.archive_repair,
        "main",
        invoke,
    )
    assert run_asr_repair_pilot.main(
        ["--list-file", "targets.txt", "--dry-run", "--format", "json"]
    ) == 0
    assert observed["arguments"][:2] == ["--class", "asr"]


def test_section_adapter_limits_targets_after_loading(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        backfill_section_list.engine,
        "read_list_file",
        lambda path: ["one.md", "two.md"],
    )
    observed = {}
    def invoke(arguments):
        observed["arguments"] = arguments
        return 0

    monkeypatch.setattr(
        backfill_section_list.archive_repair,
        "main",
        invoke,
    )
    assert backfill_section_list.main(
        ["--list-file", "targets.txt", "--limit", "1", "--dry-run"]
    ) == 0
    assert observed["arguments"][:4] == ["--class", "sectioning", "--path", "one.md"]
    assert "two.md" not in observed["arguments"]


def test_list_file_must_be_repository_relative(tmp_path: Path) -> None:
    with pytest.raises(engine.ArchiveRepairError, match="repository-relative"):
        engine.read_list_file(str(tmp_path / "targets.txt"), repo_root=tmp_path)
