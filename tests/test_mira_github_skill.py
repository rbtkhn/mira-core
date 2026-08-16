from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "docs" / "skill-drafts" / "mira-github" / "SKILL.md"


def read_skill() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_commit_reuses_matching_full_fingerprint() -> None:
    skill = " ".join(read_skill().split())
    for phrase in (
        "exactly one uncached Full gate",
        "same fingerprint with a cache hit",
        "evidence as reused rather than newly executed",
        "without repeating Full validation",
    ):
        assert phrase in skill
    for changed_input in (
        "repository bytes",
        "runtime or dependency inputs",
        "relevant environment",
        "result clarity",
    ):
        assert changed_input in skill


def test_hosted_state_is_distinct_and_uses_one_compact_watcher() -> None:
    skill = " ".join(read_skill().split())
    assert "hosted workflow state remains a separate claim" in skill
    assert "gh run watch <run-id> --repo OWNER/REPO --compact --exit-status --interval 15" in skill
    assert "Do not start parallel watchers" in skill
    assert "one structured `gh run view` query" in skill
    assert "exactly four jobs must pass" in skill


def test_powershell_refspec_examples_are_exact_and_unambiguous() -> None:
    skill = read_skill()
    assert "HEAD:refs/heads/<branch>" in skill
    assert "${sha}:refs/heads/<branch>" in skill
    assert "never write `$sha:refs/...`" in skill
    assert "Verify the resulting remote SHA" in skill


def test_push_preflight_preserves_authority_and_scope() -> None:
    skill = " ".join(read_skill().split())
    for phrase in (
        "gh auth status",
        "Confirm the target branch and refspec",
        "A direct `push` authorizes only the bounded push currently proven safe",
        "Never force-push, rebase, broaden the refspec, open a PR",
    ):
        assert phrase in skill
