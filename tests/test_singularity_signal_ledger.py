from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "build_singularity_signal_ledger.py"
SPEC = importlib.util.spec_from_file_location("build_singularity_signal_ledger", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_inline_frontmatter_arrays() -> None:
    frontmatter = MODULE.parse_frontmatter(
        """---
title: "Sample"
panelists: ["Alex Wissner-Gross", "Dave Blundin"]
guests: []
---
body
"""
    )

    assert frontmatter["title"] == "Sample"
    assert frontmatter["panelists"] == ["Alex Wissner-Gross", "Dave Blundin"]
    assert frontmatter["guests"] == []


def test_participant_context_uses_episode_level_metadata() -> None:
    context = MODULE.participant_context(
        {
            "host": "Peter H. Diamandis",
            "panelists": ["Alex Wissner-Gross", "Dave Blundin"],
            "guests": ["Ramez Naam"],
            "speaker_status": "not diarized; participant roster inferred from opening",
        }
    )

    assert context == {
        "host": "Peter H. Diamandis",
        "panelists": ["Alex Wissner-Gross", "Dave Blundin"],
        "guests": ["Ramez Naam"],
        "speaker_status": "not diarized; participant roster inferred from opening",
        "attribution_status": "episode-level-context",
    }


def test_participant_context_falls_back_when_metadata_missing() -> None:
    assert MODULE.participant_context({"speaker": "Peter H. Diamandis and Moonshots panel"}) == {
        "host": None,
        "panelists": [],
        "guests": [],
        "speaker_status": "metadata-missing",
        "attribution_status": "episode-level-context-unavailable",
    }


def test_render_markdown_includes_participants_column() -> None:
    payload = {
        "generated_at": "2026-08-28T00:00:00Z",
        "authority_boundary": "test boundary",
        "mechanism_labels": ["agent-autonomy"],
        "participant_filters": {"Ramez Naam": ["SSL-20260815-001"]},
        "rows": [
            {
                "signal_id": "SSL-20260815-001",
                "date_first_seen": "2026-08-15",
                "priority": "high",
                "participant_context": {
                    "host": "Peter H. Diamandis",
                    "panelists": ["Alex Wissner-Gross", "Dave Blundin"],
                    "guests": ["Ramez Naam"],
                    "speaker_status": "not diarized",
                    "attribution_status": "episode-level-context",
                },
                "innermost_loop_refs": [],
                "moonshots_refs": [{"path": "archive/source.md"}],
                "mechanism": ["agent-autonomy"],
                "forecast_claims": {"candidate_handles": ["10x"]},
                "evidence_status": "forecast-pending",
                "next_check_date": "2026-09-14",
                "disposition": "Review candidate links.",
            }
        ],
    }

    rendered = MODULE.render_markdown(payload)

    assert "| signal_id | date_first_seen | priority | participants |" in rendered
    assert "Host: Peter H. Diamandis; Panel: Alex Wissner-Gross, Dave Blundin; Guest: Ramez Naam" in rendered
    assert "## Participant Filters" in rendered
    assert "- Ramez Naam: `SSL-20260815-001`" in rendered


def test_participant_filters_index_signal_ids_by_name() -> None:
    rows = [
        {
            "signal_id": "SSL-20260815-001",
            "participant_context": {
                "host": "Peter H. Diamandis",
                "panelists": ["Alex Wissner-Gross"],
                "guests": ["Ramez Naam"],
            },
        },
        {
            "signal_id": "SSL-20260818-001",
            "participant_context": {
                "host": "Peter H. Diamandis",
                "panelists": ["Alex Wissner-Gross"],
                "guests": ["Alvin Graylin"],
            },
        },
    ]

    assert MODULE.participant_filters(rows) == {
        "Alex Wissner-Gross": ["SSL-20260815-001", "SSL-20260818-001"],
        "Alvin Graylin": ["SSL-20260818-001"],
        "Peter H. Diamandis": ["SSL-20260815-001", "SSL-20260818-001"],
        "Ramez Naam": ["SSL-20260815-001"],
    }
