from pathlib import Path
import json
import os
import subprocess
import sys

import pytest
import candidate_validation as candidate


@pytest.fixture(autouse=True)
def writable_fixture_objects(tmp_path):
    yield
    # Git objects are read-only on Windows; permit cleanup of this test's own
    # synthetic repository without changing production repository permissions.
    for path in tmp_path.rglob('*'):
        if path.is_file() and '.git' in path.parts:
            path.chmod(0o600)


def commit_fixture(root: Path, files: dict[str, str]) -> str:
    root.mkdir(exist_ok=True)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE).decode().strip()
    if not (root / '.git').exists():
        git('init', '-q')
    for name, text in files.items():
        target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    git('add', '--', *files)
    git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
        '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Synthetic candidate')
    return git('rev-parse', 'HEAD')


def test_candidate_missing_dependency_retry_and_inventory(tmp_path):
    repo = tmp_path / 'repo'; attempts = tmp_path / 'attempts'; attempts.mkdir()
    sha = commit_fixture(repo, {'tests/test_dependency.py':
        "from pathlib import Path\ndef test_dependency():\n    assert Path('control.md').read_text() == 'present'\n"})
    (repo / 'control.md').write_text('present')  # Must not mask missing Git bytes.
    assert candidate.run_candidate(repo, sha, ['tests/test_dependency.py'], Path(sys.executable), attempts, dict(os.environ)) != 0
    first = next(attempts.glob('*/result.json')); original = first.read_bytes()
    report = json.loads(original)
    assert report['missing_dependencies']
    assert 'control.md' not in report['inventory_before']
    sha2 = commit_fixture(repo, {'control.md': 'present'})
    assert candidate.run_candidate(repo, sha2, ['tests/test_dependency.py'], Path(sys.executable), attempts, dict(os.environ)) == 0
    assert first.read_bytes() == original
    reports = [json.loads(p.read_text()) for p in attempts.glob('*/result.json')]
    passing = next(r for r in reports if r['status'] == 'passed')
    assert passing['commit'] == sha2 and passing['tree']
    assert passing['inventory_before']['control.md'] == passing['inventory_after']['control.md']
    assert passing['supplemental_files'] == []


@pytest.mark.parametrize('path', ['../escape', '/absolute', 'a\\b', 'a:stream', '.git/config',
                                    'aux.txt', 'a/../b', 'a//b', 'a./b'])
def test_export_rejects_unsafe_paths(path):
    with pytest.raises(ValueError): candidate.safe_path(path)


@pytest.mark.parametrize('mode', ['120000', '160000'])
def test_export_rejects_linked_entries(tmp_path, monkeypatch, mode):
    def git(repo, *args):
        if args[0] == 'cat-file': return b'commit\n'
        if args[0] == 'rev-parse': return b'b' * 40
        return f'{mode} blob {"c" * 40}\tlink\0'.encode()
    monkeypatch.setattr(candidate, 'git', git)
    with pytest.raises(ValueError, match='unsupported'):
        candidate.export_commit(tmp_path, 'a' * 40, tmp_path / 'tree')
    assert not (tmp_path / 'tree').exists()


def test_candidate_imports_cannot_use_working_tree_pythonpath(tmp_path):
    repo = tmp_path / 'repo'; attempts = tmp_path / 'attempts'; attempts.mkdir()
    sha = commit_fixture(repo, {'tests/test_import.py': 'import only_local\ndef test_ok(): assert True\n'})
    (repo / 'only_local.py').write_text('present = True')
    env = dict(os.environ, PYTHONPATH=str(repo))
    assert candidate.run_candidate(repo, sha, ['tests/test_import.py'], Path(sys.executable), attempts, env) != 0
    report = json.loads(next(attempts.glob('*/result.json')).read_text())
    assert any('ModuleNotFoundError' in line for line in report['missing_dependencies'])


def test_candidate_changes_are_not_a_pass(tmp_path):
    repo = tmp_path / 'repo'; attempts = tmp_path / 'attempts'; attempts.mkdir()
    sha = commit_fixture(repo, {'control.md': 'before', 'tests/test_edit.py':
        "from pathlib import Path\ndef test_edit(): Path('control.md').write_text('after')\n"})
    assert candidate.run_candidate(repo, sha, ['tests/test_edit.py'], Path(sys.executable), attempts, dict(os.environ)) == 1
    report = json.loads(next(attempts.glob('*/result.json')).read_text())
    assert report['changed_candidate_files'] == ['control.md']
