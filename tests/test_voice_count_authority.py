from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOICES = ROOT / "narrative-geopolitics" / "voices"
MANIFEST = ROOT / "narrative-geopolitics" / "archive" / "source-manifest.json"


def manifest_sources() -> list[dict[str, object]]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return payload["sources"]


def test_descriptive_voice_documents_do_not_embed_live_corpus_totals() -> None:
    for readme in sorted(VOICES.glob("*/README.md")):
        value = readme.read_text(encoding="utf-8")
        assert "Imported source rows" not in value, readme
        assert "Central archive files" not in value, readme

    descriptive_paths = (
        VOICES / "README.md",
        VOICES / "pape" / "README.md",
        VOICES / "pape" / "authored-forecast-spine.md",
        VOICES / "pape" / "guest-pressure-tests.md",
    )
    stale_phrases = (
        "75-source",
        "75 imported sources",
        "58 authored forecast-mechanism sources",
        "17 guest interview pressure-test sources",
    )
    for path in descriptive_paths:
        value = path.read_text(encoding="utf-8")
        for phrase in stale_phrases:
            assert phrase not in value, path


def test_voice_source_index_totals_match_the_manifest() -> None:
    sources = manifest_sources()
    indexes = sorted(VOICES.glob("*/source-index.md"))
    assert indexes

    for index in indexes:
        slug = index.parent.name
        routed_sources = [
            source
            for source in sources
            if slug in source.get("voice_slugs", [])
        ]
        routed_paths = {source["local_path"] for source in routed_sources}
        value = index.read_text(encoding="utf-8")

        generic = re.search(
            r"^Corpus: (\d+) local route rows across (\d+) "
            r"central archive source files\.$",
            value,
            re.MULTILINE,
        )
        if generic:
            assert int(generic.group(1)) == len(routed_sources), index
            assert int(generic.group(2)) == len(routed_paths), index
            continue

        if slug != "pape":
            assert not re.search(r"^Corpus:", value, re.MULTILINE), index
            continue

        pape = re.search(
            r"^Corpus: (\d+) authored sources, (\d+) guest appearances, "
            r"(\d+) total imported sources\.$",
            value,
            re.MULTILINE,
        )
        assert pape, index
        authored, guest, total = (int(item) for item in pape.groups())
        assert authored + guest == total, index
        assert total == len(routed_sources), index
        assert total == len(routed_paths), index
