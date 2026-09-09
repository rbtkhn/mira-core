import copy
from datetime import datetime, timezone
import json

import pytest

from test_library_journal import setup as journal_setup
import library_growth as growth
import library_journal as journal
from cognitive_context import note_search


@pytest.fixture
def setup(journal_setup):
    repo, root, entry = journal_setup
    registry = repo / 'archive/library/integrations/work-registry.json'
    registry.parent.mkdir(parents=True)
    registry.write_text(json.dumps({'works': [{'canonical_work_id': 'WORK-test', 'library_source_id': 'LIB-test', 'note_refs': []}]}))
    return repo, root, entry


def payload(entry, name='command', question='When does command change causation?'):
    e = copy.deepcopy(entry)
    e['curiosity'] = {'question': question, 'why_selected': 'Resolve a causal uncertainty', 'expected_resolution': 'Find a limiting case', 'thread_id': e['thread_ids'][0], 'selection': 'need', 'followups': []}
    return {'entry': e, 'note_disposition': 'A distinct question merits preservation', 'notes': [
        {'operation': 'create', 'path': f'archive/notes/library/{name}.md', 'title': name,
         'question': question, 'interpretation': 'Command coordinates action when recipients can act.',
         'limitation': 'The passage does not establish a general causal law.', 'next_test': 'Compare a case where command failed.',
         'work_ids': ['WORK-test'], 'source_ids': ['LIB-test'], 'inspected': [], 'novelty_reason': 'Distinct causal question'}]}


def inspected(p, repo):
    for n in p['notes']:
        n['inspected'] = [{'path': r['path'], 'sha256': r['sha256']} for r in note_search(n['question'], repo, work_ids=n['work_ids'])]


def test_many_notes_amendment_essay_rehearsal(setup):
    repo, root, e = setup
    p = payload(e)
    p['mode'] = 'rehearsal'
    p['notes'].append(payload(e, 'responsibility', 'Who bears responsibility?')['notes'][0])
    assert growth.closeout(p, repo=repo, root=root, check=True)['status'] == 'ready'
    assert not root.exists()
    first = growth.closeout(p, repo=repo, root=root)
    assert len(first['saves']) == 2
    assert growth.closeout(p, repo=repo, root=root)['status'] == 'already-recorded'
    a = copy.deepcopy(p)
    a['entry']['encounter_id'] += ':later'
    a['notes'] = [a['notes'][0]]
    n = a['notes'][0]
    n.update(operation='amend', expected_digest=growth.sha(repo / n['path']), change_reason='Earlier interpretation neglected recipient discretion.', interpretation='Recipients can redirect coordinated action.')
    inspected(a, repo)
    assert growth.closeout(a, repo=repo, root=root)['status'] == 'saved'
    body = (repo / n['path']).read_text(encoding='utf-8')
    assert 'Command coordinates' in body and 'Recipients can redirect' in body
    essay = repo / 'archive/essays/reflection.md'
    essay.parent.mkdir(parents=True)
    essay.write_text('<!-- mira-library-artifact\n' + json.dumps({'schema': 'library-artifact-v1', 'kind': 'essay', 'title': 'Responsibility and command', 'question': 'How are these connected?', 'work_ids': ['WORK-test'], 'sources': ['LIB-test']}) + '\n-->\n# Reflection\nA separately composed rehearsal essay.', encoding='utf-8')
    assert len(growth.search('', repo, ['WORK-test'])) == 3
    today = growth.journal_calendar.current_date().isoformat()
    assert growth.growth(today, today, repo=repo, root=root)['daily'][0]['new_notes'] == 0
    assert json.loads((repo / 'archive/library/integrations/work-registry.json').read_text())['works'][0]['note_refs'] == []


def test_partial_save_retry_and_actual_day_credit(setup, monkeypatch):
    repo, root, e = setup
    p = payload(e)
    real = journal.record
    def fail(payload, **kwargs):
        if not kwargs.get('check'):
            raise OSError('Journal unavailable')
        return real(payload, **kwargs)
    monkeypatch.setattr(journal, 'record', fail)
    assert growth.closeout(p, repo=repo, root=root)['status'] == 'partial'
    today = growth.journal_calendar.current_date().isoformat()
    report = growth.growth(today, today, repo=repo, root=root)
    assert report['daily'][0]['new_notes'] == 1
    assert len(report['pending_closeout_saves']) == 1
    monkeypatch.setattr(journal, 'record', real)
    assert growth.closeout(p, repo=repo, root=root)['status'] == 'saved'
    assert growth.growth(today, today, repo=repo, root=root)['daily'][0]['new_notes'] == 1
    assert len(journal.entries(repo, root)) == 1


def test_same_question_stale_amendment_and_no_note(setup):
    repo, root, e = setup
    p = payload(e)
    growth.closeout(p, repo=repo, root=root)
    p['entry']['encounter_id'] += ':2'
    p['notes'][0]['path'] = 'archive/notes/library/duplicate.md'
    inspected(p, repo)
    with pytest.raises(ValueError, match='same question'):
        growth.closeout(p, repo=repo, root=root)
    p['notes'][0].update(path='archive/notes/library/command.md', operation='amend', expected_digest='stale')
    with pytest.raises(ValueError, match='stale'):
        growth.closeout(p, repo=repo, root=root)
    p['notes'] = []
    p['note_disposition'] = 'No distinct idea warranted; preserve the question.'
    assert growth.closeout(p, repo=repo, root=root)['status'] == 'saved'
    assert len(growth.inventory(repo)['artifacts']) == 1


@pytest.mark.parametrize('field,value', [('save_requested', False), ('encounter_status', 'incomplete')])
def test_no_save_and_incomplete(setup, field, value):
    repo, root, e = setup
    p = payload(e)
    p['entry'][field] = value
    with pytest.raises(ValueError):
        growth.closeout(p, repo=repo, root=root)
    assert not (repo / 'archive/notes').exists()


def test_bounded_curiosity_and_legacy_context(setup):
    repo, root, e = setup
    journal.record(e, repo=repo, root=root)
    assert journal.context('', repo, root)['curiosity_history'][0]['curiosity'] == 'not-recorded'
    p = payload(e)
    p['entry']['encounter_id'] += ':2'
    c = p['entry']['curiosity']
    c['followups'] = [{'question': 'What failed?', 'status': 'parked', 'thread_id': e['thread_ids'][0]}]
    c['recommended_followup'] = 0
    p['notes'] = []
    assert growth.closeout(p, repo=repo, root=root)['status'] == 'saved'
    c['followups'] *= 4
    with pytest.raises(ValueError, match='three'):
        journal.check_input(p['entry'])


def test_changed_source_and_duplicate_inspection(setup):
    repo, root, e = setup
    p = payload(e)
    growth.closeout(p, repo=repo, root=root)
    second = payload(e, 'different', 'Where does causation fail?')
    second['entry']['encounter_id'] += ':2'
    with pytest.raises(ValueError, match='inspect'):
        growth.closeout(second, repo=repo, root=root)
    (repo / 'source.md').write_text('changed')
    with pytest.raises(ValueError, match='binding'):
        growth.closeout(second, repo=repo, root=root)


def test_growth_calendar_boundaries(setup, monkeypatch):
    repo, root, e = setup
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 9, 10, 3, 59, tzinfo=timezone.utc)
    monkeypatch.setattr(growth, 'datetime', Clock)
    growth.closeout(payload(e), repo=repo, root=root)
    r = growth.growth('2026-09-09', '2026-09-10', repo=repo, root=root)
    assert [d['new_notes'] for d in r['daily']] == [1, 0]
    assert r['monthly'] == {'2026-09': 1}


def test_completed_receipt_replay_ignores_current_source_drift(setup):
    repo, root, e = setup
    p = payload(e)
    first = growth.closeout(p, repo=repo, root=root)
    (repo / 'source.md').write_text('later changed source')
    assert growth.closeout(p, repo=repo, root=root)['saves'] == first['saves']


def test_failed_atomic_save_has_no_credit(setup, monkeypatch):
    repo, root, e = setup
    def fail(*args):
        raise OSError('disk unavailable')
    monkeypatch.setattr(growth, 'atomic_write', fail)
    assert growth.closeout(payload(e), repo=repo, root=root)['status'] == 'partial'
    today = growth.journal_calendar.current_date().isoformat()
    assert growth.growth(today, today, repo=repo, root=root)['daily'][0]['new_notes'] == 0


def test_substantive_application_counts_separately_from_retrieval(setup):
    repo, root, e = setup
    saved = growth.closeout(payload(e), repo=repo, root=root)
    journal.context('command', repo, root)
    today = growth.journal_calendar.current_date().isoformat()
    assert growth.growth(today, today, repo=repo, root=root)['distinct_notes_applied'] == 0
    a = copy.deepcopy(e)
    a.update(encounter_id='application-1', kind='application', application_mode='subsequent-use', predecessor_ids=[saved['entry_id']])
    artifact = repo / 'application.md'
    artifact.write_text('Separate case reveals where the earlier interpretation fails.')
    note = saved['saves'][0]
    a['artifacts'] += [{'ref': 'application.md', 'sha256': growth.sha(artifact)}, {'ref': note['path'], 'sha256': note['sha256']}]
    a['later_use_refs'] = ['application.md']
    a['note_applications'] = [{'idea_id': note['idea_id'], 'note_ref': note['path'], 'application_ref': 'application.md', 'effect': 'failed-transfer', 'reason': 'Recipients could not act independently.'}]
    journal.record(a, repo=repo, root=root)
    report = growth.growth(today, today, repo=repo, root=root)
    assert report['distinct_notes_applied'] == 1
    assert report['corrections'][0]['effect'] == 'failed-transfer'


def test_unknown_work_rejected_and_rename_does_not_recount(setup):
    repo, root, e = setup
    p = payload(e)
    p['notes'][0]['work_ids'] = ['unknown']
    with pytest.raises(ValueError, match='canonical work'):
        growth.closeout(p, repo=repo, root=root)
    p['notes'][0]['work_ids'] = ['WORK-test']
    growth.closeout(p, repo=repo, root=root)
    (repo / p['notes'][0]['path']).rename(repo / 'archive/notes/library/renamed.md')
    today = growth.journal_calendar.current_date().isoformat()
    assert growth.growth(today, today, repo=repo, root=root)['daily'][0]['new_notes'] == 1


def test_retry_after_first_of_two_notes_saved(setup, monkeypatch):
    repo, root, e = setup
    p = payload(e)
    p['notes'].append(payload(e, 'limits', 'What limits command?')['notes'][0])
    write = growth.atomic_write
    calls = []
    def fail_second(path, body):
        calls.append(path)
        if len(calls) == 2:
            raise OSError('second save interrupted')
        write(path, body)
    monkeypatch.setattr(growth, 'atomic_write', fail_second)
    partial = growth.closeout(p, repo=repo, root=root)
    assert partial['status'] == 'partial' and len(partial['saves']) == 1
    monkeypatch.setattr(growth, 'atomic_write', write)
    assert growth.closeout(p, repo=repo, root=root)['status'] == 'saved'
    assert len(growth.inventory(repo)['artifacts']) == 2
