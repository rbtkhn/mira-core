import hashlib
import json
import shutil
from pathlib import Path

import pytest

import innermost_loop_simulation as sim
import mira_journal_references as journal
from repository_paths import (
    NOTE_RELOCATIONS, SIMULATION_ROOT, LEGACY_SIMULATION_ROOT,
    canonical_repository_path, resolve_repository_path, validate_note_relocations,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def relocated_simulation(tmp_path, monkeypatch):
    bundle = ROOT / SIMULATION_ROOT
    if not bundle.exists():
        bundle = ROOT / LEGACY_SIMULATION_ROOT
    shutil.copytree(bundle, tmp_path / SIMULATION_ROOT)
    old = 'archive/notes/2026-08-10-innermost-loop-baseline.md'
    source = ROOT / NOTE_RELOCATIONS[old]
    if not source.exists():
        source = ROOT / old
    shutil.copy2(source, tmp_path / NOTE_RELOCATIONS[old])
    monkeypatch.setattr(sim, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(sim, 'RUN_ROOT', tmp_path / SIMULATION_ROOT)
    monkeypatch.setattr(sim, 'PROTOCOL_PATH', tmp_path / SIMULATION_ROOT / 'protocol.json')
    monkeypatch.setattr(sim, 'STATE_PATH', tmp_path / SIMULATION_ROOT / 'run-state.json')
    return tmp_path


def test_relocated_simulation_keeps_frozen_bytes_and_phase_state(relocated_simulation):
    before = {p: p.read_bytes() for p in sim.RUN_ROOT.rglob('*') if p.is_file()}
    assert sim.validate() == []
    state = sim.load_json(sim.STATE_PATH)
    assert {k: v['status'] for k,v in state['phases'].items()} == {
        'day-1': 'sealed', 'day-2': 'sealed', 'day-3': 'pending', 'day-10': 'pending'}
    for phase in ('day-1','day-2'):
        row=state['phases'][phase]
        assert row['response_path'].startswith(LEGACY_SIMULATION_ROOT + '/')
        assert sim.sha256_path(sim.resolve_repo_path(row['response_path'])) == row['sha256']
    assert all(p.read_bytes()==data for p,data in before.items())


def test_future_sealing_uses_new_path_without_resealing_history(relocated_simulation):
    response=sim.RUN_ROOT/'responses/day-3-test.md'
    response.write_text('Fixture-only future response.\n')
    before=sim.STATE_PATH.read_bytes()
    sim.seal_phase('day-3',response,'2026-09-05T00:00:00Z',check=True)
    assert sim.STATE_PATH.read_bytes()==before
    sim.seal_phase('day-3',response,'2026-09-05T00:00:00Z',check=False)
    after=sim.load_json(sim.STATE_PATH)
    prior=json.loads(before)
    assert after['phases']['day-3']['response_path'].startswith(SIMULATION_ROOT+'/')
    assert after['phases']['day-1']==prior['phases']['day-1']
    assert after['phases']['day-2']==prior['phases']['day-2']
    with pytest.raises(sim.SimulationError,match='already sealed'):
        sim.seal_phase('day-1',response,'2026-09-05T00:00:00Z',check=True)


def test_frozen_baseline_tampering_still_fails(relocated_simulation):
    baseline=sim.resolve_repo_path(sim.load_json(sim.PROTOCOL_PATH)['baseline']['path'])
    baseline.write_bytes(baseline.read_bytes()+b'changed')
    assert 'frozen baseline hash mismatch' in sim.validate()


def test_historical_journal_alias_reaches_new_lineage_note(tmp_path):
    path=journal.resolve_repo_evidence_path(tmp_path,'mira/notes/2026-08-15-from-civilization-memory-to-mira-core.md')
    assert path==tmp_path/'archive/notes/development/mira-architectural-lineage.md'


def test_simulation_prefix_is_bounded_and_rejects_conflicts(tmp_path):
    assert canonical_repository_path(LEGACY_SIMULATION_ROOT+'-other/x.json')==LEGACY_SIMULATION_ROOT+'-other/x.json'
    with pytest.raises(ValueError):
        canonical_repository_path(LEGACY_SIMULATION_ROOT+'/../escape.json')
    (tmp_path/LEGACY_SIMULATION_ROOT).mkdir(parents=True)
    (tmp_path/SIMULATION_ROOT).mkdir(parents=True)
    with pytest.raises(ValueError,match='Conflicting'):
        resolve_repository_path(tmp_path,LEGACY_SIMULATION_ROOT+'/protocol.json')


def test_all_subject_note_paths_map_once_and_reject_collisions(tmp_path):
    assert len(NOTE_RELOCATIONS)==28
    for old,new in NOTE_RELOCATIONS.items():
        assert canonical_repository_path(old)==new
        assert canonical_repository_path(new)==new
    old,new=next(iter(NOTE_RELOCATIONS.items()))
    (tmp_path/old).parent.mkdir(parents=True)
    (tmp_path/new).parent.mkdir(parents=True)
    (tmp_path/old).touch(); (tmp_path/new).touch()
    with pytest.raises(ValueError,match='Conflicting'):
        resolve_repository_path(tmp_path,old)
    with pytest.raises(ValueError):
        validate_note_relocations({old:'archive/notes/../escape.md'})
