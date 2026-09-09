import copy
from datetime import datetime, timedelta, timezone
import json
import pytest

from test_library_growth import setup, payload, journal_setup
import library_expectations as x
import library_growth as g
import library_journal as j


def checkpoint(entry):
    return {'encounter_id': entry['encounter_id'], 'thread_id': entry['thread_ids'][0], 'question': 'Does command explain coordination?', 'why_selected': 'Distinguish mechanisms', 'selection': 'need', 'expected_resolution': 'Separate command from coordination', 'challenge': 'A case where command alone explains action', 'prior_exposure': 'Familiar work; this passage not yet interpreted in this encounter', 'work_ids': ['WORK-test'], 'source_ids': ['LIB-test']}


def reading(repo, root, e):
    cp = x.expect(checkpoint(e), repo, root)['checkpoint']
    p = payload(e)
    p['notes'] = []
    p['entry'].pop('curiosity')
    p['entry']['encounter_started_at'] = cp['recorded_at']
    p['entry']['encounter_ended_at'] = (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat()
    p['entry']['expectation_ref'] = {'encounter_id': cp['encounter_id'], 'digest': cp['digest']}
    g.closeout(p, repo=repo, root=root)
    return j.entries(repo, root)[-1], p


def application(repo, original, disposition='supported', mode='subsequent-use', suffix='1'):
    e = copy.deepcopy(original)
    for k in ('digest', 'version', 'entry_id', 'previous_digest', 'input_digest', 'recorded_at', 'workspace', 'schema_version', 'artifact_saves', 'reading_input_digest', 'reading_mode', 'note_disposition', 'expectation_ref', 'expectation_status', 'curiosity'):
        e.pop(k, None)
    e.update(encounter_id='application-' + suffix, kind='application', application_mode=mode, predecessor_ids=[original['entry_id']])
    e['encounter_started_at'] = (datetime.fromisoformat(original['encounter_ended_at']) + timedelta(seconds=1)).isoformat()
    e['encounter_ended_at'] = e['encounter_started_at']
    target = repo / ('application-' + suffix + '.md')
    target.write_text('Separate fixture case ' + suffix + ': recipients redirect action despite identical commands.')
    e['artifacts'].append({'ref': target.name, 'sha256': g.sha(target)})
    e['later_use_refs'] = [target.name]
    e['curiosity_review'] = {'baseline': {k: original[k] for k in ('entry_id', 'version', 'digest')}, 'expectation_ref': original['expectation_ref'], 'expected': original['curiosity']['expected_resolution'], 'observed': 'Recipients changed the effect of command.', 'next_choice': 'Read a contrasting case of concentrated authority.', 'disposition': disposition, 'explanation': 'The distinction helped separate two causal accounts.', 'boundary_test': 'Similar commands, different recipient discretion in a separate case.', 'application_ref': target.name}
    return e


def test_checkpoint_readonly_immutable_and_interrupted(setup):
    repo, root, e = setup
    p = checkpoint(e)
    assert x.expect(p, repo, root, check=True)['status'] == 'ready'
    assert not root.exists()
    first = x.expect(p, repo, root)
    assert x.expect(p, repo, root)['checkpoint'] == first['checkpoint']
    assert not j.entries(repo, root)
    assert not (repo / 'archive/notes').exists()
    p['expected_resolution'] = 'Changed expectation'
    with pytest.raises(ValueError, match='immutable'):
        x.expect(p, repo, root)


def test_no_save_and_no_historical_backfill(setup):
    repo, root, e = setup
    p = checkpoint(e)
    p['save_requested'] = False
    with pytest.raises(ValueError):
        x.expect(p, repo, root)
    assert not root.exists()
    j.record(e, repo=repo, root=root)
    p.pop('save_requested')
    with pytest.raises(ValueError, match='backfill'):
        x.expect(p, repo, root)


def test_binding_conflict_missing_checkpoint_and_no_expectation(setup):
    repo, root, e = setup
    cp = x.expect(checkpoint(e), repo, root)['checkpoint']
    p = payload(e)
    p['notes'] = []
    p['entry']['encounter_ended_at'] = (datetime.now(timezone.utc) + timedelta(seconds=2)).isoformat()
    p['entry']['expectation_ref'] = {'encounter_id': cp['encounter_id'], 'digest': cp['digest']}
    with pytest.raises(ValueError, match='conflicting'):
        g.closeout(p, repo=repo, root=root)
    p['entry'].pop('curiosity')
    p['entry']['expectation_ref']['digest'] = 'bad'
    with pytest.raises(ValueError, match='digest'):
        g.closeout(p, repo=repo, root=root)
    p['entry'].pop('expectation_ref')
    assert g.closeout(p, repo=repo, root=root)['status'] == 'saved'
    assert j.entries(repo, root)[0]['expectation_status'] == 'unrecorded'


@pytest.mark.parametrize('disposition', x.RESULTS)
def test_comparison_and_reporting_without_a_note(setup, disposition):
    repo, root, e = setup
    original, p = reading(repo, root, e)
    a = application(repo, original, disposition)
    j.record(a, repo=repo, root=root)
    ctx = j.context('coordination', repo, root)
    assert ctx['expectation_reviews']['comparisons'][0]['review']['disposition'] == disposition
    today = g.journal_calendar.current_date().isoformat()
    report = g.growth(today, today, repo=repo, root=root)
    assert report['expectation_review']['recorded_expectations'] == 1
    assert report['expectation_review']['subsequent_reviews_by_disposition'][disposition] == 1
    assert report['daily'][0]['new_notes'] == 0


def test_chronology_rewritten_expectation_and_renamed_source(setup):
    repo, root, e = setup
    original, _ = reading(repo, root, e)
    a = application(repo, original)
    a['encounter_started_at'] = e['encounter_started_at']
    with pytest.raises(ValueError, match='precedes'):
        j.record(a, repo=repo, root=root)
    a = application(repo, original)
    a['curiosity_review']['expected'] = 'Hindsight rewrite'
    with pytest.raises(ValueError, match='rewrites'):
        j.record(a, repo=repo, root=root)
    a = application(repo, original)
    target = repo / a['later_use_refs'][0]
    target.write_bytes((repo / 'source.md').read_bytes())
    a['artifacts'][-1]['sha256'] = g.sha(target)
    with pytest.raises(ValueError, match='renamed'):
        j.record(a, repo=repo, root=root)


def test_rehearsal_corrections_bounded_retrieval_and_gaps(setup):
    repo, root, e = setup
    original, _ = reading(repo, root, e)
    a = application(repo, original, mode='retrospective-rehearsal')
    first = j.record(a, repo=repo, root=root)
    a['curiosity_review'].update(disposition='not-supported', observed='The distinction did not explain the later case.', next_choice='Seek evidence about institutional constraints instead.')
    j.record(a, repo=repo, root=root, revise=first['digest'])
    for i in range(2, 5):
        j.record(application(repo, original, mode='retrospective-rehearsal', suffix=str(i)), repo=repo, root=root)
    ctx = j.context('coordination', repo, root)['expectation_reviews']
    assert len(ctx['comparisons']) == 3 and len(ctx['omitted']) == 2
    assert any(e.get('curiosity_review', {}).get('next_choice') == 'Seek evidence about institutional constraints instead.' for e in j.entries(repo, root))
    today = g.journal_calendar.current_date().isoformat()
    assert sum(g.growth(today, today, repo=repo, root=root)['expectation_review']['subsequent_reviews_by_disposition'].values()) == 0
    x.path(original['encounter_id'], repo, root).unlink()
    assert j.context('coordination', repo, root)['expectation_reviews']['comparisons'][0]['findings']


def test_parked_reopening_condition(setup):
    repo, root, e = setup
    c = payload(e)['entry']['curiosity']
    c.update(followups=[{'question': 'Which prerequisite is missing?', 'thread_id': e['thread_ids'][0], 'status': 'parked', 'reopening_condition': 'An independently documented contrary case becomes available.'}], recommended_followup=0)
    g.check_curiosity(c, e['thread_ids'])
    c['followups'][0]['status'] = 'open'
    with pytest.raises(ValueError, match='parked'):
        g.check_curiosity(c, e['thread_ids'])


def test_two_expectation_rehearsal_changes_recommendation(setup):
    repo, root, e = setup
    first, _ = reading(repo, root, e)
    j.record(application(repo, first, mode='retrospective-rehearsal'), repo=repo, root=root)
    second_entry = copy.deepcopy(e)
    second_entry['encounter_id'] += ':second'
    second, p = reading(repo, root, second_entry)
    unhelpful = application(repo, second, 'not-supported', 'retrospective-rehearsal', 'second')
    unhelpful['curiosity_review'].update(observed='The distinction added no explanatory value.', next_choice='Read institutional constraints before returning to command.', explanation='The case turned on incentives rather than coordination.')
    j.record(unhelpful, repo=repo, root=root)
    ctx = j.context('coordination', repo, root)['expectation_reviews']['comparisons']
    assert {r['review']['disposition'] for r in ctx} == {'supported', 'not-supported'}
    assert any('institutional constraints' in r['review']['next_choice'] for r in ctx)
    assert x.load(second['expectation_ref'], repo, root)['expected_resolution'] == second['curiosity']['expected_resolution']
    x.path(second['encounter_id'], repo, root).unlink()
    assert g.closeout(p, repo=repo, root=root)['status'] == 'already-recorded'


def test_provenance_cannot_be_supplied(setup):
    repo, root, e = setup
    p = checkpoint(e)
    p['recorded_at'] = '2020-01-01T00:00:00+00:00'
    with pytest.raises(ValueError, match='runtime-generated'):
        x.expect(p, repo, root)
