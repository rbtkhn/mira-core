"""Reviewed, hash-bound browser plans. Capture transport never grants admission."""
from collections import Counter
from datetime import date, datetime
import json
import os
import re
from pathlib import Path
import subprocess
import sys

import newsletter_capture as nc

EVIDENCE = ('authorship', 'publication_date', 'completeness', 'access_gate', 'host', 'homepage')
EXCLUDED = {'description-only', 'announcement', 'narration-duplicate', 'guest-authored', 'media-only/announcement'}


def fingerprint(value):
    return nc.digest(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8'))


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def authors(value):
    singular, plural = value.get('voice_slug'), value.get('voice_slugs')
    if plural is not None and (not isinstance(plural, list) or not all(isinstance(v, str) and v for v in plural)):
        raise ValueError('voice_slugs must be a list of person slugs')
    if singular and plural is not None and plural != [singular]:
        raise ValueError('Contradictory singular/plural author inputs')
    values = plural if plural is not None else ([singular] if singular else [])
    from voice_metadata import canonical_slug
    return sorted(set(canonical_slug(v) for v in values))


def load_capture(item):
    path = Path(item['capture_file'])
    raw = path.read_bytes()
    if nc.digest(raw) != item['capture_sha256']:
        raise ValueError('Reviewed capture changed')
    payload = read(path)
    receipt_path = path.parent / 'receipt.json'
    if receipt_path.exists():
        receipt = read(receipt_path)
        for name in ('payload.json', 'body.html', 'body.txt'):
            info = receipt['files'][name]
            content = (path.parent / name).read_bytes()
            if len(content) != info['bytes'] or nc.digest(content) != info['sha256']:
                raise ValueError('Capture transport integrity failure')
        if payload['html'] != (path.parent / 'body.html').read_bytes().decode('utf-8') or payload['text'] != (path.parent / 'body.txt').read_bytes().decode('utf-8'):
            raise ValueError('Capture transport content mismatch')
    return payload


def normalized(item):
    raw = load_capture(item)
    review = item['review']
    if set(review) - {'voice_slug', 'voice_slugs', 'homepage', 'publication_url', 'publication_date', 'host_slug',
                      'classification', 'access_gate', 'evidence', 'related_urls', 'edition_reason', 'difference_summary',
                      'edition_comparison', 'edition_evidence'}:
        raise ValueError('Review contains unsupported capture overrides')
    value = {**raw, **review}
    value['voice_slugs'] = authors(review if 'voice_slugs' in review or 'voice_slug' in review else raw)
    value['homepage'] = review.get('homepage') or review.get('publication_url') or raw.get('homepage') or raw.get('publication_url', '')
    # Never derive the publication day from the UTC observation timestamp.
    value['publication_date'] = review.get('publication_date') or raw.get('publication_date', '')
    return value


def review_problem(value):
    classification = value.get('classification')
    evidence = value.get('evidence', {})
    if not isinstance(evidence, dict):
        return 'unresolved', 'Review evidence must be an object'
    if value.get('media_marked') and not evidence.get('accompanying_text'):
        return 'unresolved', 'Accompanying text not inspected'
    if classification in EXCLUDED:
        return ('excluded', classification) if evidence.get('completeness') else ('unresolved', 'Missing exclusion evidence')
    if value.get('access_gate') not in (None, 'none'):
        return 'held', 'Access gated; no complete-body admission'
    if value.get('access_gate') is None:
        return 'unresolved', 'Missing explicit access-gate disposition'
    if classification != 'complete-written-article' or any(not evidence.get(k) for k in EVIDENCE):
        return 'unresolved', 'Missing reviewed article evidence'
    if any(not isinstance(evidence[k], str) or not evidence[k].strip() for k in EVIDENCE if k != 'authorship'):
        return 'unresolved', 'Review evidence must describe observed support'
    attribution = evidence['authorship']
    if not isinstance(attribution, dict) or attribution.get('basis') not in {'explicit-byline', 'publisher-author-index'} or not attribution.get('reference'):
        return 'unresolved', 'Missing explicit authorship basis/reference'
    if not value['voice_slugs'] or not value.get('host_slug'):
        return 'unresolved', 'Unresolved author or host'
    if value.get('publication') not in nc.SEEDS or value['publication'] == 'innermost-loop':
        return 'held', 'Not an approved Geopolitics publication'
    if not nc.canonical(value.get('url', '')) or not nc.canonical(value['homepage']):
        return 'unresolved', 'Missing HTTPS provenance'
    try:
        date.fromisoformat(value['publication_date'])
        observed = datetime.fromisoformat(value['observed_at'].replace('Z', '+00:00'))
        if observed.tzinfo is None:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        return 'unresolved', 'Missing displayed publication date or timezone-aware observation'
    if not value.get('text') or not value.get('html'):
        return 'unresolved', 'Empty written capture'
    return None


def manifest(repo):
    data = read(repo / 'archive/sources/geopolitics/source-manifest.json')
    if not isinstance(data.get('sources'), list):
        raise ValueError('Malformed source manifest')
    paths = set()
    for row in data['sources']:
        if not isinstance(row, dict):
            raise ValueError('Malformed manifest row')
        path = row.get('local_path', '')
        target = (repo / path).resolve()
        if not path or Path(path).is_absolute() or path in paths or not target.is_relative_to((repo / 'archive/sources/geopolitics/sources').resolve()):
            raise ValueError('Ambiguous or escaping manifest path')
        paths.add(path)
    return data


def match(repo, value):
    rows = manifest(repo)['sources']
    url = nc.canonical(value['url'])
    related = {nc.canonical(u) for u in value.get('related_urls', [])}
    matches = [r for r in rows if any(nc.canonical(r.get(k, '')) in ({url} | related) - {''} for k in ('source_url', 'source_identity'))]
    # Older imported rows may omit URL metadata retained in their source wrapper.
    # Inspect only manifest-owned files, and only their metadata header.
    for row in rows:
        if row in matches or (row.get('source_url') and row.get('source_identity')):
            continue
        target = repo / row['local_path']
        if not target.is_file():
            continue
        header = target.read_text(encoding='utf-8-sig').split('\n---', 1)[0]
        wrapper_urls = re.findall(r'^source_(?:url|identity):\s*[\"\']?(https://[^\s\"\']+)', header, re.MULTILINE)
        if any(nc.canonical(u) in ({url} | related) - {''} for u in wrapper_urls):
            matches.append(row)
    if len(matches) > 1:
        return {'status': 'held', 'reason': 'Multiple archived editions or identities'}
    if not matches:
        return None
    row = matches[0]
    target = repo / row['local_path']
    if not target.is_file():
        return {'status': 'held', 'reason': 'Existing archive body missing'}
    content = target.read_text(encoding='utf-8-sig')
    if '\n## Transcript\n\n' not in content:
        return {'status': 'held', 'reason': 'Existing body boundary missing'}
    expected_roles = {v: ['author'] for v in value['voice_slugs']}
    wrapper_roles = re.search(r'^voice_roles: (.+)$', content.split('\n## Transcript\n\n', 1)[0], re.MULTILINE)
    try:
        source_roles = json.loads(wrapper_roles[1]) if wrapper_roles else None
    except ValueError:
        source_roles = None
    correct = (nc.canonical(row.get('source_url', '')) == url
               and row.get('date') == value['publication_date']
               and row.get('title') == value['title']
               and content.split('\n## Transcript\n\n', 1)[1].rstrip() == value['text'].rstrip()
               and sorted(row.get('voice_slugs', [])) == value['voice_slugs']
               and row.get('voice_roles') == expected_roles
               and source_roles == expected_roles
               and all(row.get('role_status', {}).get(v) == 'confirmed' and row.get('role_basis', {}).get(v) for v in value['voice_slugs'])
               and row.get('host_slug') == value['host_slug']
               and nc.canonical(row.get('publication_url', '')) == nc.canonical(value['homepage']))
    from voice_indexes import default_voices_root
    unindexed = []
    for voice in value['voice_slugs']:
        index = default_voices_root(repo) / voice / 'source-index.md'
        if not index.exists():
            unindexed.append(voice)
        elif '](' + '../../../' + row['local_path'] + ')' not in index.read_text(encoding='utf-8'):
            correct = False
    return {'status': 'existing' if correct else 'held', 'archive_path': row['local_path'],
            'unindexed_voices': unindexed, 'body_comparison': 'UTF-8 text after terminal whitespace normalization',
            'archive_sha256': nc.digest(target.read_bytes()),
            'reason': 'Verified body and metadata' if correct else 'Existing body, attribution, edition, or metadata mismatch'}


def command(repo, item, value):
    # Materialize only a temporary intake body alongside the explicit plan inputs.
    body = Path(item['capture_file']).parent / (item['capture_sha256'] + '.intake.txt')
    text = value['text'].encode('utf-8')
    if body.exists() and body.read_bytes() != text:
        raise ValueError('Temporary body integrity failure')
    if not body.exists():
        nc.write(body, text)
    provenance = {'capture_sha256': item['capture_sha256'], 'observed_at': value['observed_at'],
                  'evidence': value['evidence'], 'primary_url': value['url'],
                  'related_urls': value.get('related_urls', []), 'edition_reason': value.get('edition_reason'),
                  'difference_summary': value.get('difference_summary'), 'edition_comparison': value.get('edition_comparison'),
                  'edition_evidence': value.get('edition_evidence')}
    args = [sys.executable, str(repo / 'scripts/land_best_intake.py'), '--pub-date', value['publication_date'],
            '--ingest-date', nc.now().date().isoformat(), '--title', value['title'], '--url', value['url'],
            '--body-file', str(body), '--host-slug', value['host_slug'], '--publication-url', value['homepage'],
            '--source-form', 'newsletter', '--modality', 'newsletter', '--kind', 'source-text',
            '--source-class', 'authored newsletter', '--trim-opening', 'none', '--asr-repair', 'none', '--sectioning', 'none',
            '--upstream-path', 'browser-capture://' + item['capture_sha256'], '--source-note', json.dumps(provenance, ensure_ascii=False),
            '--editorial-note', 'Reviewed rendered written article; claims not independently verified.']
    for voice in value['voice_slugs']:
        args += ['--voice-slug', voice]
    return args


def invoke(run, args, repo):
    return run(args, cwd=repo, capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})


def plan(store, batch_file, plan_file, run=subprocess.run):
    source = Path(batch_file).resolve()
    if Path(plan_file).resolve().is_relative_to(store.repo.resolve()):
        raise ValueError('Plan artifacts must use an external temporary root')
    document = read(source)
    if document.get('discovery', {}).get('candidate_count', len(document['candidates'])) != len(document['candidates']):
        raise ValueError('Discovery candidate count does not reconcile')
    manifest(store.repo)
    items = []
    seen = set()
    for candidate in document['candidates']:
        path = Path(candidate['capture_file'])
        if not path.is_absolute():
            path = source.parent / path
        if path.resolve().is_relative_to(store.repo.resolve()):
            raise ValueError('Capture artifacts must use an external temporary root')
        item = {**candidate, 'capture_file': str(path.resolve()), 'capture_sha256': nc.digest(path.read_bytes())}
        if item['capture_sha256'] in seen:
            raise ValueError('Duplicate candidate capture')
        seen.add(item['capture_sha256'])
        item.setdefault('review', {})
        value = normalized(item)
        problem = review_problem(value)
        item['result'] = dict(zip(('status', 'reason'), problem)) if problem else {'status': 'ready'}
        items.append(item)
    # Reviewed work identifiers, not title guesses, establish edition groups.
    groups = {}
    for item in items:
        if item.get('work_id'):
            groups.setdefault(item['work_id'], []).append(item)
    for group in groups.values():
        if len(group) < 2:
            continue
        eligible = [i for i in group if i['result']['status'] == 'ready']
        primary = [i for i in eligible if i.get('edition_kind') == 'original-publisher']
        if not primary:
            primary = [i for i in eligible if i.get('edition_kind') == 'personal-newsletter']
        summaries = [i for i in group if i.get('difference_summary') and i.get('edition_evidence')]
        if len(primary) != 1 or not summaries:
            for i in eligible:
                i['result'] = {'status': 'held', 'reason': 'Edition selection or comparison unresolved'}
            continue
        chosen = primary[0]
        comparisons = []
        chosen_text = normalized(chosen)['text']
        for other in group:
            if other is chosen:
                continue
            other_value = normalized(other)
            comparisons.append({'capture_sha256': other['capture_sha256'],
                                'kind': 'incomplete-counterpart' if other['result']['status'] != 'ready' else
                                ('exact-text' if chosen_text == other_value['text'] else 'wording-variant')})
        chosen['review'].update(related_urls=sorted(set(chosen['review'].get('related_urls', []) +
                                    [normalized(i)['url'] for i in group if i is not chosen] +
                                    [u for i in group for u in i['review'].get('related_urls', [])])),
                                edition_reason=chosen['edition_kind'], difference_summary=summaries[0]['difference_summary'],
                                edition_evidence=summaries[0]['edition_evidence'], edition_comparison=comparisons)
        for i in eligible:
            if i is not chosen:
                i['result'] = {'status': 'excluded', 'reason': 'Related edition', 'primary_capture': chosen['capture_sha256']}
    for item in items:
        if item['result']['status'] != 'ready':
            continue
        value = normalized(item)
        existing = match(store.repo, value)
        if existing:
            item['result'] = existing
            continue
        preview = invoke(run, command(store.repo, item, value) + ['--dry-run', '--json'], store.repo)
        if preview.returncode:
            raise ValueError('Native intake preview failed: ' + preview.stderr[-500:])
        output = json.loads(preview.stdout)
        if output.get('status') == 'ALREADY LANDED':
            item['result'] = {'status': 'held', 'reason': 'Native intake found an existing identity outside the reviewed URL match',
                              'archive_path': output.get('archive'), 'native_preflight': output.get('preflight')}
            continue
        rows = [message for message in output.get('messages', []) if message.startswith('DRY RUN')]
        if len(rows) != 1:
            raise ValueError('Native intake preview did not return exactly one source row')
        row = json.loads(rows[0].split('\n', 1)[1])
        if (sorted(row['voice_slugs']) != value['voice_slugs'] or row.get('voice_roles') != {v: ['author'] for v in value['voice_slugs']}
                or row.get('date') != value['publication_date'] or row.get('title') != value['title']
                or row['host_slug'] != value['host_slug'] or nc.canonical(row['publication_url']) != nc.canonical(value['homepage'])):
            raise ValueError('Native preview does not preserve reviewed metadata')
        target = output['preflight']['sources'][0]['planned_path']
        resolved = (store.repo / target).resolve()
        if not resolved.is_relative_to((store.repo / 'archive/sources/geopolitics/sources').resolve()):
            raise ValueError('Escaping intake destination')
        if resolved.exists():
            item['result'] = {'status': 'held', 'reason': 'Destination already exists'}
        item['planned_path'] = target
        item['preview'] = output
    destinations = Counter(i.get('planned_path') for i in items if i['result']['status'] == 'ready')
    for item in items:
        if item['result']['status'] == 'ready' and destinations[item.get('planned_path')] > 1:
            item['result'] = {'status': 'held', 'reason': 'Multiple candidates share an intake destination'}
    plan_value = {'schema_version': 1, 'repo': str(store.repo.resolve()), 'input_file': str(source),
                  'input_sha256': nc.digest(source.read_bytes()), 'discovery': document.get('discovery', {'complete': False, 'reason': 'Discovery boundary unspecified'}), 'items': items}
    plan_value['digest'] = fingerprint(plan_value)
    if Path(plan_file).exists() and read(plan_file) != plan_value:
        raise ValueError('Plan file already exists with different reviewed state; choose a new plan file')
    nc.write(Path(plan_file), plan_value)
    return plan_value


def execute(store, plan_file, run=subprocess.run):
    plan_file = Path(plan_file)
    p = read(plan_file)
    digest = p.pop('digest')
    if fingerprint(p) != digest or p['repo'] != str(store.repo.resolve()):
        raise ValueError('Plan changed or belongs to another repository')
    if nc.digest(Path(p['input_file']).read_bytes()) != p['input_sha256']:
        raise ValueError('Reviewed plan input changed')
    for item in p['items']:
        load_capture(item)
    manifest(store.repo)
    results = []
    receipt_path = plan_file.with_suffix('.receipt.json')
    previous = read(receipt_path) if receipt_path.exists() else {}
    if previous and previous.get('plan_digest') != digest:
        raise ValueError('Receipt belongs to a different plan')
    attempted = set(previous.get('attempted', []))
    events = list(previous.get('events', []))
    def checkpoint(status, error=None):
        counts = dict(Counter(r['status'] for r in results))
        receipt = {'status': status, 'plan_digest': digest, 'discovery': p['discovery'], 'discovered': len(p['items']),
                   'processed': len(results), 'counts': counts, 'results': results, 'attempted': sorted(attempted), 'events': events}
        if error:
            receipt['error'] = str(error)
        nc.write(receipt_path, receipt)
        return receipt
    try:
        for item in p['items']:
            result = {**item['result'], 'capture_id': item['capture_sha256'],
                      'capture': {'status': 'integrity-verified', 'sha256': item['capture_sha256'],
                                  'observed_at': load_capture(item).get('observed_at')},
                      'review': {'sha256': fingerprint(item['review']), 'decision': item['result']}}
            if result['status'] not in {'ready', 'existing'}:
                results.append(result)
                continue
            value = normalized(item)
            current = match(store.repo, value)
            if current:
                if current['status'] == 'held' and item['capture_sha256'] in attempted:
                    raise ValueError('Previously attempted admission failed verification')
                results.append({**result, **current, 'verification': current})
                events.append({'capture_id': item['capture_sha256'], 'phase': 'verification', 'status': current['status']})
                checkpoint('running')
                continue
            if result['status'] == 'existing':
                raise ValueError('Previously existing source disappeared')
            if (store.repo / item['planned_path']).exists():
                results.append({**result, 'status': 'held', 'reason': 'Destination changed since planning'})
                continue
            before = manifest(store.repo)
            from voice_indexes import default_voices_root, STANDARD_ROW_RE
            indexes = list(default_voices_root(store.repo).glob('*/source-index.md'))
            prior_roles = {}
            for path in indexes:
                if not path.resolve().is_relative_to(store.repo.resolve()):
                    raise ValueError('Escaping voice index path')
                prior_roles[path] = {m['link']: m['role'] for line in path.read_text(encoding='utf-8').splitlines()
                                     if (m := STANDARD_ROW_RE.match(line))}
            attempted.add(item['capture_sha256'])
            events.append({'capture_id': item['capture_sha256'], 'phase': 'admission', 'status': 'started'})
            checkpoint('running')
            landed = invoke(run, command(store.repo, item, value) + ['--json'], store.repo)
            diagnostic = plan_file.parent / (item['capture_sha256'] + '.native-result.json')
            nc.write(diagnostic, {'returncode': landed.returncode, 'stdout': landed.stdout, 'stderr': landed.stderr})
            events.append({'capture_id': item['capture_sha256'], 'phase': 'admission', 'status': 'returned',
                           'returncode': landed.returncode, 'diagnostic_file': str(diagnostic)})
            checkpoint('running')
            if landed.returncode:
                try:
                    reason = json.loads(landed.stderr).get('error', landed.stderr[-500:])
                except (ValueError, AttributeError):
                    reason = landed.stderr[-500:]
                raise ValueError('Native intake failed; inspect state before retry: ' + reason)
            # Intake explicitly permits restoring only unintended generated role drift.
            restored = []
            for path, roles in prior_roles.items():
                original = path.read_text(encoding='utf-8')
                lines = original.splitlines(keepends=True)
                for number, line in enumerate(lines):
                    m = STANDARD_ROW_RE.match(line.rstrip('\r\n'))
                    if m and m['link'] in roles and m['role'] != roles[m['link']]:
                        lines[number] = line[:m.start('role')] + roles[m['link']] + line[m.end('role'):]
                        restored.append({'path': str(path.relative_to(store.repo)), 'link': m['link']})
                updated = ''.join(lines)
                if updated != original:
                    nc.write(path, updated.encode('utf-8'))
            verified = match(store.repo, value)
            after = manifest(store.repo)
            old = {r['local_path']: r for r in before['sources']}
            actual = {r['local_path']: r for r in after['sources']}
            if any(actual.get(k) != v for k, v in old.items()) or len(actual) != len(old) + 1:
                raise ValueError('Unexpected manifest mutation')
            if not verified or verified['status'] != 'existing' or verified['archive_path'] != item['planned_path']:
                raise ValueError('New admission failed body/metadata verification')
            for voice in value['voice_slugs']:
                index = default_voices_root(store.repo) / voice / 'source-index.md'
                if index.exists() and '](' + '../../../' + item['planned_path'] + ')' not in index.read_text(encoding='utf-8'):
                    raise ValueError('New admission missing voice-index route')
            results.append({**result, **verified, 'status': 'admitted', 'verification': verified, 'restored_role_labels': restored})
            events.append({'capture_id': item['capture_sha256'], 'phase': 'verification', 'status': 'passed'})
            checkpoint('running')
        return checkpoint('complete-with-gaps' if any(r['status'] in {'held', 'unresolved'} for r in results) or not p['discovery'].get('complete') else 'complete')
    except (ValueError, OSError, KeyError, TypeError) as error:
        checkpoint('stopped', error)
        raise
