"""Local reading closeout and disposable Library artifact views; no routing authority."""
from __future__ import annotations

import copy
from contextlib import nullcontext
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

import journal_calendar
import library_journal as journal
from bridge_handoff import locked

MARKER = re.compile(r'<!-- mira-library-artifact\n(.*?)\n-->', re.S)
REQUIRED = ('question', 'interpretation', 'limitation', 'next_test', 'title')
EFFECTIVE_DATE = date(2026, 9, 9)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path):
    matches = MARKER.findall(path.read_text(encoding='utf-8-sig'))
    journal.require(len(matches) <= 1, 'multiple artifact envelopes')
    return json.loads(matches[0]) if matches else None


def inventory(repo):
    rows, findings = [], []
    for shelf in ('notes', 'essays'):
        for p in sorted((repo / 'archive' / shelf).rglob('*.md')):
            if not p.resolve().is_relative_to((repo / 'archive' / shelf).resolve()):
                continue
            try:
                m = metadata(p)
                if m:
                    journal.require(m.get('schema') == 'library-artifact-v1', 'unsupported artifact schema')
                    journal.require(isinstance(m.get('work_ids'), list) and m['work_ids'], 'explicit work bindings required')
                    journal.require(m.get('kind') == ('note' if shelf == 'notes' else 'essay'), 'artifact shelf mismatch')
                    rows.append({**m, 'path': p.relative_to(repo).as_posix(), 'sha256': sha(p)})
            except (ValueError, KeyError, TypeError) as error:
                findings.append({'path': p.relative_to(repo).as_posix(), 'error': str(error)})
    return {'artifacts': rows, 'findings': findings, 'authority': 'inventory only; no operational eligibility', 'writes_performed': False}


def search(focus, repo, work_ids=(), limit=5):
    words = set(re.findall(r'\w+', focus.casefold())) - {'the', 'a', 'of', 'and', 'to'}
    rows = []
    for m in inventory(repo)['artifacts']:
        content = ' '.join(str(m.get(k, '')) for k in ('title', 'question', 'work_ids', 'sources'))
        score = len(words & set(re.findall(r'\w+', content.casefold())))
        overlap = len(set(work_ids) & set(m['work_ids']))
        if score or overlap or (not focus and not work_ids):
            rows.append({**m, 'score': score + 3 * overlap, 'full_read_required': True})
    return sorted(rows, key=lambda r: (-r['score'], r['path']))[:limit]


def check_curiosity(c, threads):
    journal.require(isinstance(c, dict), 'curiosity must be an object')
    for k in ('question', 'why_selected', 'expected_resolution'):
        journal.require(journal.text(c.get(k)), f'curiosity {k} required')
    journal.require(c.get('thread_id') in threads, 'curiosity must reuse an encounter thread')
    journal.require(c.get('selection') in {'need', 'exploration', 'operator'}, 'invalid question selection')
    follow = c.get('followups', [])
    journal.require(isinstance(follow, list) and len(follow) <= 3, 'at most three follow-up questions')
    for q in follow:
        if 'reopening_condition' in q:
            journal.require(q.get('status') == 'parked' and journal.text(q['reopening_condition']), 'reopening condition belongs to a parked question')
        journal.require(journal.text(q.get('question')) and q.get('status') in {'open', 'answered', 'reframed', 'parked'}, 'invalid question disposition')
        journal.require(q.get('thread_id') in threads, 'follow-up must bind an encounter thread')
    recommendation = c.get('recommended_followup')
    journal.require((not follow and recommendation is None) or (type(recommendation) is int and 0 <= recommendation < len(follow)), 'recommend one follow-up when present')


def atomic_write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.library-pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
            f.write(body)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def closeout(payload, *, repo=journal.REPO_ROOT, root=None, check=False):
    """Agent-authored judgments; atomic individual saves, recoverable journal closeout."""
    entry = copy.deepcopy(payload['entry'])
    # Completed closeout replay uses its immutable receipt, not current checkpoint files.
    completed = [e for e in journal.entries(repo, root) if e['encounter_id'] == entry['encounter_id']]
    if completed:
        journal.require(completed[-1].get('reading_input_digest') == journal.digest(payload), 'completed closeout differs; preserve receipt and use a new encounter or journal revision')
        return {'status': 'already-recorded', 'entry_id': completed[-1]['entry_id'], 'saves': completed[-1].get('artifact_saves', []), 'writes_performed': False}
    import library_expectations
    library_expectations.bind(entry, repo, root)
    journal.check_input(entry)
    journal.require(entry['kind'] == 'reading', 'closeout requires substantive reading')
    if entry.get('curiosity'):
        check_curiosity(entry['curiosity'], entry['thread_ids'])
    notes = payload.get('notes', [])
    journal.require(isinstance(notes, list) and len(notes) <= 3, 'at most three substantive notes per closeout')
    journal.require(journal.text(payload.get('note_disposition')), 'note disposition required, including no-note reason')
    input_digest = journal.digest(payload)
    with (nullcontext() if check else locked(journal.location(repo, root) / '.reading-lock')):
        previous = [e for e in journal.entries(repo, root) if e['encounter_id'] == entry['encounter_id']]
        if previous:
            journal.require(previous[-1].get('reading_input_digest') == input_digest, 'completed closeout differs; preserve receipt and use a new encounter or journal revision')
            return {'status': 'already-recorded', 'entry_id': previous[-1]['entry_id'], 'saves': previous[-1].get('artifact_saves', []), 'writes_performed': False}
        journal.require(not journal.gaps(entry, repo), 'passage/source bindings missing or changed')
        plans, seen, baselines = [], set(), {}
        existing = inventory(repo)
        journal.require(not existing['findings'], 'invalid Library artifact envelope; inspect inventory findings')
        from cognitive_context import note_search
        for n in notes:
            journal.require(n.get('operation') in {'create', 'amend'}, 'invalid note operation')
            journal.require(all(journal.text(n.get(k)) for k in REQUIRED), 'substantive note fields required')
            journal.require(n.get('work_ids') and all(journal.text(w) for w in n['work_ids']), 'explicit work bindings required')
            # Source IDs must actually occur in the admitted encounter passage bindings.
            source_ids = {p['source_id'] for p in entry['passages']}
            journal.require(n.get('source_ids') and set(n['source_ids']) <= source_ids, 'note requires encounter passage sources')
            registry_path = repo / 'archive/library/integrations/work-registry.json'
            journal.require(registry_path.is_file(), 'resolve canonical work registry before closeout')
            works = json.loads(registry_path.read_text(encoding='utf-8-sig'))['works']
            by_id = {w['canonical_work_id']: w for w in works}
            journal.require(set(n['work_ids']) <= set(by_id), 'unknown canonical work binding')
            journal.require(all(by_id[w]['library_source_id'] in n['source_ids'] for w in n['work_ids']), 'each work must bind an encounter passage source')
            rel = n['path']
            governed = {ref for w in works for ref in w.get('note_refs', [])}
            journal.require(rel not in governed, 'governed cognitive amendment requires Library Integration')
            p = (repo / rel).resolve()
            journal.require(not Path(rel).is_absolute() and p.is_relative_to((repo / 'archive/notes/library').resolve()) and p.suffix == '.md', 'unsafe note path')
            journal.require(p not in seen, 'duplicate target')
            seen.add(p)
            baselines[p] = sha(p) if p.exists() else None
            operation_id = journal.digest([entry['encounter_id'], rel, n['operation']])
            old = metadata(p) if p.exists() else None
            prior_event = next((e for e in (old or {}).get('saves', []) if e['operation_id'] == operation_id), None)
            if prior_event:
                journal.require(prior_event['input_digest'] == input_digest, 'retry changed saved content')
                journal.require(old['body_sha256'] == hashlib.sha256(MARKER.sub('', p.read_text(encoding='utf-8')).encode()).hexdigest(), 'saved note changed before retry')
                plans.append((p, None, prior_event))
                continue
            matches = note_search(n['question'], repo, work_ids=n['work_ids'])
            # A partially completed batch was already compared as one proposal.
            # Its own newly saved artifacts must not make an identical retry stale.
            own_saved_paths = {m['path'] for m in existing['artifacts'] if any(s.get('input_digest') == input_digest for s in m.get('saves', []))}
            matches = [m for m in matches if m['path'] not in own_saved_paths]
            inspected = n.get('inspected', [])
            journal.require(all(any(b.get('path') == m['path'] and b.get('sha256') == m['sha256'] for b in inspected) for m in matches), 'inspect strongest duplicate matches with current digests')
            journal.require(journal.text(n.get('novelty_reason')), 'explicit novelty/amendment judgment required')
            question_key = ' '.join(re.findall(r'\w+', n['question'].casefold()))
            if n['operation'] == 'create':
                journal.require(not p.exists(), 'create target already exists')
                journal.require(not any(' '.join(re.findall(r'\w+', m.get('question', '').casefold())) == question_key for m in existing['artifacts'] if m['kind'] == 'note'), 'same question requires amendment')
                journal.require(not any(e['question_key'] == question_key for _, _, e in plans), 'duplicate question within closeout')
            else:
                journal.require(old and old.get('kind') == 'note' and sha(p) == n.get('expected_digest'), 'stale or ungoverned amendment target')
                journal.require(' '.join(re.findall(r'\w+', old['question'].casefold())) == question_key, 'distinct question requires a new note')
                journal.require(journal.text(n.get('change_reason')), 'amendment must explain changed reasons')
            now = datetime.now(timezone.utc).isoformat()
            event = {'operation_id': operation_id, 'input_digest': input_digest, 'encounter_id': entry['encounter_id'], 'journal_entry_id': 'LJ-' + journal.digest(entry['encounter_id'])[:20], 'operation': n['operation'], 'saved_at': now, 'path': rel, 'question_key': question_key,
                     'idea_id': old['idea_id'] if old else 'LI-' + journal.digest([entry['encounter_id'], question_key])[:20], 'mode': payload.get('mode', 'normal')}
            journal.require(event['mode'] in {'normal', 'rehearsal'}, 'invalid closeout mode')
            sources = [p for p in entry['passages'] if p['source_id'] in n['source_ids']]
            # References only: no private passage bodies are copied to tracked prose.
            source_prose = '\n'.join(f"- {s['source_id']} — {s['edition']}; {s['language']}; {s['boundary']}" for s in sources)
            block = f"\n## Interpretation recorded {now}\n\n{n.get('change_reason', '')}\n\n### Question\n{n['question']}\n\n### Source passages\n{source_prose}\n\n### Interpretation\n{n['interpretation']}\n\n### Strongest limitation\n{n['limitation']}\n\n### Next discriminating test\n{n['next_test']}\n"
            body = MARKER.sub('', p.read_text(encoding='utf-8')) if old else f"# {n['title']}\n\nClass: interpretive-note.\nStatus: private-provisional; work in progress.\nAuthority: interpretation only; Library Integration required for governed use.\n"
            if old:
                split = body.find('\n## Interpretation recorded')
                journal.require(split >= 0, 'amendment target lacks preserved interpretation sections')
                body = body[:split] + block + '\n## Earlier reasoning\n' + body[split:]
            else:
                body += block
            meta = {'schema': 'library-artifact-v1', 'kind': 'note', 'idea_id': event['idea_id'], 'title': n['title'], 'question': n['question'],
                    'work_ids': sorted(set(n['work_ids']) | set((old or {}).get('work_ids', []))), 'sources': sorted(set(n['source_ids']) | set((old or {}).get('sources', []))),
                    'saves': (old or {}).get('saves', []) + [event], 'body_sha256': hashlib.sha256(body.encode()).hexdigest()}
            rendered = '<!-- mira-library-artifact\n' + json.dumps(meta, ensure_ascii=False, sort_keys=True) + '\n-->' + body
            plans.append((p, rendered, event))
        # Validate predecessor and encounter constraints before the first artifact write.
        journal.record(entry, repo=repo, root=root, check=True)
        if check:
            return {'status': 'ready', 'operations': len(plans), 'writes_performed': False}
        saved = []
        try:
            for p, rendered, event in plans:
                if rendered is not None:
                    journal.require((sha(p) if p.exists() else None) == baselines[p], 'target changed after closeout validation')
                    atomic_write(p, rendered)
                saved.append({**event, 'sha256': sha(p)})
            entry.update(artifact_saves=saved, reading_input_digest=input_digest, reading_mode=payload.get('mode', 'normal'), note_disposition=payload['note_disposition'])
            entry['artifacts'].extend({'ref': s['path'], 'sha256': s['sha256']} for s in saved)
            result = journal.record(entry, repo=repo, root=root)
            return {**result, 'saves': saved, 'remaining': []}
        except (OSError, ValueError) as error:
            return {'status': 'partial', 'saves': saved, 'remaining': 'retry identical closeout input', 'error': str(error), 'writes_performed': bool(saved)}


def growth(start, end, *, repo=journal.REPO_ROOT, root=None):
    import library_expectations
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    journal.require(first <= last and (last - first).days <= 3660, 'invalid report interval')
    entries = journal.entries(repo, root)
    heads = {e['entry_id']: e for e in entries}
    saves = {s['operation_id']: s for e in entries for s in e.get('artifact_saves', [])}
    pending = []
    for m in inventory(repo)['artifacts']:
        p = repo / m['path']
        intact = m.get('body_sha256') == hashlib.sha256(MARKER.sub('', p.read_text(encoding='utf-8')).encode()).hexdigest()
        for s in m.get('saves', []):
            if s['operation_id'] not in saves:
                pending.append({**s, 'integrity': 'intact' if intact else 'changed'})
                if intact:
                    saves[s['operation_id']] = s
    creates = {}
    for s in sorted(saves.values(), key=lambda s: s['saved_at']):
        if s['operation'] == 'create' and s['mode'] == 'normal':
            creates.setdefault(s['idea_id'], s)
    daily, monthly = [], {}
    day = first
    while day <= last:
        count = sum(journal_calendar.current_date(datetime.fromisoformat(s['saved_at'])) == day for s in creates.values())
        daily.append({'date': day.isoformat(), 'new_notes': count, 'target': 1 if day >= EFFECTIVE_DATE else None, 'attained': count >= 1 if day >= EFFECTIVE_DATE else None,
                      'status': 'recorded-save-count' if day >= EFFECTIVE_DATE else 'not-recorded; before rollout'})
        monthly[day.strftime('%Y-%m')] = monthly.get(day.strftime('%Y-%m'), 0) + count
        day += timedelta(days=1)
    applications = [e for e in heads.values() if e['kind'] == 'application' and e.get('application_mode') == 'subsequent-use' and first <= journal_calendar.current_date(datetime.fromisoformat(e['recorded_at'])) <= last]
    applied = [a for e in applications for a in e.get('note_applications', [])]
    readings = sorted([e for e in heads.values() if e['kind'] == 'reading' and e.get('reading_mode') != 'rehearsal'], key=lambda e: e['recorded_at'])
    return {'expectation_review': library_expectations.report(entries, first, last, repo, root), 'daily': daily, 'monthly': monthly, 'calendar_policy': journal_calendar.POLICY_ID,
            'application_entries': [{'entry_id': e['entry_id'], 'later_use_refs': e['later_use_refs'], 'changes': e['learning_changes']} for e in applications],
            'distinct_notes_applied': len({a['idea_id'] for a in applied}),
            'corrections': [a for a in applied if a['effect'] in {'qualified', 'rejected', 'changed', 'failed-transfer'}],
            'friction': [{'entry_id': e['entry_id'], 'observation': e['friction']} for e in heads.values() if 'friction' in e and first <= journal_calendar.current_date(datetime.fromisoformat(e['recorded_at'])) <= last],
            'missing_fields': 'not-recorded', 'legacy_entries_without_save_records': sum('artifact_saves' not in e for e in heads.values()),
            'exploration': {'recent_selections': [e.get('curiosity', {}).get('selection', 'not-recorded') for e in readings[-4:]], 'preference': 'approximately one in four; no debt'},
            'pending_closeout_saves': pending,
            'review_due': bool(creates) and (last - min(journal_calendar.current_date(datetime.fromisoformat(s['saved_at'])) for s in creates.values())).days >= 30,
            'authority': 'counts and interpretive application records; no recursive improvement score', 'writes_performed': False}
