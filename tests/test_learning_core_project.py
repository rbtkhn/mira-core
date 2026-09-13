"""Focused integrity checks; semantic authority/education review remains manual."""
from pathlib import Path
import re

import pytest

import publication_validation as routing

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/learning-core"
DOCUMENTS = (
    "README.md", "intake.md", "learner-profile-template.md", "plan-template.md",
    "evidence-and-approval.md", "portfolio-and-review.md", "continuity.md",
    "resource-selection.md", "worked-examples.md", "source-map.md",
)
PIN = "ccf82892261137465329d3dc724ade6c7c82e22d"


@pytest.mark.parametrize("name", DOCUMENTS)
def test_exact_documents_require_domain_review(tmp_path, name):
    relative = f"projects/learning-core/{name}"
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_text("# Synthetic route fixture\n")
    report = routing.build_report([relative], repo_root=tmp_path)
    assert report["status"] == "manual-required"
    assert report["owners"] == ["learning-core/portable-methods"]
    assert report["manual_checks"] == [routing.MANUAL_LEARNING_CORE_CHECK]
    assert not report["blockers"]


@pytest.mark.parametrize("relative", (
    "projects/learning-core/private-profile.md",
    "projects/learning-core/approval-record.md",
    "projects/learning-core/family/intake.md",
    "projects/learning-core/intake.json",
    "projects/learning-core/README-private.md",
    "projects/learning-core/photograph.jpg",
    "projects/learning-core-other/README.md",
))
def test_neighbors_do_not_inherit_admission(tmp_path, relative):
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_text("Private-looking synthetic fixture only\n")
    assert routing.build_report([relative], repo_root=tmp_path)["status"] == "blocked"


def test_mixed_scope_does_not_hide_private_neighbor(tmp_path):
    for name in ("README.md", "family-responses.md"):
        target = tmp_path / "projects/learning-core" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Synthetic\n")
    report = routing.build_report([
        "projects/learning-core/README.md", "projects/learning-core/family-responses.md",
    ], repo_root=tmp_path)
    assert report["status"] == "blocked"
    assert report["blockers"]


@pytest.mark.parametrize("name", DOCUMENTS)
def test_package_links_resolve_without_private_store(name):
    source = PROJECT / name
    text = source.read_text(encoding="utf-8")
    for href in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if href.startswith("https://"):
            continue
        target = (source.parent / href.split("#")[0]).resolve()
        assert target.is_relative_to(ROOT), href
        assert target.is_file(), f"{name}: {href}"


def test_source_accounting_is_complete_unique_and_pinned():
    source_map = (PROJECT / "source-map.md").read_text(encoding="utf-8")
    rows = [line for line in source_map.splitlines() if " | `" in line]
    assert len(rows) == 60
    paths = set()
    for row in rows:
        cells = row.split(" | ")
        match = re.search(r"\[([^\]]+)\]\((https://[^)]+)\)", cells[0])
        assert match
        path, url = match.groups()
        assert path not in paths
        paths.add(path)
        assert url == f"https://github.com/rbtkhn/anyang-intelligence/blob/{PIN}/projects/learning-core/{path}"
        assert re.fullmatch(r"`[0-9a-f]{40}`", cells[1])
        assert cells[2] and cells[4].strip(" |")
        target = re.search(r"\]\(([^)]+)\)", cells[3]).group(1)
        assert target in DOCUMENTS
    assert {"README.md", "abigail-phase-2-onboarding-survey.md",
            "catalog/khan-kids-curated-catalog.yaml", "one-time-retainer-scope.md",
            "ai-interface-training/hold-after-review-exemplar.md"} <= paths


def test_blank_templates_have_no_populated_worksheet_rows():
    for name in ("learner-profile-template.md", "plan-template.md"):
        body = (PROJECT / name).read_text(encoding="utf-8")
        for line in body.splitlines():
            if line.startswith("- "):
                assert line.endswith(":"), f"Populated field: {name}: {line}"
        assert "outside Git" in body


def test_no_operational_configuration_was_imported():
    for name in DOCUMENTS:
        body = (PROJECT / name).read_text(encoding="utf-8")
        assert "$learner-intake" not in body
        assert "$business-intake" not in body
        assert "1000" not in body and "$1,000" not in body
    # Source-map filenames alone may name deferred integrations; they are not local files.
    assert not (PROJECT / "catalog").exists()
    assert not (PROJECT / "loop-examples").exists()
