"""Immutable private expectations and evidence-bound interpretive comparisons."""
from contextlib import nullcontext
from datetime import datetime, timezone
import json
import re

import library_journal as j
from bridge_handoff import locked

FIELDS = ('question', 'why_selected', 'expected_resolution', 'thread_id', 'selection')
RESULTS = ('supported', 'partly-supported', 'not-supported', 'not-yet-assessable')


def path(encounter, repo, root):
    return j.location(repo, root) / 'expectations' / (j.digest(encounter) + '.json')


def load(ref, repo, root=None):
    value = json.loads(path(ref['encounter_id'], repo, root).read_text(encoding='utf-8'))
    j.require(value['workspace'] == j.workspace(repo), 'expectation workspace mismatch')
    j.require(value['encounter_id'] == ref['encounter_id'], 'expectation identity mismatch')
    j.require(value['digest'] == j.digest({k: v for k, v in value.items() if k != 'digest'}) == ref['digest'], 'expectation digest mismatch')
    return value


def expect(payload, repo=j.REPO_ROOT, root=None, check=False):
    j.require(isinstance(payload, dict) and payload.get('save_requested', True) is True, 'expectation saving declined')
    j.require(not set(payload) & {'recorded_at', 'digest', 'workspace', 'schema_version', 'input_digest'}, 'checkpoint provenance is runtime-generated')
    for k in ('encounter_id', *FIELDS, 'challenge', 'prior_exposure'):
        j.require(j.text(payload.get(k)), f'expectation {k} required')
    j.require(re.fullmatch(r'LJT-[a-z0-9-]+', payload['thread_id']), 'stable question thread required')
    j.require(payload['selection'] in {'need', 'exploration', 'operator'}, 'invalid expectation selection')
    for k in ('work_ids', 'source_ids'):
        j.require(isinstance(payload.get(k), list) and payload[k] and all(j.text(s) for s in payload[k]), f'{k} handles required')
    target = path(payload['encounter_id'], repo, root)
    with (nullcontext() if check else locked(j.location(repo, root) / '.write-lock')):
        if target.exists():
            value = json.loads(target.read_text(encoding='utf-8'))
            value = load({'encounter_id': payload['encounter_id'], 'digest': value['digest']}, repo, root)
            j.require(value['input_digest'] == j.digest(payload), 'immutable expectation differs; use a new encounter')
            return {'status': 'already-recorded', 'checkpoint': value, 'writes_performed': False}
        j.require(not any(e['encounter_id'] == payload['encounter_id'] for e in j.entries(repo, root)), 'cannot backfill a completed encounter expectation')
        if payload.get('predecessor_checkpoint'):
            load(payload['predecessor_checkpoint'], repo, root)
        if check:
            return {'status': 'ready', 'writes_performed': False}
        value = {**payload, 'schema_version': 1, 'workspace': j.workspace(repo), 'recorded_at': datetime.now(timezone.utc).isoformat(), 'input_digest': j.digest(payload)}
        value['digest'] = j.digest(value)
        from library_growth import atomic_write
        atomic_write(target, json.dumps(value, ensure_ascii=False, indent=2))
        return {'status': 'saved', 'checkpoint': value, 'path': str(target), 'writes_performed': True}


def bind(entry, repo, root=None):
    ref = entry.get('expectation_ref')
    if not ref:
        j.require(entry.get('expectation_status', 'unrecorded') in {'unrecorded', 'retrospective'}, 'prospective expectation requires a checkpoint')
        entry.setdefault('expectation_status', 'retrospective' if entry.get('curiosity') else 'unrecorded')
        return entry
    value = load(ref, repo, root)
    j.require(ref['encounter_id'] == entry['encounter_id'], 'checkpoint belongs to another encounter')
    j.require(datetime.fromisoformat(value['recorded_at']) <= datetime.fromisoformat(entry['encounter_ended_at']), 'checkpoint was recorded after the encounter')
    c = entry.setdefault('curiosity', {})
    for k in FIELDS:
        j.require(k not in c or c[k] == value[k], f'conflicting checkpoint field: {k}')
        c[k] = value[k]
    j.require(value['thread_id'] in entry['thread_ids'], 'checkpoint thread mismatch')
    j.require(set(value['source_ids']) <= {p['source_id'] for p in entry['passages']}, 'checkpoint intended sources missing from encounter')
    entry['expectation_status'] = 'checkpoint-recorded; prior exposure declared, not independently verified'
    return entry


def check_review(entry):
    r = entry.get('curiosity_review')
    if r is None:
        return
    j.require(entry['kind'] == 'application' and isinstance(r, dict), 'curiosity review requires an application')
    for k in ('expected', 'observed', 'next_choice', 'explanation', 'boundary_test'):
        j.require(j.text(r.get(k)), f'curiosity review {k} required')
    j.require(r.get('disposition') in RESULTS, 'invalid curiosity review disposition')
    b = r.get('baseline', {})
    j.require(j.text(b.get('entry_id')) and type(b.get('version')) is int and j.text(b.get('digest')), 'exact baseline version and digest required')
    j.require(b['entry_id'] in entry['predecessor_ids'], 'baseline must be an explicit predecessor')
    j.require(r.get('application_ref') in entry['later_use_refs'], 'review requires separate application artifact')


def baseline(review, rows):
    ref = review['baseline']
    found = next((e for e in rows if e['entry_id'] == ref['entry_id'] and e['version'] == ref['version']), None)
    j.require(found and found['digest'] == ref['digest'], 'baseline version unavailable or digest mismatch')
    return found


def validate_review(entry, rows, repo, root=None):
    if not entry.get('curiosity_review'):
        return
    r = entry['curiosity_review']
    prior = baseline(r, rows)
    j.require(set(entry['thread_ids']) & set(prior['thread_ids']), 'review must reuse baseline thread')
    j.require(datetime.fromisoformat(entry['encounter_started_at']) >= datetime.fromisoformat(prior['encounter_ended_at']), 'application precedes reading completion')
    ref = prior.get('expectation_ref')
    j.require(r.get('expectation_ref') == ref, 'review must retain original checkpoint binding')
    if ref:
        cp = load(ref, repo, root)
        j.require(datetime.fromisoformat(entry['encounter_started_at']) >= datetime.fromisoformat(cp['recorded_at']), 'application precedes expectation')
    j.require(r['expected'] == prior.get('curiosity', {}).get('expected_resolution', 'not-recorded'), 'review rewrites original expectation')
    if r['expected'] == 'not-recorded':
        j.require(r['disposition'] == 'not-yet-assessable', 'unrecorded expectation cannot be assessed as supported or unsuccessful')
    old_refs = {b['ref'] for b in prior['artifacts']}
    j.require(r['application_ref'] not in old_refs, 'application reuses reading source or resulting note')
    current = next(b for b in entry['artifacts'] if b['ref'] == r['application_ref'])
    j.require(current['sha256'] not in {b['sha256'] for b in prior['artifacts']}, 'renamed reading artifact is not a separate application')


def view(rows, focus, selected_threads, repo, root=None):
    words = set(re.findall(r'\w+', focus.casefold()))
    candidates = []
    for e in rows:
        if not e.get('curiosity_review'):
            continue
        r = e['curiosity_review']
        score = len(words & set(re.findall(r'\w+', json.dumps(r).casefold())))
        if focus and not score and not set(e['thread_ids']) & set(selected_threads):
            continue
        findings, checkpoint = [], None
        try:
            prior = baseline(r, rows)
            if prior.get('expectation_ref'):
                cp = load(prior['expectation_ref'], repo, root)
                checkpoint = {k: cp[k] for k in ('question', 'expected_resolution', 'challenge', 'prior_exposure', 'recorded_at', 'digest')}
            findings.extend(j.gaps(prior, repo))
        except (OSError, ValueError, KeyError) as error:
            findings.append({'status': 'unavailable', 'reason': str(error)})
        candidates.append({'entry_id': e['entry_id'], 'version': e['version'], 'digest': e['digest'], 'mode': e['application_mode'], 'review': r, 'checkpoint': checkpoint, 'findings': findings + j.gaps(e, repo), 'score': score, 'recorded_at': e['recorded_at']})
    candidates.sort(key=lambda e: (e['score'], e['recorded_at'], e['entry_id'], e['version']), reverse=True)
    return {'comparisons': candidates[:3], 'omitted': [{k: e[k] for k in ('entry_id', 'version', 'digest')} for e in candidates[3:]], 'authority': 'interpretive comparisons; not recursive-learning evidence'}


def report(rows, first, last, repo, root=None):
    import journal_calendar as calendar
    counts = {k: 0 for k in RESULTS}
    heads = {e['entry_id']: e for e in rows}
    reviews = []
    for e in heads.values():
        if e.get('curiosity_review') and e.get('application_mode') == 'subsequent-use' and first <= calendar.current_date(datetime.fromisoformat(e['recorded_at'])) <= last:
            counts[e['curiosity_review']['disposition']] += 1
            reviews.append({'entry_id': e['entry_id'], 'version': e['version'], 'digest': e['digest'], 'review': e['curiosity_review']})
    checkpoints, gaps = [], []
    folder = j.location(repo, root) / 'expectations'
    if folder.exists():
        for p in sorted(folder.iterdir()):
            if p.suffix != '.json':
                continue
            try:
                cp = json.loads(p.read_text(encoding='utf-8'))
                cp = load({'encounter_id': cp['encounter_id'], 'digest': cp['digest']}, repo, root)
                if first <= calendar.current_date(datetime.fromisoformat(cp['recorded_at'])) <= last:
                    checkpoints.append({'encounter_id': cp['encounter_id'], 'digest': cp['digest'], 'path': str(p)})
            except (OSError, ValueError, KeyError) as error:
                gaps.append({'path': str(p), 'reason': str(error)})
    return {'recorded_expectations': len(checkpoints), 'checkpoints': checkpoints, 'subsequent_reviews_by_disposition': counts, 'reviews': reviews, 'gaps': gaps, 'pending_outcomes_are_failures': False}
