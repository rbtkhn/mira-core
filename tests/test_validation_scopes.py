from types import SimpleNamespace
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import pytest
import validation_scopes as scope


def test_structural_partition_is_complete_disjoint_and_keeps_default():
    checks = tuple((name, lambda: []) for name in sorted(scope.PUBLIC_CHECKS | scope.CORPUS_CHECKS))
    public = scope.checks_for_scope(checks, 'public-package')
    corpus = scope.checks_for_scope(checks, 'corpus')
    assert set(public).isdisjoint(corpus)
    assert set(public) | set(corpus) == set(checks)
    assert scope.checks_for_scope(checks, 'all') is checks
    assert {name for name, _ in corpus} == scope.CORPUS_CHECKS
    assert scope.PUBLIC_CHECKS.isdisjoint(scope.CORPUS_CHECKS)


def test_new_structural_check_requires_explicit_classification():
    checks = tuple((name, lambda: []) for name in scope.PUBLIC_CHECKS | {'new_unknown_control'})
    for selected in ('public-package', 'corpus'):
        with pytest.raises(ValueError, match='unclassified structural checks'):
            scope.checks_for_scope(checks, selected)


def test_missing_public_check_fails_closed():
    with pytest.raises(ValueError, match='public checks missing'):
        scope.checks_for_scope((), 'public-package')


def test_corpus_module_exclusion_is_explicit_and_public_only(tmp_path):
    public = SimpleNamespace(getoption=lambda key: True, rootpath=tmp_path)
    all_checks = SimpleNamespace(getoption=lambda key: False, rootpath=tmp_path)
    path = tmp_path / 'tests/test_library_note_relocation.py'
    assert scope.pytest_ignore_collect(path, public) is True
    assert scope.pytest_ignore_collect(path, all_checks) is None
    assert scope.pytest_ignore_collect(tmp_path / 'test_unknown.py', public) is None
    assert scope.pytest_ignore_collect(tmp_path / 'tests/neighbor/test_library_note_relocation.py', public) is None


def test_live_records_are_deferred_without_hiding_other_failures():
    excluded = []
    config = SimpleNamespace(getoption=lambda key: key == '--public-package',
        hook=SimpleNamespace(pytest_deselected=lambda items: excluded.extend(items)),
        pluginmanager=SimpleNamespace(get_plugin=lambda name: None))
    live = SimpleNamespace(originalname='live', name='live', nodeid=next(iter(scope.CORPUS_CASES)))
    unit = SimpleNamespace(originalname='test_unknown_failure', name='unit', nodeid='test_x.py::unit')
    items = [live, unit]
    scope.pytest_collection_modifyitems(config, items)
    assert items == [unit]
    assert excluded == [live]


def test_corpus_selection_is_complementary_and_unknown_tests_stay_public():
    live = SimpleNamespace(nodeid=next(iter(scope.CORPUS_CASES)) + '[synthetic]')
    new = SimpleNamespace(nodeid='tests/test_new.py::test_failure')
    selected = {}
    for flag in ('--public-package', '--corpus-only'):
        config = SimpleNamespace(getoption=lambda key: key == flag,
            hook=SimpleNamespace(pytest_deselected=lambda items: None),
            pluginmanager=SimpleNamespace(get_plugin=lambda name: None))
        items = [live, new]
        scope.pytest_collection_modifyitems(config, items)
        selected[flag] = items
    assert selected == {'--public-package': [new], '--corpus-only': [live]}


def test_conflicting_pytest_scopes_fail_closed():
    config = SimpleNamespace(getoption=lambda key: True)
    with pytest.raises(pytest.UsageError, match='mutually exclusive'):
        scope.pytest_collection_modifyitems(config, [])


def test_public_scope_keeps_privacy_enforcement():
    assert 'archive.validate_repository_state' in scope.PUBLIC_CHECKS
    import validate_repository as validation
    for selected in ('public-package', 'corpus'):
        assert scope.checks_for_scope(validation.REPOSITORY_CHECKS, selected)


@pytest.mark.parametrize('selected_scope,flag', [('public-package', '--public-package'), ('corpus', '--corpus-only')])
def test_scoped_validation_preserves_failure_and_cannot_cache_full(monkeypatch, tmp_path, selected_scope, flag):
    import sys
    from tools import validate_repo as runner
    calls = []
    monkeypatch.setattr(runner, 'resolve_validation_python', lambda root: Path(sys.executable))
    monkeypatch.setattr(runner, 'full_result_fingerprint', lambda *a: pytest.fail('scope used Full cache'))
    def phase(command, **kwargs):
        calls.append((command, kwargs['mode']))
        return 7 if kwargs['phase'] == 'structural' else 0
    monkeypatch.setattr(runner, 'run_phase', phase)
    assert runner.main(['--scope', selected_scope, '--temp-root', str(tmp_path)]) == 7
    assert len(calls) == 2
    assert all(mode == selected_scope for _, mode in calls)
    assert flag in calls[-1][0]


def test_scopes_reject_full_cache_and_focused_combinations():
    from tools import validate_repo as runner
    assert runner.main(['--scope', 'public-package', '--cache-only']) == 2
    assert runner.main(['--scope', 'corpus', '--path', 'tests/test_example.py']) == 2


def test_scope_control_publication_routes_are_exact(tmp_path):
    import publication_validation as routing
    for rel in ('docs/validation-scopes.md', '.github/workflows/validate.yml'):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('Synthetic control')
        assert routing.build_report([rel], repo_root=tmp_path)['status'] == 'manual-required'
    neighbor = tmp_path / '.github/workflows/unreviewed.yml'
    neighbor.write_text('Synthetic neighbor')
    assert routing.build_report([neighbor.relative_to(tmp_path).as_posix()], repo_root=tmp_path)['status'] == 'blocked'
