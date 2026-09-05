import hashlib

import pytest

from scripts import thesis_track
from scripts.thesis_track import classify, evidence_spans


def test_default_definition_follows_domain_rename(tmp_path, monkeypatch):
    monkeypatch.setattr(thesis_track, "ROOT", tmp_path)
    domain = tmp_path / "narrative-geopolitics"
    definition = domain / "voices/mercouris/odessa-thesis-2026.md"
    definition.parent.mkdir(parents=True)
    definition.write_bytes(b"default thesis")
    before = thesis_track.pilot("mercouris/odessa")
    domain.rename(tmp_path / "geopolitics")
    after = thesis_track.pilot("mercouris/odessa")
    assert after["definition"] == tmp_path / "geopolitics/voices/mercouris/odessa-thesis-2026.md"
    assert after["definition_version"] == before["definition_version"]


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_explicit_definition_is_used_for_path_and_digest(tmp_path, monkeypatch, layout):
    monkeypatch.setattr(thesis_track, "ROOT", tmp_path)
    (tmp_path / layout).mkdir()
    definition = tmp_path / "custom.md"
    definition.write_bytes(b"custom thesis")
    monkeypatch.setitem(thesis_track.PILOTS["mercouris/odessa"], "definition", definition)
    result = thesis_track.pilot("mercouris/odessa")
    assert result["definition"] == definition
    assert result["definition_version"] == hashlib.sha256(b"custom thesis").hexdigest()[:16]


def test_forecast_classification_is_deterministic():
    claim_type, confidence, basis = classify("Odessa will become the final battle", "Russia could eventually capture the city.")
    assert claim_type == "forecast"
    assert confidence == "medium"
    assert basis == "forecast-language"


def test_evidence_span_is_bounded_and_line_addressable():
    text = "\n".join(["noise"] * 3 + ["Russia may blockade Odessa port and cut maritime access to Ukraine." ] + ["tail"] * 3)
    spans = evidence_spans(text, ["odessa", "port"])
    assert spans
    assert spans[0]["line_start"] <= spans[0]["line_end"]
    assert len(spans[0]["excerpt"]) <= 480


def test_title_only_candidate_is_not_accepted_by_closeout_guard():
    # The production closeout rejects low-confidence accepted candidates;
    # this test locks the classification boundary used by that guard.
    claim_type, confidence, basis = classify("Odessa", "Odessa")
    assert claim_type == "descriptive"
    assert confidence == "low"
    assert basis == "keyword-only"
