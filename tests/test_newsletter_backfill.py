import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import newsletter_capture as nc
import newsletter_backfill as bf


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


@pytest.fixture
def case(tmp_path):
    repo = tmp_path / 'repo'
    (repo / 'geopolitics/voices').mkdir(parents=True)
    put(repo / 'archive/sources/geopolitics/source-manifest.json', {'sources': [], 'source_count': 0})
    store = nc.Store(repo, tmp_path / 'private')
    return store, tmp_path


def candidate(root, name='one', **overrides):
    payload = dict(url='https://thegrayzone.substack.com/p/' + name, title=name, html='<p>Full article α.</p>',
                   text='Full article α.', observed_at='2026-09-15T01:00:00Z', publication='blumenthal')
    put(root / (name + '.json'), payload)
    review = dict(voice_slugs=['blumenthal', 'wyatt-reed'], host_slug='grayzone',
                  publication_url='https://thegrayzone.substack.com/', publication_date='2026-09-14',
                  classification='complete-written-article', access_gate='none', evidence={
                      'authorship': {'basis': 'explicit-byline', 'reference': 'By Max Blumenthal and Wyatt Reed'},
                      'publication_date': 'SEP 14, 2026', 'completeness': 'Full text and ending reviewed',
                      'access_gate': 'No gate present', 'host': 'The Grayzone', 'homepage': 'Visible publication link'})
    review.update(overrides)
    return {'capture_file': str(root / (name + '.json')), 'review': review}


def fake_native(store, corrupt=None):
    calls = []
    def run(args, **kwargs):
        get = lambda flag: args[args.index(flag) + 1]
        voices = [args[i+1] for i, a in enumerate(args) if a == '--voice-slug']
        name = get('--title')
        relative = 'archive/sources/geopolitics/sources/' + get('--pub-date') + '/source-' + name + '.md'
        row = dict(local_path=relative, source_url=get('--url'), voice_slugs=voices, title=name, date=get('--pub-date'),
                   voice_roles={v: ['author'] for v in voices}, role_status={v: 'confirmed' for v in voices},
                   role_basis={v: 'authored_source_class' for v in voices}, host_slug=get('--host-slug'), publication_url=get('--publication-url'))
        if '--dry-run' in args:
            return SimpleNamespace(returncode=0, stderr='', stdout=json.dumps({'preflight': {'sources': [{'planned_path': relative}]}, 'messages': ['DRY RUN\n' + json.dumps(row)]}))
        calls.append(name)
        path = store.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('---\nvoice_roles: ' + json.dumps(row['voice_roles']) + '\n---\n# Title\n\n## Transcript\n\n' + Path(get('--body-file')).read_text(encoding='utf-8'), encoding='utf-8')
        if corrupt:
            corrupt(row)
        m = bf.manifest(store.repo)
        m['sources'].append(row)
        put(store.repo / 'archive/sources/geopolitics/source-manifest.json', m)
        return SimpleNamespace(returncode=0, stdout='{}', stderr='')
    run.calls = calls
    return run


def build(case, items):
    store, root = case
    batch, plan = root / 'batch.json', root / 'plan.json'
    put(batch, {'discovery': {'complete': True, 'boundary': 'January through September'}, 'candidates': items})
    run = fake_native(store)
    nc.browser_plan(store, batch, plan, run)
    return plan, run


def test_coauthors_and_resume_without_receipt(case):
    store, root = case
    plan, run = build(case, [candidate(root)])
    assert nc.browser_land_plan(store, plan, run)['counts'] == {'admitted': 1}
    plan.with_suffix('.receipt.json').unlink()
    assert nc.browser_land_plan(store, plan, run)['counts'] == {'existing': 1}
    assert run.calls == ['one']


def test_native_identity_hold_and_warning_preview(case):
    store, root = case
    batch, plan = root / 'batch.json', root / 'plan.json'
    put(batch, {'candidates': [candidate(root), candidate(root, 'two')]})
    native = fake_native(store)
    def run(args, **kwargs):
        if '--dry-run' in args and args[args.index('--title') + 1] == 'one':
            return SimpleNamespace(returncode=0, stderr='', stdout=json.dumps({
                'status': 'ALREADY LANDED', 'archive': 'existing-source.md', 'preflight': {}}))
        result = native(args, **kwargs)
        if '--dry-run' in args:
            data = json.loads(result.stdout)
            data['messages'].insert(0, 'Preflight: WARNING (1 source(s))')
            result.stdout = json.dumps(data)
        return result
    p = nc.browser_plan(store, batch, plan, run)
    assert [i['result']['status'] for i in p['items']] == ['held', 'ready']
    receipt = nc.browser_land_plan(store, plan, run)
    assert receipt['counts'] == {'held': 1, 'admitted': 1}
    assert native.calls == ['two']


def test_wrapper_identity_and_reviewed_edition_alias_prevent_duplicate(case):
    store, root = case
    item = candidate(root)
    plan, run = build(case, [item])
    nc.browser_land_plan(store, plan, run)
    m = bf.manifest(store.repo)
    row = m['sources'][0]
    url = row.pop('source_url')
    path = store.repo / row['local_path']
    path.write_text(path.read_text(encoding='utf-8').replace('---\n', '---\nsource_url: "'+url+'"\n', 1), encoding='utf-8')
    put(store.repo / 'archive/sources/geopolitics/source-manifest.json', m)
    primary = candidate(root, 'primary', related_urls=[url])
    personal = candidate(root, 'personal')
    for value, kind in [(primary, 'original-publisher'), (personal, 'personal-newsletter')]:
        value.update(work_id='same-work', edition_kind=kind, edition_evidence='Reviewed source wrapper and edition', difference_summary='Wording variant')
    batch = root / 'second.json'; second = root / 'second-plan.json'
    put(batch, {'candidates':[primary, personal]})
    result = nc.browser_plan(store, batch, second, run)
    assert result['items'][0]['result']['status'] == 'held'
    assert url in result['items'][0]['review']['related_urls']
    assert run.calls == ['one']


@pytest.mark.parametrize('change', [lambda r: r['voice_slugs'].pop(), lambda r: r['voice_slugs'].append('other'),
                                   lambda r: r['voice_roles'].update(blumenthal=['guest'])])
def test_wrong_authors_stop_after_admission(case, change):
    store, root = case
    plan, _ = build(case, [candidate(root), candidate(root, 'two')])
    run = fake_native(store, change)
    with pytest.raises(ValueError, match='verification'):
        nc.browser_land_plan(store, plan, run)
    assert run.calls == ['one']
    assert bf.read(plan.with_suffix('.receipt.json'))['status'] == 'stopped'


@pytest.mark.parametrize('reverse', [False, True])
def test_hold_independent_of_order(case, reverse):
    store, root = case
    first = candidate(root)
    # Establish a real source then change only its old metadata.
    plan, run = build(case, [first])
    nc.browser_land_plan(store, plan, run)
    m = bf.manifest(store.repo); m['sources'][0].pop('publication_url')
    put(store.repo / 'archive/sources/geopolitics/source-manifest.json', m)
    plan.unlink()
    items = [first, candidate(root, 'two')]
    plan, run = build(case, items[::-1] if reverse else items)
    plan.with_suffix('.receipt.json').unlink()
    result = nc.browser_land_plan(store, plan, run)
    assert result['counts'] == {'held': 1, 'admitted': 1}
    assert run.calls == ['two']


@pytest.mark.parametrize('target', ['capture', 'review', 'plan'])
def test_changed_inputs_stop(case, target):
    store, root = case
    item = candidate(root); plan, run = build(case, [item])
    path = Path(item['capture_file']) if target == 'capture' else root / ('batch.json' if target == 'review' else 'plan.json')
    data = bf.read(path); data['changed'] = True; put(path, data)
    with pytest.raises(ValueError, match='changed'):
        nc.browser_land_plan(store, plan, run)
    assert not run.calls


def test_malformed_manifest_and_escape(case):
    store, root = case
    put(store.repo / 'archive/sources/geopolitics/source-manifest.json', {'sources': [{'local_path': '../../outside'}]})
    with pytest.raises(ValueError, match='escaping'):
        build(case, [candidate(root)])


def test_legacy_alias_and_missing_review(case):
    store, root = case
    assert bf.authors({'voice_slug': 'blumenthal'}) == ['blumenthal']
    with pytest.raises(ValueError, match='Contradictory'):
        bf.authors({'voice_slug': 'blumenthal', 'voice_slugs': ['blumenthal', 'wyatt-reed']})
    item = candidate(root)
    payload = bf.read(item['capture_file']); payload.update(item['review']); payload.pop('voice_slugs'); payload['voice_slug'] = 'blumenthal'
    put(Path(item['capture_file']), payload)
    run = fake_native(store)
    assert nc.browser_capture(store, item['capture_file'], True, run)['status'] == 'admitted'
    assert nc.browser_capture(store, item['capture_file'], True, run)['status'] == 'existing'


@pytest.mark.parametrize('classification,gate,inspected,status', [
    ('complete-written-article', 'none', True, 'admitted'),
    ('description-only', 'none', True, 'excluded'),
    ('guest-authored', 'none', True, 'excluded'),
    ('narration-duplicate', 'none', True, 'excluded'),
    ('complete-written-article', 'paid', True, 'held'),
    ('complete-written-article', 'none', False, 'unresolved')])
def test_mixed_content(case, classification, gate, inspected, status):
    store, root = case
    item = candidate(root, classification=classification, access_gate=gate)
    raw = bf.read(item['capture_file']); raw['media_marked'] = True; put(Path(item['capture_file']), raw)
    if inspected:
        item['review']['evidence']['accompanying_text'] = 'Rendered accompanying text inspected'
    plan, run = build(case, [item])
    assert nc.browser_land_plan(store, plan, run)['results'][0]['status'] == status


@pytest.mark.parametrize('original_gate,different', [('none', False), ('none', True), ('paid', True)])
def test_editions(case, original_gate, different):
    store, root = case
    original = candidate(root, 'original', access_gate=original_gate)
    personal = candidate(root, 'personal')
    for item, kind in [(original, 'original-publisher'), (personal, 'personal-newsletter')]:
        item.update(work_id='work-one', edition_kind=kind, edition_evidence='Publisher byline and syndication link',
                    difference_summary='Reviewed wording changes' if different else 'Exact same article text')
    if different:
        raw = bf.read(personal['capture_file']); raw['text'] += ' Different wording.'; put(Path(personal['capture_file']), raw)
    plan, run = build(case, [personal, original])
    result = nc.browser_land_plan(store, plan, run)
    assert result['counts']['admitted'] == 1
    assert run.calls == ['original' if original_gate == 'none' else 'personal']


def test_zero_exit_is_not_success(case):
    store, root = case
    plan, _ = build(case, [candidate(root)])
    with pytest.raises(ValueError, match='manifest mutation|verification'):
        nc.browser_land_plan(store, plan, lambda *a, **k: SimpleNamespace(returncode=0, stdout='{}', stderr=''))


def test_public_cli_real_native_coauthors(case):
    store, root = case
    # Copy code into an isolated repository: no subprocess can target the real archive.
    scripts = Path(nc.__file__).parent
    (store.repo / 'scripts').mkdir()
    for path in scripts.glob('*.py'):
        shutil.copyfile(path, store.repo / 'scripts' / path.name)
    index = store.repo / 'geopolitics/voices/blumenthal/source-index.md'
    index.parent.mkdir(parents=True)
    index.write_text('# Index\n\nCorpus: 0 local route rows across 0 central archive source files.\n\n| Date | Source | Role | Host slug | Archive link |\n| --- | --- | --- | --- | --- |\n', encoding='utf-8')
    batch, plan = root / 'cli-input.json', root / 'cli-plan.json'
    put(batch, {'discovery': {'complete': True}, 'candidates': [candidate(root)]})
    base = [sys.executable, str(store.repo / 'scripts/newsletter_capture.py')]
    def call(args):
        proc = subprocess.run(base + args + ['--state-root', str(root / 'private'), '--json'], capture_output=True, text=True, encoding='utf-8')
        assert proc.returncode == 0, proc.stderr
        return json.loads(proc.stdout)
    call(['browser-plan', '--batch-file', str(batch), '--plan-file', str(plan)])
    assert call(['browser-land-plan', '--plan-file', str(plan)])['counts'] == {'admitted': 1}
    plan.with_suffix('.receipt.json').unlink()
    assert call(['browser-land-plan', '--plan-file', str(plan)])['counts'] == {'existing': 1}
    row = bf.manifest(store.repo)['sources'][0]
    assert row['date'] == '2026-09-14'  # observation was on the next UTC calendar day
    assert row['voice_roles'] == {'blumenthal': ['author'], 'wyatt-reed': ['author']}
    assert row['local_path'] in index.read_text(encoding='utf-8')


def test_existing_different_edition_is_held(case):
    store, root = case
    personal = candidate(root, 'personal')
    plan, run = build(case, [personal]); nc.browser_land_plan(store, plan, run)
    plan.unlink(); plan.with_suffix('.receipt.json').unlink()
    original = candidate(root, 'original')
    for item, kind in [(personal, 'personal-newsletter'), (original, 'original-publisher')]:
        item.update(work_id='shared', edition_kind=kind, edition_evidence='Syndication links', difference_summary='Reviewed changes')
    plan, run = build(case, [original, personal])
    result = nc.browser_land_plan(store, plan, run)
    assert result['counts'] == {'held': 1, 'excluded': 1}
    assert run.calls == []


def test_index_role_drift_preserved(case):
    store, root = case
    index = store.repo / 'geopolitics/voices/blumenthal/source-index.md'
    index.parent.mkdir(parents=True)
    old_line = '| `2025-01-01` | Old | `host-pressure test` | `channel` | [source](../../../archive/sources/geopolitics/sources/2025-01-01/source-old.md) |\n'
    index.write_text(old_line, encoding='utf-8')
    plan, native = build(case, [candidate(root)])
    def run(args, **kwargs):
        output = native(args, **kwargs)
        text = index.read_text(encoding='utf-8').replace('host-pressure test', 'guest')
        text += '| `2026-09-14` | one | `author` | `grayzone` | [source](../../../archive/sources/geopolitics/sources/2026-09-14/source-one.md) |\n'
        index.write_text(text, encoding='utf-8')
        return output
    result = nc.browser_land_plan(store, plan, run)
    assert old_line in index.read_text(encoding='utf-8')
    assert len(result['results'][0]['restored_role_labels']) == 1


def test_unrelated_manifest_change_stops(case):
    store, root = case
    plan, run = build(case, [candidate(root), candidate(root, 'two')])
    def corrupt(args, **kwargs):
        output = run(args, **kwargs)
        m = bf.manifest(store.repo)
        m['sources'].append({'local_path': 'archive/sources/geopolitics/sources/unexpected.md'})
        put(store.repo / 'archive/sources/geopolitics/source-manifest.json', m)
        return output
    with pytest.raises(ValueError, match='Unexpected manifest mutation'):
        nc.browser_land_plan(store, plan, corrupt)
    assert run.calls == ['one']


def test_interrupted_native_save_resumes(case):
    store, root = case
    plan, native = build(case, [candidate(root), candidate(root, 'two')])
    def interrupted(args, **kwargs):
        native(args, **kwargs)
        raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        nc.browser_land_plan(store, plan, interrupted)
    resumed = nc.browser_land_plan(store, plan, native)
    assert resumed['counts'] == {'existing': 1, 'admitted': 1}
    assert native.calls == ['one', 'two']


def test_colliding_destinations_held_before_mutation(case):
    store, root = case
    one, two = candidate(root), candidate(root, 'two')
    raw = bf.read(two['capture_file']); raw['title'] = 'one'; put(Path(two['capture_file']), raw)
    plan, run = build(case, [one, two])
    assert nc.browser_land_plan(store, plan, run)['counts'] == {'held': 2}
    assert not run.calls


def test_missing_review_never_invented(case):
    store, root = case
    item = candidate(root); item['review']['evidence'].pop('authorship')
    plan, run = build(case, [item])
    assert nc.browser_land_plan(store, plan, run)['counts'] == {'unresolved': 1}
    assert not run.calls


def test_bridge_receipt_tampering_stops(case):
    store, root = case
    item = candidate(root)
    raw = Path(item['capture_file']).read_bytes(); payload = json.loads(raw)
    folder = root / 'bridge'; folder.mkdir()
    for name, content in {'payload.json': raw, 'body.txt': payload['text'].encode(), 'body.html': payload['html'].encode()}.items():
        (folder / name).write_bytes(content)
    put(folder / 'receipt.json', {'files': {name: {'bytes': len((folder/name).read_bytes()), 'sha256': nc.digest((folder/name).read_bytes())}
                                          for name in ['payload.json', 'body.txt', 'body.html']}})
    item['capture_file'] = str(folder / 'payload.json')
    plan, run = build(case, [item])
    (folder / 'body.txt').write_text('tampered')
    with pytest.raises(ValueError, match='integrity'):
        nc.browser_land_plan(store, plan, run)
    assert bf.read(plan.with_suffix('.failure.json'))['status'] == 'stopped'
    assert not run.calls


def test_review_can_correct_raw_author_metadata(case):
    store, root = case
    item = candidate(root)
    raw = bf.read(item['capture_file']); raw['voice_slug'] = 'blumenthal'; put(Path(item['capture_file']), raw)
    before = Path(item['capture_file']).read_bytes()
    plan, run = build(case, [item])
    assert nc.browser_land_plan(store, plan, run)['counts'] == {'admitted': 1}
    assert Path(item['capture_file']).read_bytes() == before


def test_complete_classification_requires_gate_disposition(case):
    store, root = case
    item = candidate(root); item['review'].pop('access_gate')
    plan, run = build(case, [item])
    assert nc.browser_land_plan(store, plan, run)['counts'] == {'unresolved': 1}


def test_native_transaction_failure_stops_remaining_sources(case):
    store, root = case
    plan, _ = build(case, [candidate(root), candidate(root, 'two')])
    calls = []
    def fail(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=1, stdout='', stderr='transaction rolled back')
    with pytest.raises(ValueError, match='Native intake failed'):
        nc.browser_land_plan(store, plan, fail)
    assert len(calls) == 1
    assert bf.read(plan.with_suffix('.receipt.json'))['events'][-1]['returncode'] == 1
