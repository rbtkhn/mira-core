from __future__ import annotations

import importlib.util
import sys


SPEC = importlib.util.spec_from_file_location("sectioning_v2", "scripts/sectioning_v2.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules["sectioning_v2"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_rejects_mid_sentence_boundary() -> None:
    paragraphs = ["The opening is complete.", "continuation starts mid-thought.", "A new topic begins here."]
    assert MODULE.propose(paragraphs, ["Opening", "New Topic"]) == []


def test_rejects_generic_labels() -> None:
    paragraphs = ["The opening is complete.", "A second topic begins here."]
    assert MODULE.propose(paragraphs, ["Show Open", "Segment 2"]) == []


def test_renders_complete_topic_sections() -> None:
    paragraphs = ["The opening is complete.", "Turning to the second topic, it begins here."]
    sections = MODULE.propose(paragraphs, ["Show Open — Energy", "Russia — Drones"])
    assert len(sections) == 2
    assert "### Russia — Drones" in MODULE.render(sections)


def test_does_not_split_ordinary_paragraphs_without_transition_cue() -> None:
    paragraphs = ["The opening is complete.", "This continues the same topic.", "A third paragraph continues it."]
    assert MODULE.propose(paragraphs, ["Opening", "Topic", "Third"]) == []


def test_accepts_structural_heading_cue() -> None:
    paragraphs = ["The opening is complete.", "### Iran Negotiations\nThe next topic begins here."]
    sections = MODULE.propose(paragraphs, ["Opening", "Iran Negotiations"])
    assert len(sections) == 2


def test_derives_topic_label_from_title_and_content() -> None:
    label = MODULE.derive_label("The discussion turns to drone attacks and energy routes.", "Ukraine Russia")
    assert label == "Drone Offensive"


def test_curated_labels_replace_keyword_bags() -> None:
    assert MODULE.derive_label("The drone offensive is fading.", "Ukraine Russia") == "Drone Offensive"
    assert MODULE.derive_label("Iran ceasefire negotiations have stalled.", "Iran Talks") == "Iran Ceasefire Negotiations"


def test_fallback_rejects_filename_and_frontmatter_boilerplate() -> None:
    assert MODULE.derive_label("The discussion continues.", "source-example-transcript-ingest-date-kind") == "Discussion Continues"
