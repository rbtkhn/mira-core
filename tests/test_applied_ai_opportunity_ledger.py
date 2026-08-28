from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "build_applied_ai_opportunity_ledger.py"
SPEC = importlib.util.spec_from_file_location("build_applied_ai_opportunity_ledger", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_markdown_metadata() -> None:
    metadata = MODULE.parse_markdown_metadata(
        """# Example - Transcript

- Speaker: Nate Herk
- Channel: Nate Herk | AI Automation
- Date published: 2026-08-23
- Source ID: SS-NATE-HERK
"""
    )

    assert metadata["speaker"] == "Nate Herk"
    assert metadata["channel"] == "Nate Herk | AI Automation"
    assert metadata["date published"] == "2026-08-23"


def test_score_labels_detects_opportunity_types() -> None:
    labels = MODULE.score_labels(
        "Use Claude Code and Codex for browser automation, pricing, and client retainers.",
        MODULE.OPPORTUNITY_LEXICON,
    )

    assert "automation-service" in labels
    assert "browser-automation" in labels
    assert "pricing-and-packaging" in labels


def test_roi_handles_extracts_money_percent_and_time() -> None:
    handles = MODULE.roi_handles("Charge $100 to $500, save 20 hours a week, and target 10 to 20% ROI uplift.")

    assert "$100" in handles
    assert "10 to 20%" in handles
    assert "20 hours" in handles


def test_creator_and_type_filters_index_rows() -> None:
    rows = [
        {
            "opportunity_id": "AAO-20260823-001",
            "creator_context": {"creator": "Nate Herk"},
            "opportunity_type": ["automation-service", "pricing-and-packaging"],
        },
        {
            "opportunity_id": "AAO-20260821-002",
            "creator_context": {"creator": "Nate B. Jones"},
            "opportunity_type": ["model-tool-arbitrage"],
        },
    ]

    assert MODULE.creator_filters(rows) == {
        "Nate B. Jones": ["AAO-20260821-002"],
        "Nate Herk": ["AAO-20260823-001"],
    }
    assert MODULE.opportunity_type_filters(rows)["automation-service"] == ["AAO-20260823-001"]


def test_offer_map_entry_maps_curated_rows_and_defaults() -> None:
    mapped = MODULE.offer_map_entry("AAO-20260823-004")
    unmapped = MODULE.offer_map_entry("AAO-19000101-001")

    assert mapped["status"] == "mapped"
    assert mapped["rank"] == 1
    assert mapped["offer_name"] == "Constraint-to-Automation Sprint"
    assert mapped["source_row_ids"] == ["AAO-20260823-004"]
    assert unmapped["status"] == "not-mapped"
    assert unmapped["source_row_ids"] == []


def test_implementation_brief_entry_maps_top_offer_and_defaults() -> None:
    brief = MODULE.implementation_brief_entry("AAO-20260823-004")
    unmapped = MODULE.implementation_brief_entry("AAO-19000101-001")

    assert brief["status"] == "draft"
    assert brief["brief_id"] == "constraint-to-automation-sprint-v1"
    assert brief["offer_name"] == "Constraint-to-Automation Sprint"
    assert "Lead intake and follow-up" in brief["ideal_first_use_cases"]
    assert brief["related_artifacts"]["delivery_checklist"].endswith("constraint-to-automation-sprint-delivery-checklist.md")
    assert unmapped["status"] == "not-drafted"
    assert unmapped["delivery_steps"] == []


def test_render_markdown_includes_filters_and_table() -> None:
    payload = {
        "generated_at": "2026-08-28T00:00:00Z",
        "authority_boundary": "triage only",
        "opportunity_labels": ["automation-service"],
        "creator_filters": {"Nate Herk": ["AAO-20260823-001"]},
        "opportunity_type_filters": {"automation-service": ["AAO-20260823-001"]},
        "offer_map_filters": {"mapped": ["AAO-20260823-001"]},
        "rows": [
            {
                "opportunity_id": "AAO-20260823-001",
                "date_first_seen": "2026-08-23",
                "priority": "high",
                "creator_context": {"creator": "Nate Herk"},
                "opportunity_type": ["automation-service"],
                "buyer_or_user": ["small business"],
                "pain_point": ["lead handling"],
                "tool_stack": ["Claude Code"],
                "pricing_or_roi_signal": {"handles": ["$100"]},
                "offer_map": {
                    "status": "mapped",
                    "rank": 1,
                    "offer_name": "Constraint-to-Automation Sprint",
                    "primary_buyer": "Small business",
                    "core_pain": "Lead handling",
                    "delivery_shape": "Build one measured workflow.",
                    "pricing_model": "Fixed fee.",
                    "measurement_plan": "Compare before and after.",
                    "source_row_ids": ["AAO-20260823-001"],
                    "why_high_roi": "Measured workflow lift.",
                },
                "implementation_brief": {
                    "status": "draft",
                    "brief_id": "constraint-to-automation-sprint-v1",
                    "offer_name": "Constraint-to-Automation Sprint",
                    "purpose": "Turn one bottleneck into a measured workflow.",
                    "core_promise": "Measure whether the number moved.",
                    "best_buyers": ["Small business"],
                    "ideal_first_use_cases": ["Lead follow-up"],
                    "delivery_steps": ["Diagnose one constraint.", "Build the workflow."],
                    "offer_ladder": [{"stage": "Sprint", "shape": "One measured automation."}],
                    "measurement_plan": ["Baseline time per run"],
                    "go_no_go_filter": {"strong_yes": "Repeated and measurable."},
                    "innermost_loop_angle": "Detect, intervene, measure, retain.",
                    "related_artifacts": {
                        "delivery_checklist": "archive/sources/singularity/constraint-to-automation-sprint-delivery-checklist.md"
                    },
                    "authority_boundary": "Planning only.",
                },
                "source_refs": [{"path": "archive/source.md"}],
                "innermost_loop_refs": [],
                "disposition": "Extract concrete workflow.",
            }
        ],
    }

    rendered = MODULE.render_markdown(payload)

    assert "# Applied AI Opportunity Ledger" in rendered
    assert "- Nate Herk: `AAO-20260823-001`" in rendered
    assert "## Offer Map" in rendered
    assert "## Implementation Briefs" in rendered
    assert "Constraint-to-Automation Sprint" in rendered
    assert "delivery_checklist" in rendered
    assert "Baseline time per run" in rendered
    assert "| opportunity_id | date_first_seen | priority | creator |" in rendered
