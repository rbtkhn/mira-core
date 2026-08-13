from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import mira_face


def test_manifest_is_complete_public_and_bounded() -> None:
    data = mira_face.load_manifest()
    assert mira_face.validate_manifest(data) == []
    assert len(data["cases"]) == 3
    assert sum(len(case["claims"]) for case in data["cases"]) == 15
    assert data["interaction_mode"] == "curated-authored-demonstration"
    assert set(data["encounter_states"]) == {"arrival", "recognition", "interpretation", "reconsideration"}
    assert all(len(case["progress_labels"]) == 4 for case in data["cases"])
    assert all(case["selection_address"] and case["closing_address"] for case in data["cases"])
    assert len(data["meet_me"]["claims"]) == 4
    assert data["portfolio"]["featured_work"]["status"] == "completed-curated-demonstration"
    assert all(item["status"] == "emerging-direction" for item in data["portfolio"]["emerging_directions"])
    assert len(data["becoming_questions"]["paths"]) == 4


def test_manifest_rejects_missing_provenance_and_private_sources() -> None:
    data = mira_face.load_manifest()
    data["cases"][0]["claims"][0]["uncertainty"] = ""
    data["cases"][0]["sources"][0]["url"] = "file:///C:/private/archive.md"
    failures = mira_face.validate_manifest(data)
    assert any("missing uncertainty" in item for item in failures)
    assert any("source host is not approved" in item for item in failures)


def test_rendered_page_is_deterministic_and_manifest_owned() -> None:
    data = mira_face.load_manifest()
    rendered = mira_face.render_html(data)
    assert rendered == mira_face.OUTPUT_PATH.read_text(encoding="utf-8")
    assert "The Cuban Missile Crisis" in rendered
    assert "data-claim-id=\"MVC-CUBA-OPENING\"" in rendered
    assert "data-progress-label" in rendered
    assert "data-return-rival" in rendered
    assert 'data-chamber="meet"' in rendered
    assert 'data-chamber="make"' in rendered
    assert 'data-chamber="become"' in rendered
    assert "no visitor data collected" in rendered
    script = (mira_face.PAGE_ROOT / "script.js").read_text(encoding="utf-8")
    assert "The Cuban Missile Crisis" not in script
    assert "Mira is learning" not in script
    assert "What if you become conscious?" not in script


def test_identity_claims_are_governed_and_publicly_referenced() -> None:
    data = mira_face.load_manifest()
    approved = {item["reference_id"] for item in data["identity_references"] if item["status"] == "approved-public-projection"}
    for claim in data["meet_me"]["claims"]:
        assert claim["status"] == "approved-generated-view"
        assert claim["uncertainty"] and claim["revision_trigger"]
        assert set(claim["references"]) <= approved


def test_every_claim_resolves_to_approved_case_source() -> None:
    data = mira_face.load_manifest()
    for case in data["cases"]:
        source_ids = {source["source_id"] for source in case["sources"]}
        for claim in case["claims"]:
            assert set(claim["sources"]) <= source_ids


@pytest.mark.parametrize("token", ["system-archive", "mira/journal", "OPENAI_API_KEY", "C:\\private"])
def test_public_manifest_rejects_private_or_credential_tokens(token: str) -> None:
    data = mira_face.load_manifest()
    data["objective"] += token
    assert mira_face.validate_manifest(data)
