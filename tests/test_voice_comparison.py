from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("voice_comparison", ROOT / "scripts" / "voice_comparison.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["voice_comparison"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_slug_and_explicit_voice_shape():
    assert MODULE.slug("Odessa / Odesa") == "odessa-odesa"


def test_candidate_lines_require_object_and_mechanism():
    rows = MODULE.candidate_lines(
        ["Russia may blockade Odessa", "", "The port is strategically important."],
        "Odessa",
    )
    assert rows and "blockade Odessa" in rows[0][1]


def test_report_has_three_quotes_per_voice_and_boundary():
    quotes = {
        "alpha": [MODULE.Quote("alpha", f"quote {i} Odessa", ROOT / "a.md", i, "host") for i in range(3)],
        "beta": [MODULE.Quote("beta", f"quote {i} Odessa", ROOT / "b.md", i, "host") for i in range(3)],
    }
    report = MODULE.render("Odessa", ["alpha", "beta"], quotes)
    assert report.count("> “") == 6
    assert "not independent corroboration" in report
    assert "reality-check" in report
