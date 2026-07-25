from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "report_cross_voice_reference_density.py"


def load_module():
    spec = importlib.util.spec_from_file_location("cross_voice_density", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_manifest_routes_are_deduplicated_and_normalized() -> None:
    module = load_module()
    rows = module.manifest_rows("freeman")
    identities = [(row["path" if "path" in row else "local_path"], row["voice_slug"]) for row in rows]
    assert len(identities) == len(set(identities))
    assert all(row["voice_slug"] == row["voice_slug"].lower() for row in rows)


def test_report_contains_comparison_surfaces_and_is_deterministic() -> None:
    module = load_module()
    first = module.build_report()
    assert first == module.build_report()
    assert "# Historical-Reference Density Pilot" in first
    assert "## Voice comparison" in first
    assert "## Host/channel comparison" in first
    assert "## Transcript drilldown" in first
    assert "Confidence mix" in first
    assert "candidate historical-reference" in first
    assert "bounded validation pilot" in first


def test_confidence_classes_are_explicit() -> None:
    module = load_module()
    assert module.confidence("**Freeman:** The Bay of Pigs", "freeman") == "direct"
    assert module.confidence("**Host:** The Bay of Pigs", "freeman") == "strong-inferred"
    assert module.confidence("The Bay of Pigs was a precedent.", "freeman") == "provisional"
