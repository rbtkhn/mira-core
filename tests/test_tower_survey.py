import json

import pytest
import tower
from test_tower import repo, entry, put, queue, land


def roster(repo):
    put(repo, "geopolitics/channels/channel-index.md",
        "| `daily-one` | One | `active` | role | shelf | 1 | 1 | `daily` | [open](https://www.youtube.com/@one) | first | last |\n"
        "| `weekly-two` | Two | `active` | role | shelf | 1 | 1 | `weekly` | [open](https://www.youtube.com/@two) | first | last |\n")


def receipt(repo):
    return tower.capture.write_browser_receipt(capture_date="2026-09-12",
        channel_slug="daily-one", channel_url="https://www.youtube.com/@one",
        observed_at="2026-09-12T15:00:00+00:00", observed_urls=[],
        no_qualifying_videos=True, notes="Videos and Live; channel search checked",
        access_mode="public", access_eligibility="eligible",
        queue_root=repo / "geopolitics/work/capture/youtube")


def binding(repo):
    c = tower.survey_coverage("2026-09-12", repo)
    return {**{k: c[k] for k in ("date", "status", "receipts", "gaps")},
            "channel_slugs": [r["slug"] for r in c["channels"]]}


def test_empty_backlog_is_not_survey(repo, tmp_path):
    roster(repo)
    tower.initialize(repo, tmp_path / "state")
    before = sorted(p.relative_to(repo) for p in repo.rglob("*") if p.is_file())
    plan = tower.survey_plan("2026-09-12", repo, tmp_path / "state")
    assert plan["survey"]["status"] == "incomplete"
    assert plan["backlog"]["status"] == "clear"
    assert [r["slug"] for r in plan["survey"]["channels"]] == ["daily-one"]
    assert plan["next_commands"][0][1:3] == ["mira-youtube", "daily-check"]
    assert before == sorted(p.relative_to(repo) for p in repo.rglob("*") if p.is_file())
    receipt(repo)
    assert tower.survey_coverage("2026-09-12", repo)["status"] == "complete"


@pytest.mark.parametrize("field,value", [("capture_date", "2026-09-11"),
    ("channel_slug", "other"), ("channel_url", "https://www.youtube.com/@other"),
    ("evidence_basis", "rss"), ("observed_at", "invalid"), ("notes", ""),
    ("observed_urls", ["not-a-video"]),
    ("access_context", {"mode": "authenticated", "eligibility": "ineligible"})])
def test_bad_evidence_cannot_complete(repo, field, value):
    roster(repo)
    path = receipt(repo)
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data))
    assert tower.survey_coverage("2026-09-12", repo)["status"] == "incomplete"


def test_binding_and_immutable_retry(repo):
    roster(repo)
    with pytest.raises(ValueError, match="requires a survey"):
        tower.close(entry(entry_mode="current-geopolitics"), repo, check=True)
    incomplete = binding(repo)
    assert tower.close(entry(survey=incomplete), repo, check=True)["status"] == "validated"
    receipt(repo)
    with pytest.raises(ValueError, match="bindings changed"):
        tower.close(entry(survey=incomplete), repo, check=True)
    value = entry(entry_mode="current-geopolitics", survey=binding(repo))
    assert tower.close(value, repo)["status"] == "saved"
    receipt_path = tower.capture.browser_receipt_path("2026-09-12", "daily-one", repo / "geopolitics/work/capture/youtube")
    receipt_path.unlink()
    assert tower.close(value, repo)["status"] == "reused"
    assert "YouTube Survey Coverage" in tower.notebook.contribution_text(tower.contributions(repo)[0])


def test_known_backlog_and_landed_route(repo, tmp_path):
    roster(repo)
    queue(repo, status="missing")
    state = tmp_path / "state"
    tower.initialize(repo, state)
    assert tower.survey_plan("2026-09-12", repo, state)["backlog"]["counts"] == {"acquisition-pending": 1}
    land(repo)
    rows = tower.survey_plan("2026-09-12", repo, state)["backlog"]["pending"]
    assert len(rows) == 1 and rows[0]["kind"] == "analysis-pending"
