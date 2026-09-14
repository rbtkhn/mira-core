from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import validate_repository as validation


def test_published_local_contracts_are_in_governed_inventory():
    expected = {'mira-gemini', 'mira-grok', 'mira-treasury', 'mira-youtube', 'tower'}
    assert expected <= validation.LOCAL_SKILLS
    root = Path(__file__).resolve().parents[1]
    for name in expected:
        assert (root / 'docs/skill-drafts' / name / 'SKILL.md').is_file()


def test_batch_triage_uses_established_runtime_without_obsolete_invocation():
    root = Path(__file__).resolve().parents[1]
    path = root / 'docs/skill-drafts/shared/batch-triage.md'
    assert validation.obsolete_guidance_failures([path], root) == []
    text = path.read_text(encoding='utf-8')
    assert 'established Python executable' in text
    assert 'Capture the exit' in text


def test_pilot_validation_does_not_crash_on_unrelated_living_work(monkeypatch, tmp_path):
    import library_integration as library
    (tmp_path / library.INTEGRATION_RELATIVE_ROOT).mkdir(parents=True)
    monkeypatch.setattr(library, 'EXPECTED_WORKS', 0)
    monkeypatch.setattr(library, 'EXPECTED_TOPICS', 0)
    manifest = {'schema_version': library.PILOT_MANIFEST_SCHEMA,
                'pilot_id': library.PILOT_ID, 'status': 'synthetic',
                'works': [], 'essay_artifacts_created': 0}
    monkeypatch.setattr(library, 'load_pilot_manifest', lambda root: manifest)
    reconciliation = {'works': [{'canonical_work_id': 'FICTIONAL-LIVING-WORK',
                                 'state': 'revision-due'}]}
    monkeypatch.setattr(library, 'reconcile_repository', lambda *a, **k: reconciliation)
    assert library.validate_pilot_contract(tmp_path, {'sources': []}) == []
    assert reconciliation['works'][0]['state'] == 'revision-due'
