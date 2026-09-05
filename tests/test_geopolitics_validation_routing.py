import importlib.util
from pathlib import Path
import sys
import subprocess
import stat

import pytest

import publication_validation as publication


@pytest.fixture
def rename_repo(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path)
    git("init", "-q")
    git("config", "core.autocrlf", "false")
    old = tmp_path / "narrative-geopolitics"
    old.mkdir()
    (old / "README.md").write_bytes(b"unchanged\n")
    git("add", "--", "narrative-geopolitics/README.md")
    old.rename(tmp_path / "geopolitics")
    yield tmp_path, git
    # Git objects are read-only on Windows; allow the owning test runner to
    # remove this temporary fixture without changing repository cleanup policy.
    for path in (tmp_path / ".git").rglob("*"):
        if path.is_file():
            path.chmod(stat.S_IREAD | stat.S_IWRITE)


def test_verified_rename_routes_unknown_content_without_mutation(rename_repo):
    root, git = rename_repo
    before = git("ls-files", "--stage")
    with pytest.raises(publication.RoutingError):
        publication.route_path("geopolitics/README.md", repo_root=root)
    report = publication.build_report(["geopolitics/README.md"], repo_root=root,
                                     rename_sources=["narrative-geopolitics/README.md"])
    assert report["status"] == "manual-required"
    assert report["commands"] == ["tools/run.ps1 test --mode full"]
    assert report["rename_evidence"][0]["authority_effect"] == "none"
    assert git("ls-files", "--stage") == before
    assert (root / "geopolitics/README.md").read_bytes() == b"unchanged\n"


@pytest.mark.parametrize("case", ["changed", "missing", "indexed-target", "source-present", "unindexed-source"])
def test_verified_rename_rejects_invalid_git_or_file_state(rename_repo, case):
    root, git = rename_repo
    target = root / "geopolitics/README.md"
    if case == "changed":
        target.write_bytes(b"new content\n")
    elif case == "missing":
        target.unlink()
    elif case == "indexed-target":
        git("add", "--", "geopolitics/README.md")
    elif case == "unindexed-source":
        git("update-index", "--force-remove", "--", "narrative-geopolitics/README.md")
    else:
        (root / "narrative-geopolitics").mkdir()
    report = publication.build_report(["geopolitics/README.md"], repo_root=root,
                                     rename_sources=["narrative-geopolitics/README.md"])
    assert report["status"] == "blocked"
    assert report["rename_evidence"] == []


@pytest.mark.parametrize("source,target", [
    ("narrative-geopolitics/README.md", "geopolitics/other.md"),
    ("archive/README.md", "geopolitics/README.md"),
    ("narrative-geopolitics/../README.md", "geopolitics/../README.md"),
    ("narrative-geopolitics/README.md", "C:/outside.md"),
])
def test_verified_rename_rejects_unsafe_or_mismatched_mapping(rename_repo, source, target):
    root, _ = rename_repo
    with pytest.raises(publication.RoutingError):
        publication.verified_rename(source, target, repo_root=root)


def test_verified_rename_rejects_duplicate_and_incomplete_pairs(rename_repo):
    root, _ = rename_repo
    for sources in ([], ["narrative-geopolitics/README.md"] * 2):
        with pytest.raises(publication.RoutingError):
            publication.build_report(["geopolitics/README.md"], repo_root=root,
                                     rename_sources=sources)


def test_verified_rename_rejects_duplicate_targets(rename_repo):
    root, _ = rename_repo
    report = publication.build_report(
        ["geopolitics/README.md"] * 2, repo_root=root,
        rename_sources=["narrative-geopolitics/README.md", "narrative-geopolitics/other.md"])
    assert report["status"] == "blocked"


def test_verified_rename_cli_requires_explicit_mapping():
    args = publication.parser().parse_args([
        "--path", "geopolitics/README.md",
        "--rename-source", "narrative-geopolitics/README.md", "--json"])
    assert args.rename_source == ["narrative-geopolitics/README.md"]


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("geopolitics_routing_validator", ROOT / "tools/validate_repo.py")
assert spec is not None and spec.loader is not None
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


@pytest.mark.parametrize(("suffix", "owner"), [
    ("voices/barnes/source-index.md", "narrative-geopolitics/archive"),
    ("voices/README.md", "narrative-geopolitics/voice-control"),
    ("voices/barnes/README.md", "narrative-geopolitics/voice-control"),
    ("voices/barnes/lens.md", "narrative-geopolitics/voice-control"),
    ("templates/synthesis.md", "geo-strategy/templates"),
    ("method/contract.md", "geo-strategy/method"),
    ("work/daily/2026-09-04/issue.md", "geo-strategy"),
    ("work/forecasts/forecast-ledger.md", "geo-strategy/forecast-ledger"),
    ("work/morning-brief/2026-09-04.md", "morning-brief"),
    ("work/morning-brief/2026-09-04.receipt.json", "morning-brief"),
    ("work/strategy-notebook/2026-09.md", "geo-strategy/strategy-notebook"),
    ("work/coverage/contracts/2026-09.json", "archive-audit/monthly-completeness"),
    ("work/coverage/receipts/2026-09.jsonl", "archive-audit/monthly-completeness"),
    ("work/capture/youtube/youtube-capture-policy.yml", "youtube-capture/geopolitics-policy"),
    ("work/capture/youtube/2026-09-04.jsonl", "youtube-capture/geopolitics-queue"),
    ("work/historical-reference/run-review-01.json", "historical-reference"),
    ("work/reality/claims/CLM-001.json", "reality-check"),
    ("work/verification/packets/VER-001/packet.md", "reality-check"),
    ("work/verification/legacy-inventory.json", "reality-check"),
])
def test_publication_alias_preserves_owner_checks_and_commands(
    tmp_path: Path, suffix: str, owner: str,
) -> None:
    old = publication.route_path("narrative-geopolitics/" + suffix, repo_root=tmp_path)
    new = publication.route_path("geopolitics/" + suffix, repo_root=tmp_path)
    assert old["owner"] == owner
    assert new == old


@pytest.mark.parametrize("prefix", ["narrative-geopolitics", "geopolitics"])
def test_report_and_historical_run_command_keep_physical_path(tmp_path: Path, prefix: str) -> None:
    relative = prefix + "/work/historical-reference/example.json"
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(b'{}\n')
    report = publication.build_report([relative], repo_root=tmp_path)
    assert report["paths"] == [relative]
    assert report["owners"] == ["historical-reference"]
    assert report["commands"] == [
        "python scripts/validate_historical_reference_taxonomy.py --run " + relative
    ]
    assert report["blockers"] == []
    assert target.read_bytes() == b'{}\n'
    assert sorted(p.name for p in tmp_path.iterdir()) == [prefix]


@pytest.mark.parametrize("suffix", [
    "work/daily/2026-09-04/issue.md",
    "work/daily/2026-09-04/judgment.json",
    "voices/barnes/source-index.md",
    "work/comparisons/example.md",
    "work/continuity/example.md",
])
def test_fast_test_selection_is_identical_for_both_names(suffix: str) -> None:
    routes = [validator.fast_route([validator.Change(" M", prefix + "/" + suffix)])
              for prefix in ("narrative-geopolitics", "geopolitics")]
    assert routes[0].effective_mode == "fast"
    assert routes[0].tests
    assert routes[1] == routes[0]
    mixed = validator.fast_route([
        validator.Change(" M", "narrative-geopolitics/" + suffix),
        validator.Change(" M", "geopolitics/" + suffix),
    ])
    assert mixed == routes[0]


@pytest.mark.parametrize("prefix", ["narrative-geopolitics", "geopolitics"])
@pytest.mark.parametrize("status", ["R ", " D", " T", "UU"])
def test_unsafe_git_status_still_requires_full(prefix: str, status: str) -> None:
    route = validator.fast_route([
        validator.Change(status, prefix + "/work/daily/2026-09-04/issue.md")
    ])
    assert route.effective_mode == "full"
    assert route.reasons[0].startswith("unsafe_git_change:")
    assert route.tests == ()


def test_actual_rename_not_treated_as_two_safe_modifications() -> None:
    route = validator.fast_route([validator.Change(
        "R ", "narrative-geopolitics/work/daily/2026-09-04/issue.md -> geopolitics/work/daily/2026-09-04/issue.md"
    )])
    assert route.effective_mode == "full"
    assert route.reasons[0].startswith("unsafe_git_change:")


@pytest.mark.parametrize("path", [
    "geopolitics-other/work/daily/2026-09-04/issue.md",
    "narrative-geopolitics-other/work/daily/2026-09-04/issue.md",
    "other/geopolitics/work/daily/2026-09-04/issue.md",
    "geopolitics/archive/sources/source.md",
    "geopolitics/unknown/file.md",
])
def test_alias_does_not_broaden_unrelated_routing(tmp_path: Path, path: str) -> None:
    with pytest.raises(publication.RoutingError) as error:
        publication.route_path(path, repo_root=tmp_path)
    assert str(error.value).endswith(path)
    assert validator.fast_route([validator.Change(" M", path)]).effective_mode == "full"


def test_shared_archive_keeps_its_distinct_route(tmp_path: Path) -> None:
    path = "archive/sources/geopolitics/sources/2026-09-04/source.md"
    route = publication.route_path(path, repo_root=tmp_path)
    assert route["owner"] == "narrative-geopolitics/archive"
    assert route["commands"] == ["tools/run.ps1 test --path tests/test_voice_count_authority.py"]
    fast = validator.fast_route([validator.Change(" M", path)])
    assert fast.effective_mode == "fast"
    assert fast.tests == (
        "tests/test_smart_intake.py", "tests/test_land_best_intake.py",
        "tests/test_role_aware_archive.py", "tests/test_voice_reconciliation.py",
    )
