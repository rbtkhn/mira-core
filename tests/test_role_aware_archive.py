from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("role_aware_archive", ROOT / "scripts" / "role_aware_archive.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_authored_publication_gets_author_role_and_publication_identity() -> None:
    row = {
        "date": "2026-07-08",
        "voice_slugs": ["pape"],
        "source_class": "authored forecast mechanism",
        "modality": "substack-post",
        "source_url": "https://escalationtrap.substack.com/p/example",
    }
    roles, status, basis = MODULE.infer_roles(row)
    assert roles == {"pape": ["author"]}
    assert status == {"pape": "confirmed"}
    assert basis == {"pape": "authored_source_class"}
    assert MODULE.publication_from_row(row) == {
        "publication_slug": "escalation-trap",
        "publication_name": "Escalation Trap",
        "publication_url": "https://escalationtrap.substack.com/",
    }


def test_explicit_publication_domains_are_resolved_without_promoting_platforms() -> None:
    row = {"source_class": "authored analysis", "modality": "article", "source_url": "https://responsiblestatecraft.org/trump-iran/"}
    assert MODULE.publication_from_row(row)["publication_slug"] == "responsible-statecraft"
    row = {"source_class": "authored newsletter", "modality": "substack-post", "source_url": "https://substack.com/@tritaparsi/p-123"}
    assert MODULE.publication_from_row(row)["publication_slug"] == "trita-parsi"
    row = {"source_class": "authored lecture", "modality": "youtube", "source_url": "https://www.youtube.com/watch?v=abc"}
    assert MODULE.publication_from_row(row) is None


def test_authored_nonpublication_gets_explicit_absence_reason() -> None:
    row = {"source_class": "authored lecture", "modality": "youtube", "source_url": "https://www.youtube.com/watch?v=abc"}
    assert MODULE.publication_absence_reason(row) == "youtube_container_not_publication"


def test_cristoforou_aliases_resolve_to_canonical_person() -> None:
    assert MODULE.canonical_slug("alex-christoforou") == "cristoforou"
    assert MODULE.canonical_slug("christoforou") == "cristoforou"


def test_guest_route_stays_person_and_host_separate() -> None:
    row = {
        "voice_slugs": ["barnes"],
        "source_class": "guest interview pressure test",
        "modality": "cleaned-transcript",
        "host_slug": "mario-nawfal",
    }
    roles, status, basis = MODULE.infer_roles(row)
    assert roles == {"barnes": ["guest"]}
    assert status == {"barnes": "inferred"}
    assert basis == {"barnes": "host_route_with_person_voice"}
    assert MODULE.validate_row({**row, "voice_roles": roles, "role_status": status, "role_basis": basis}) == []


def test_invalid_publication_voice_and_orphan_role_are_rejected() -> None:
    row = {
        "voice_slugs": ["pape"],
        "voice_roles": {"mario-nawfal": ["guest"], "pape": ["author"]},
        "role_status": {"pape": "confirmed", "mario-nawfal": "confirmed"},
        "role_basis": {"pape": "test", "mario-nawfal": "test"},
        "publication_slug": "pape",
    }
    failures = MODULE.validate_row(row)
    assert "voice_roles contains a person absent from voice_slugs" in failures
    assert "publication slug appears as a person voice" in failures


def test_publication_render_is_provenance_not_voice_claim() -> None:
    text = MODULE.render_publication(
        "example",
        "Example Publication",
        [{"date": "2026-07-01", "title": "Essay", "voice_slugs": ["pape"], "local_path": "narrative-geopolitics/archive/sources/2026-07-01/a.md"}],
    )
    assert "manifest-derived" in text
    assert "not a person voice record" in text
    assert "`pape`" in text


def test_speaker_edge_must_match_guest_role_and_be_labeled_for_strong_quote() -> None:
    from scripts.validate_speaker_edges import validate_edges

    rows = {"src-1": {"voice_roles": {"barnes": ["guest"], "mario-nawfal": ["host"]}}}
    good = [{"source": "src-1", "person": "barnes", "role": "guest", "turns": [23, 24], "attribution_status": "labeled", "quote_attribution": "strong"}]
    assert validate_edges(good, rows) == []
    bad = [{"source": "src-1", "person": "mario-nawfal", "role": "host", "turns": [23], "attribution_status": "inferred", "quote_attribution": "strong", "quoted_person": "barnes"}]
    assert any("host framing" in failure for failure in validate_edges(bad, rows))


def test_speaker_edge_cannot_create_new_person_route() -> None:
    from scripts.validate_speaker_edges import validate_edges

    edge = [{"source": "src-1", "person": "new-person", "role": "guest", "turns": [1], "attribution_status": "labeled"}]
    assert any("not a routed voice" in failure for failure in validate_edges(edge, {"src-1": {"voice_roles": {"barnes": ["guest"]}}}))
