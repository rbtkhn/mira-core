from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("speaker_label_corpus", ROOT / "scripts" / "speaker_label_corpus.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules["speaker_label_corpus"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_explicit_speaker_markers_are_normalized_and_unknown_is_preserved() -> None:
    body = "Glenn: Welcome.\n\nChas Freeman: Thank you.\n\nA quoted passage without attribution."
    labeled, stats = MODULE.label_body(body, {"voice_slugs": ["freeman"]}, {"host": "Glenn Diesen", "guest": "Chas Freeman"})
    assert "**Glenn Diesen**: Welcome." in labeled
    assert "**Chas Freeman**: Thank you." in labeled
    assert "**Unknown**: A quoted passage without attribution." in labeled
    assert stats["unknown_turn_count"] == 1


def test_solo_transcript_uses_one_label_for_continuous_body() -> None:
    labeled, stats = MODULE.label_body(
        "First paragraph.\n\nSecond paragraph.",
        {"voice_slugs": ["mercouris"]},
        {"source_form": "solo", "host": "Alexander Mercouris"},
    )
    assert labeled.startswith("**Alexander Mercouris**:")
    assert labeled.count("**Alexander Mercouris**:") == 1
    assert stats["solo_format"] == "single-label-continuous"


def test_consecutive_explicit_turns_do_not_repeat_same_speaker() -> None:
    labeled, _ = MODULE.label_body(
        "Glenn Diesen: First.\n\nGlenn Diesen: Second.",
        {"voice_slugs": ["freeman"]},
        {"host": "Glenn Diesen", "guest": "Chas Freeman"},
    )
    assert labeled.count("**Glenn Diesen**:") == 1


def test_selector_is_deterministic() -> None:
    rows = [{"date": "2025-01-01", "local_path": "b", "modality": "transcript"}, {"date": "2025-02-01", "local_path": "a", "modality": "transcript"}]
    manifest = {"sources": rows}
    assert MODULE.select_rows(manifest, 2) == MODULE.select_rows(manifest, 2)


def test_derivative_does_not_change_raw(tmp_path: Path) -> None:
    source = ROOT / "narrative-geopolitics/archive/sources/2025-05-31/source-glenn-diesen-chas-freeman-the-collapse-of-american-diplomacy-2025-05-31.md"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    row = {"local_path": str(source.relative_to(ROOT)).replace("\\", "/"), "voice_slugs": ["freeman"]}
    target, result = MODULE.derivative(row, tmp_path)
    target.parent.mkdir(parents=True)
    target.write_text(result["text"], encoding="utf-8")
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    provenance = result["provenance"]
    assert provenance["source_sha256"] == before
    assert provenance["labeling_method"]


def test_unresolved_relative_links_become_plain_text_in_derivative(tmp_path: Path) -> None:
    target = tmp_path / "derived.md"
    text = MODULE.sanitize_unresolved_links("[missing](missing.md#section) [web](https://example.com)", target)
    assert text == "missing [web](https://example.com)"
