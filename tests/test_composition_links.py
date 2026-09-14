import hashlib
import json

import pytest
import composition_links as links
import mira_memory
import tower
from test_tower import repo, entry, put


def compose(repo, origin, shelf="essays", name="idea", **extra):
    meta = {"schema": links.SCHEMA, "kind": links.KINDS[shelf], "summary": "Tests the concentration premise",
            "origins": [{"ref": origin, "sha256": hashlib.sha256((repo / origin).read_bytes()).hexdigest()}],
            "return_question": "Does decentralization change the estimate?", **extra}
    path = f"archive/{shelf}/{name}.md"
    put(repo, path, "# Thought\n<!-- mira-composition\n" + json.dumps(meta) + "\n-->\nQualified argument.")
    return path


@pytest.mark.parametrize("shelf", list(links.KINDS))
def test_round_trip(repo, shelf, monkeypatch):
    origin = tower.close(entry(), repo)["path"]
    before = (repo / origin).read_bytes()
    artifact = compose(repo, origin, shelf)
    metadata = links.inspect(repo, artifact)
    response = {"ref": artifact, "sha256": metadata["sha256"], "effect": "changed", "reason": "Counterexample narrows assessment"}
    tower.close(entry("later", date="2026-09-13", closed_at="2026-09-13T15:00:00+00:00",
                      composition_refs=[response], correction_links=[origin]), repo)
    assert (repo / origin).read_bytes() == before
    assert links.search(repo, notebook_ref=origin)["artifacts"][0]["path"] == artifact
    reverse = links.search(repo, artifact_ref=artifact)
    assert reverse["responses"][0]["effect"] == "changed"
    assert reverse["artifacts"][0]["origins"][0]["status"] == "matched"
    monkeypatch.setattr(mira_memory, "route_focus", lambda *a: pytest.fail("No Memory dependency"))
    context = tower.context("2026-09-12", "intelligence", repo)
    assert context["compositions"]
    assert any(r["temporal_status"] == "later-correction" for r in context["contributions"])
    (repo / artifact).write_text("Changed draft", encoding="utf-8")
    assert links.search(repo, artifact_ref=artifact)["responses"][0]["binding"]["status"] == "changed"
    with pytest.raises(ValueError, match="missing or changed"):
        tower.close(entry("third", composition_refs=[response]), repo, check=True)


def test_gaps_legacy_multiple_origins_and_budget(repo):
    one = tower.close(entry(), repo)["path"]
    two = tower.close(entry("two"), repo)["path"]
    path = compose(repo, one)
    meta = links.inspect(repo, path)
    origins = [{"ref": r, "sha256": hashlib.sha256((repo / r).read_bytes()).hexdigest()} for r in (one, two)]
    compose(repo, one, origins=origins)
    assert len(links.search(repo, artifact_ref=path)["artifacts"][0]["origins"]) == 2
    (repo / two).unlink()
    assert links.inspect(repo, path)["origins"][1]["status"] == "missing"
    put(repo, "archive/notes/legacy.md", "# no metadata")
    assert links.inspect(repo, "archive/notes/legacy.md")["status"] == "unlinked"
    put(repo, "archive/essays/bad.md", "<!-- mira-composition\ninvalid\n-->")
    result = links.search(repo, notebook_ref=one, limit=0)
    assert result["omitted"]
    assert links.search(repo, notebook_ref=one)["gaps"]
    with pytest.raises(ValueError):
        links.validate_responses(repo, [{"ref": path, "sha256": meta["sha256"], "effect": "changed", "reason": "test"}], [])


@pytest.mark.parametrize("ref", ["../outside.md", "C:/private/a.md", "/archive/essays/a.md", "archive/essays/../../../a.md", "archive/essays/a\\b.md"])
def test_unsafe(repo, ref):
    with pytest.raises(ValueError):
        links.resolve(repo, ref, True)


def test_memory_routes():
    assert mira_memory.route_focus("recover composition lineage")["recommended_owner"] == "strategy-notebook"
    assert mira_memory.route_focus("Study writing")["recommended_owner"] == "mira-memory"
    assert mira_memory.route_focus("recover composition lineage and recover journal")["routing_state"] == "needs-decomposition"
    assert mira_memory.route_focus("composition lineage record dream")["recommended_owner"] == "dream"


def test_validation_and_character_budget(repo):
    origin = tower.close(entry(), repo)["path"]
    path = compose(repo, origin)
    sha = links.inspect(repo, path)["sha256"]
    with pytest.raises(ValueError, match="corrected origin"):
        links.validate_responses(repo, [{"ref": path, "sha256": sha, "effect": "changed", "reason": "new premise"}], [])
    compose(repo, origin, summary="x" * 13000)
    result = links.search(repo, notebook_ref=origin)
    assert not result["artifacts"] and result["omitted"]
    compose(repo, origin, kind="letter")
    with pytest.raises(ValueError, match="shelf kind"):
        links.inspect(repo, path)
    compose(repo, origin, origins=[{"ref": origin, "sha256": "bad"}])
    with pytest.raises(ValueError, match="SHA-256"):
        links.inspect(repo, path)
