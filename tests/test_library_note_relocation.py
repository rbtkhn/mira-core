"""Relocation preserves artifact identity; it never renews an approval."""
import json
import shutil
from pathlib import Path

import pytest

import archive_library
import library_integration as li
import library_reasoning
import validate_repository
from repository_paths import (
    LIBRARY_NOTE_RELOCATIONS,
    canonical_repository_path,
    resolve_repository_path,
    validate_library_note_relocations,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def relocated(tmp_path):
    shutil.copytree(ROOT / "archive/library/integrations", tmp_path / "archive/library/integrations")
    shutil.copytree(ROOT / "archive/schemas", tmp_path / "archive/schemas")
    for old, new in LIBRARY_NOTE_RELOCATIONS.items():
        # Supports exercising the transaction before the real files are moved.
        source = ROOT / new if (ROOT / new).is_file() else ROOT / old
        target = tmp_path / new
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    registered = {
        ref
        for work in li.load_work_registry(ROOT)['works']
        for ref in work['note_refs']
        if ref not in LIBRARY_NOTE_RELOCATIONS
    }
    for ref in registered:
        source = ROOT / ref
        target = tmp_path / ref
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    li.note_link_index_repository(tmp_path, check=False)
    li.route_index_repository(tmp_path, archive_library.load_registry(), check=False)
    return tmp_path


def test_relocated_library_preserves_lineage_hashes_and_route_approvals(relocated):
    registry = archive_library.load_registry()
    assert li.validate_repository(relocated, registry) == []
    before = json.loads((ROOT / 'archive/library/integrations/route-index.json').read_text())
    after = li.build_route_index(relocated, registry)
    assert after == before
    result = li.reconcile_repository(relocated, registry)
    assert result['status'] == 'passed'
    assert result['writes_performed'] is False
    for old, new in LIBRARY_NOTE_RELOCATIONS.items():
        assert resolve_repository_path(relocated, old) == relocated / new
        assert resolve_repository_path(relocated, new) == relocated / new
        assert not (relocated / old).exists()


def test_changed_historical_note_fails_hash_and_approval_checks(relocated):
    old = 'archive/notes/2026-09-01-library-grotius-mare-liberum-integration-note-addendum-02.md'
    target = resolve_repository_path(relocated, old)
    target.write_bytes(target.read_bytes() + b'\nChanged historical text.\n')
    registry = archive_library.load_registry()
    assert any('historical predecessor note changed' in x for x in li.validate_repository(relocated, registry))
    routes = li.build_route_index(relocated, registry)
    assert any('review-binding-stale' in row['ineligibility_reasons'] for row in routes['routes'])


def test_missing_target_is_not_resolved_to_old_location(relocated):
    old, new = next(iter(LIBRARY_NOTE_RELOCATIONS.items()))
    (relocated / new).unlink()
    assert not resolve_repository_path(relocated, old).exists()
    assert li.validate_note_paths(relocated, [old])['status'] == 'failed'


def test_old_and_new_conflict_for_both_reference_forms(relocated):
    old, new = next(iter(LIBRARY_NOTE_RELOCATIONS.items()))
    shutil.copy2(relocated / new, relocated / old)
    for ref in (old, new):
        with pytest.raises(ValueError, match='Conflicting'):
            resolve_repository_path(relocated, ref)


@pytest.mark.parametrize('mapping', [
    {'archive/notes/a.md': '../outside.md'},
    {'archive/notes/a.md': 'archive/notes/library/../outside.md'},
    {'archive/notes/a.md': 'archive/notes/library/a.md', 'archive/notes/b.md': 'archive/notes/library/a.md'},
    {'archive/notes/a.md': 'archive/notes/library/b.md', 'archive/notes/library/b.md': 'archive/notes/library/c.md'},
])
def test_invalid_mapping_is_rejected(mapping):
    with pytest.raises(ValueError):
        validate_library_note_relocations(mapping)


def test_browsing_links_use_work_qualified_physical_paths(relocated):
    index = li.build_note_link_index(relocated)
    text = li.render_note_link_index(index)
    for row in index['links']:
        target = Path(canonical_repository_path(row['note_ref']))
        assert f'[{target.parent.name}/{target.name}]' in text
        assert f'../../notes/library/{target.parent.name}/{target.name}' in text


def test_relocation_table_covers_exact_registered_notes():
    refs = {ref for work in li.load_work_registry(ROOT)['works'] for ref in work['note_refs']}
    historical_refs = refs & set(LIBRARY_NOTE_RELOCATIONS)
    assert historical_refs == set(LIBRARY_NOTE_RELOCATIONS)
    assert len(historical_refs) == 17


def test_historical_and_generated_markdown_links_validate(relocated, monkeypatch):
    old = next(iter(LIBRARY_NOTE_RELOCATIONS))
    historical = relocated / 'historical.md'
    historical.write_text(f'[Historical note]({old})\n', encoding='utf-8')
    pages = [historical, relocated / 'archive/library/integrations/note-link-index.md',
             relocated / 'archive/library/integrations/route-index.md']
    monkeypatch.setattr(validate_repository, 'REPO_ROOT', relocated)
    monkeypatch.setattr(validate_repository, 'markdown_files', lambda: pages)
    monkeypatch.setattr(validate_repository, 'load_manifest', lambda: {'sources': []})
    assert validate_repository.markdown_link_failures() == []


def test_reasoning_resolves_historical_bindings_without_rewriting_them(relocated, monkeypatch):
    monkeypatch.setattr(library_reasoning, 'REPO_ROOT', relocated)
    old, new = next(iter(LIBRARY_NOTE_RELOCATIONS.items()))
    path = relocated / new
    import hashlib
    binding = {'ref': old, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    assert library_reasoning.validate_artifact_binding(binding, expected_path=path) == []
    assert binding['ref'] == old


def test_authorized_head_update_keeps_predecessor_bytes(relocated):
    work = next(w for w in li.load_work_registry(relocated)['works']
                if 'HOMER' in w['canonical_work_id'])
    ancestor = resolve_repository_path(relocated, work['note_refs'][0])
    before = ancestor.read_bytes()
    head = resolve_repository_path(relocated, work['revision_head_note_ref'])
    envelope = li.parse_note_envelope(head)
    envelope['status'] = 'provisional'
    li.write_note_envelope(head, envelope)
    assert ancestor.read_bytes() == before
    assert not (relocated / work['revision_head_note_ref']).exists()
    assert li.parse_note_envelope(head)['predecessor_note_ref'] == work['note_refs'][0]
