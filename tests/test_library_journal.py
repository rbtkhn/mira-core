import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import library_journal as journal


@pytest.fixture
def setup(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    source = repo / "source.md"
    source.write_text("retained source", encoding="utf-8")
    entry = {
        "encounter_id": "session-1:reading-1", "kind": "reading", "encounter_status": "substantive-closed",
        "encounter_started_at": "2026-09-08T12:00:00+00:00", "encounter_ended_at": "2026-09-08T13:00:00+00:00",
        "title": "Command and causation", "narrative": "Private prose: command cannot explain all causation.\n",
        "occasion": "Question about command", "encounter": "Operator challenged Mira's analogy",
        "change": "Separate command from causation", "next_test": "Test on a later judgment", "coverage": "One passage and encounter",
        "authors": ["Tolstoy"], "thread_ids": ["LJT-causation"],
        "artifacts": [{"ref": "source.md", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}],
        "passages": [{"source_id": "LIB-test", "edition": "test", "language": "English", "boundary": "paragraph 1", "ref": "source.md"}],
        "attribution": [{"speaker": "operator", "contribution": "Challenged analogy", "source": "session-1"}],
        "unresolved_questions": ["When does command matter?"], "counterevidence": [], "later_use_refs": [], "predecessor_ids": [], "metaphors": [],
        "learning_changes": [{"proposal": "Distinguish command from causation", "rejection_condition": "Command independently explains outcome", "status": "revisable-trial", "stages": {s: {"status": "missing", "reason": "Not independently observed", "refs": []} for s in journal.STAGES}}],
    }
    return repo, tmp_path / "private", entry


def test_atomic_idempotent_record_and_rebuildable_index(setup):
    repo, root, e = setup
    assert journal.record(e, repo=repo, root=root, check=True)["status"] == "ready"
    assert not root.exists()
    first = journal.record(e, repo=repo, root=root)
    path = Path(first["path"])
    assert path.read_text() == e["narrative"]
    (journal.location(repo, root) / "index.json").unlink()
    assert journal.record(e, repo=repo, root=root)["status"] == "already-recorded"
    assert len(journal.entries(repo, root)) == 1
    assert (journal.location(repo, root) / "index.json").exists()
    assert list(repo.iterdir()) == [repo / "source.md"]
    assert "Private prose" not in json.dumps(journal.summary(repo, root))


def test_revision_preserves_old_reading_and_requires_digest(setup):
    repo, root, e = setup
    first = journal.record(e, repo=repo, root=root)
    e["narrative"] = "Correction: command can matter under specified conditions."
    with pytest.raises(ValueError, match="revise"):
        journal.record(e, repo=repo, root=root)
    with pytest.raises(ValueError, match="revise"):
        journal.record(e, repo=repo, root=root, revise="bad")
    second = journal.record(e, repo=repo, root=root, revise=first["digest"])
    assert second["version"] == 2
    ctx = journal.context("causation", repo, root)
    assert ctx["latest"][0]["narrative"] == e["narrative"]
    assert len(ctx["corrections_and_predecessors"]) == 1
    assert Path(first["path"]).is_file()


@pytest.mark.skipif(os.name != "nt", reason="Windows inherited Journal reader ACLs")
def test_recorded_versions_preserve_parent_acl_inheritance(setup):
    repo, root, entry = setup
    first = journal.record(entry, repo=repo, root=root)
    entry["narrative"] = "A corrected interpretation."
    second = journal.record(entry, repo=repo, root=root, revise=first["digest"])
    for receipt in (first, second):
        version = Path(receipt["path"]).parent
        script = (
            "$a=[System.IO.Directory]::GetAccessControl($env:MIRA_JOURNAL_ACL_TEST_PATH); "
            "if ($a.AreAccessRulesProtected) { throw 'Version blocks inherited readers' }; "
            "if (-not ($a.Access | Where-Object IsInherited)) { throw 'Missing inherited ACL' }"
        )
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            env={**os.environ, "MIRA_JOURNAL_ACL_TEST_PATH": str(version)},
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr or result.stdout


@pytest.mark.parametrize("field,value", [("encounter_status", "menu"), ("encounter_status", "incomplete"), ("save_requested", False), ("authors", ["Plato"])])
def test_refuses_non_encounters_and_out_of_pool(setup, field, value):
    repo, root, e = setup
    e[field] = value
    with pytest.raises(ValueError):
        journal.record(e, repo=repo, root=root)
    assert not root.exists()


def test_source_drift_is_reported_without_erasing_history(setup):
    repo, root, e = setup
    journal.record(e, repo=repo, root=root)
    (repo / "source.md").write_text("changed")
    assert journal.context("", repo, root)["evidence_gaps"][0]["status"] == "changed"
    with pytest.raises(ValueError, match="binding"):
        journal.record(e, repo=repo, root=root)


def test_bounded_older_threads_and_failures_survive(setup):
    repo, root, e = setup
    first = journal.record(e, repo=repo, root=root)
    for n in range(5):
        item = copy.deepcopy(e)
        item["encounter_id"] = f"session-{n+2}:reading"
        item["thread_ids"] = [f"LJT-other-{n}"]
        item["title"] = "Different topic"
        journal.record(item, repo=repo, root=root)
    ctx = journal.context("causation", repo, root)
    assert len(ctx["latest"]) == 3
    assert len(ctx["relevant_older_threads"]) <= 3
    assert first["entry_id"] in {x["entry_id"] for x in ctx["related"]}
    later = repo / "outcome.md"
    later.write_text("Later case rejected the analogy")
    e["encounter_id"] = "later-failure"
    e["predecessor_ids"] = [first["entry_id"]]
    e["learning_changes"][0]["status"] = "failed-transfer"
    with pytest.raises(ValueError, match="separate artifact"):
        journal.record(e, repo=repo, root=root)
    e["artifacts"].append({"ref": "outcome.md", "sha256": hashlib.sha256(later.read_bytes()).hexdigest()})
    e["later_use_refs"] = ["outcome.md"]
    journal.record(e, repo=repo, root=root)
    assert journal.context("causation", repo, root)["latest"][0]["learning_changes"][0]["status"] == "failed-transfer"


def test_journal_cannot_certify_recursive_learning(setup):
    repo, root, e = setup
    e["learning_changes"][0]["stages"]["later_outcome"]["status"] = "admitted"
    with pytest.raises(ValueError, match="unassessed"):
        journal.record(e, repo=repo, root=root)


def test_workspace_and_integrity_isolation(setup, tmp_path):
    repo, root, e = setup
    result = journal.record(e, repo=repo, root=root)
    assert journal.entries(tmp_path / "other-repo", root) == []
    Path(result["path"]).write_text("tampered")
    with pytest.raises(ValueError, match="companion"):
        journal.entries(repo, root)


def test_private_access_failure_is_not_empty_history(setup, monkeypatch):
    repo, root, e = setup
    journal.record(e, repo=repo, root=root)
    base = journal.location(repo, root)
    original = Path.iterdir

    def inaccessible(path):
        if path == base:
            raise PermissionError("private journal inaccessible")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", inaccessible)
    with pytest.raises(PermissionError):
        journal.context("", repo, root)
    assert journal.summary(repo, root)["status"] == "unavailable"


def test_missing_private_store_is_unavailable(setup):
    repo, root, _ = setup
    assert journal.summary(repo, root)["status"] == "unavailable"


@pytest.mark.parametrize("author", journal.CORE)
def test_all_core_eight_are_eligible(setup, author):
    repo, root, e = setup
    e["authors"] = [author]
    assert journal.record(e, repo=repo, root=root, check=True)["status"] == "ready"


def test_predecessor_recovery_cycle_and_limit(setup, monkeypatch):
    repo, root, e = setup
    first = journal.record(e, repo=repo, root=root)
    e["encounter_id"] = "child"
    e["thread_ids"] = ["LJT-child"]
    e["predecessor_ids"] = [first["entry_id"]]
    child = journal.record(e, repo=repo, root=root)
    original = next(x for x in journal.entries(repo, root) if x["entry_id"] == first["entry_id"])
    original["predecessor_ids"] = [child["entry_id"]]
    original["narrative"] += " correction"
    journal.record(original, repo=repo, root=root, revise=first["digest"])
    for n in range(4):
        item = copy.deepcopy(e)
        item.update(encounter_id=f"new-{n}", thread_ids=[f"LJT-new-{n}"], predecessor_ids=[])
        journal.record(item, repo=repo, root=root)
    ctx = journal.context(repo=repo, root=root, thread_ids=["LJT-child"])
    assert first["entry_id"] in {x["entry_id"] for x in ctx["predecessor_history"]}
    assert ctx["history_limits"]["cycles"]
    assert ctx["corrections_and_predecessors"]
    monkeypatch.setattr(journal, "HISTORY_LIMIT", 1)
    assert journal.context(repo=repo, root=root, thread_ids=["LJT-child", "LJT-causation"])["history_limits"]["truncated"]


def test_substantive_selection_and_explicit_budget(setup):
    repo, root, e = setup
    e["artifacts"][0]["metadata"] = "irrelevantkeyword"
    journal.record(e, repo=repo, root=root)
    for n in range(4):
        item = copy.deepcopy(e)
        item.update(encounter_id=f"new-{n}", thread_ids=[f"LJT-new-{n}"])
        journal.record(item, repo=repo, root=root)
    assert not journal.context("irrelevantkeyword", repo, root)["related"]
    ctx = journal.context("causation", repo, root, ["LJT-causation", "LJT-new-0", "LJT-new-1"])
    assert len(ctx["relevant_older_threads"]) == 3
    with pytest.raises(ValueError, match="three"):
        journal.context(repo=repo, root=root, thread_ids=["a", "b", "c", "d"])
    with pytest.raises(ValueError, match="unknown"):
        journal.context(repo=repo, root=root, thread_ids=["LJT-absent"])
    (repo / "source.md").unlink()
    gap = journal.context(repo=repo, root=root)["evidence_gaps"][0]
    assert gap["entry_id"] and gap["version"] == 1 and gap["status"] == "missing"


def test_application_requires_reused_thread_and_distinct_artifact(setup):
    repo, root, e = setup
    parent = journal.record(e, repo=repo, root=root)
    e.update(encounter_id="application", kind="application", application_mode="retrospective-rehearsal", predecessor_ids=[parent["entry_id"]], passages=[])
    e["later_use_refs"] = ["source.md"]
    with pytest.raises(ValueError, match="separate application"):
        journal.record(e, repo=repo, root=root)
    (repo / "application.json").write_text("review")
    e["artifacts"].append({"ref": "application.json", "sha256": hashlib.sha256(b"review").hexdigest()})
    e["later_use_refs"] = ["application.json"]
    e["thread_ids"] = ["LJT-wrong"]
    with pytest.raises(ValueError, match="reuse"):
        journal.record(e, repo=repo, root=root)
    e["thread_ids"] = ["LJT-causation"]
    journal.record(e, repo=repo, root=root)
    assert journal.record(e, repo=repo, root=root)["status"] == "already-recorded"
    e["learning_changes"][0]["status"] = "observed-later-use"
    with pytest.raises(ValueError, match="rehearsal"):
        journal.check_input(e)
